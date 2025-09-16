//! PyO3-backed Word2Vec with Matryoshka multi-level representations.
//!
//! Exposes a thin Python module (`_core`) with two primary types:
//! - `Word2Vec`: training and model state (vocab, options, weights)
//! - `KeyedVectors`: query-only vectors with optional NumPy memmap backing
//!
//! Highlights
//! - Levels: operations can run on vector prefixes (e.g., d/4, d/2, d) to
//!   trade accuracy for speed without recomputing new vectors.
//! - Concurrency: training uses Rayon for data parallelism; shared weights are
//!   updated under striped locks to avoid a single global mutex; CPU work runs
//!   under `allow_threads` to avoid blocking the GIL.
//! - I/O: vectors persist as `{base}.vocab.json` + `{base}.npy`; `.npy` can be
//!   memory-mapped in Python for zero-copy queries.
#![allow(
    clippy::needless_range_loop,
    clippy::useless_conversion,
    clippy::manual_div_ceil,
    clippy::needless_borrow,
    clippy::too_many_arguments
)]
use ahash::AHashMap as HashMap;
use once_cell::sync::Lazy;
use pyo3::exceptions::{PyKeyboardInterrupt, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyIterator, PyModule, PyType};
use rand::{rngs::StdRng, Rng, SeedableRng};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
// removed local Huffman impl; no BinaryHeap/Reverse needed here
use std::cell::RefCell;
use std::fs;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::mpsc;
use std::sync::Arc;
use std::sync::Mutex;
use std::time::{Duration, Instant};

mod io;
mod ops;
mod sampling;
mod training;
mod weights;
mod kv;
mod logutil;
use io::npy::{npy_header_len, read_npy_shape, write_npy};
// cosine_prefix used only in earlier versions; current codepaths inline cosine
use weights::SharedWeights;
// Re-export KeyedVectors and logging helper from split modules
use kv::KeyedVectors;
use logutil::log_info_msg;

static BASE_SEED: AtomicU64 = AtomicU64::new(42);
static GLOBAL_RNG: Lazy<Mutex<StdRng>> =
    Lazy::new(|| Mutex::new(StdRng::seed_from_u64(BASE_SEED.load(Ordering::Relaxed))));
static RNG_COUNTER: AtomicU64 = AtomicU64::new(1);
// Versioning to re-seed per-thread RNGs when `set_seed` is called.
static SEED_EPOCH: AtomicU64 = AtomicU64::new(1);
thread_local! {
    static TLS_RNG: RefCell<(u64, Option<StdRng>)> = const { RefCell::new((0, None)) };
}

// SharedWeights moved to weights module

#[derive(Serialize, Deserialize, Clone, Default)]
struct KVSerde {
    vectors: HashMap<String, Vec<f32>>,
    vector_size: usize,
}


#[pyclass(module = "word2vec_matryoshka")]
/// Trainable Word2Vec model supporting Matryoshka levels.
struct Word2Vec {
    vector_size: usize,
    window: usize,
    _min_count: usize,
    max_final_vocab: Option<usize>,
    _workers: usize,
    negative: usize,
    sg: bool,
    hs: bool,
    cbow_mean: bool,
    levels: Vec<usize>,
    alpha: f32,
    min_alpha: f32,
    // number of iterations over the corpus when not specified at train time
    epochs: usize,
    log_verbose: bool,
    log_interval: f64,
    // vocab and matrices
    vocab: HashMap<String, usize>,
    ivocab: Vec<String>,
    counts: Vec<u64>,
    hs_codes: Vec<Vec<u8>>,     // per word
    hs_points: Vec<Vec<usize>>, // per word, internal node indices (>= vocab)
    alias_prob: Vec<f32>,
    alias_alias: Vec<usize>,
    w_in: Vec<f32>,  // shape: (vocab, dim)
    w_out: Vec<f32>, // shape: (nodes, dim): nodes=vocab for NS; nodes=2*vocab-1 for HS
}

#[pymethods]
impl Word2Vec {
    #[new]
    #[pyo3(signature = (sentences=None, vector_size=100, window=5, min_count=5, max_final_vocab=None, workers=1, negative=5, sg=0, hs=0, cbow_mean=1, levels=None, alpha=0.025, min_alpha=0.0001, epochs=5, verbose=true, progress_interval=1.0))]
    /// Construct a model; if `sentences` is provided, build vocab immediately.
    fn new(
        sentences: Option<Bound<'_, PyAny>>,
        vector_size: usize,
        window: usize,
        min_count: usize,
        max_final_vocab: Option<usize>,
        workers: usize,
        negative: usize,
        sg: i32,
        hs: i32,
        cbow_mean: i32,
        levels: Option<Vec<usize>>,
        alpha: f32,
        min_alpha: f32,
        epochs: usize,
        verbose: bool,
        progress_interval: f64,
    ) -> PyResult<Self> {
        if sg != 0 && sg != 1 {
            return Err(PyValueError::new_err(
                "sg must be 0 (CBOW) or 1 (skip-gram)",
            ));
        }
        let sg_flag = sg == 1;
        if hs != 0 && hs != 1 {
            return Err(PyValueError::new_err("hs must be 0 (off) or 1 (on)"));
        }
        let hs_flag = hs == 1;
        if cbow_mean != 0 && cbow_mean != 1 {
            return Err(PyValueError::new_err(
                "cbow_mean must be 0 (sum) or 1 (mean)",
            ));
        }
        let cbow_mean_flag = cbow_mean == 1;
        let mut lv = levels.unwrap_or_else(|| default_levels(vector_size));
        lv.retain(|&d| d >= 1 && d <= vector_size);
        if lv.is_empty() {
            lv.push(vector_size);
        }
        let mut model = Self {
            vector_size,
            window,
            _min_count: min_count,
            max_final_vocab,
            _workers: workers,
            negative,
            sg: sg_flag,
            hs: hs_flag,
            cbow_mean: cbow_mean_flag,
            levels: lv,
            alpha,
            min_alpha,
            epochs,
            log_verbose: verbose,
            log_interval: progress_interval,
            vocab: HashMap::default(),
            ivocab: Vec::new(),
            counts: Vec::new(),
            hs_codes: Vec::new(),
            hs_points: Vec::new(),
            alias_prob: Vec::new(),
            alias_alias: Vec::new(),
            w_in: Vec::new(),
            w_out: Vec::new(),
        };
        // If sentences are provided, automatically start training after initialization.
        if let Some(s) = sentences {
            // Use constructor defaults (`epochs`, logging settings) when not overridden.
            model.train(s, None, None, None, None, None)?;
        }
        Ok(model)
    }

    #[classmethod]
    fn load(_cls: &Bound<'_, PyType>, path: &str) -> PyResult<Self> {
        // Load from KeyedVectors files using base prefix
        let base = path;
        let vocab_path = format!("{}.vocab.json", base);
        let npy_path = format!("{}.npy", base);
        let vocab_text = fs::read_to_string(&vocab_path)
            .map_err(|e| PyValueError::new_err(format!("failed to read {}: {}", vocab_path, e)))?;
        let ivocab: Vec<String> = serde_json::from_str(&vocab_text)
            .map_err(|e| PyValueError::new_err(format!("failed to parse vocab json: {}", e)))?;
        let mut vocab: HashMap<String, usize> = HashMap::default();
        for (i, w) in ivocab.iter().enumerate() {
            vocab.insert(w.clone(), i);
        }
        let (_rows, dim) = read_npy_shape(&npy_path)?;
        // Read npy data into w_in
        let buf = fs::read(&npy_path)
            .map_err(|e| PyValueError::new_err(format!("failed to read {}: {}", npy_path, e)))?;
        let header_len = npy_header_len(&buf)?;
        let data_bytes = &buf[header_len..];
        let rows = ivocab.len();
        if data_bytes.len() != rows * dim * 4 {
            return Err(PyValueError::new_err("npy size mismatch"));
        }
        let mut w_in = vec![0f32; rows * dim];
        for i in 0..rows {
            let dst = &mut w_in[i * dim..(i + 1) * dim];
            let src = &data_bytes[i * dim * 4..(i + 1) * dim * 4];
            for j in 0..dim {
                let off = j * 4;
                dst[j] = f32::from_le_bytes(src[off..off + 4].try_into().unwrap());
            }
        }
        let w_out = vec![0.0f32; rows * dim];
        Ok(Self {
            vector_size: dim,
            window: 5,
            _min_count: 1,
            max_final_vocab: None,
            _workers: 1,
            negative: 5,
            sg: true,
            hs: false,
            cbow_mean: true,
            levels: default_levels(dim),
            alpha: 0.025,
            min_alpha: 0.0001,
            epochs: 5,
            log_verbose: true,
            log_interval: 1.0,
            vocab,
            ivocab,
            counts: Vec::new(),
            hs_codes: Vec::new(),
            hs_points: Vec::new(),
            alias_prob: Vec::new(),
            alias_alias: Vec::new(),
            w_in,
            w_out,
        })
    }

    fn save(&self, path: &str) -> PyResult<()> {
        // Save as KeyedVectors files preserving ivocab order
        let base = path;
        let vocab_path = format!("{}.vocab.json", base);
        let npy_path = format!("{}.npy", base);
        let vocab_tmp = format!("{}.tmp", &vocab_path);
        let npy_tmp = format!("{}.tmp", &npy_path);
        let vocab_json = serde_json::to_string(&self.ivocab)
            .map_err(|e| PyValueError::new_err(format!("failed to encode vocab: {}", e)))?;
        fs::write(&vocab_tmp, vocab_json)
            .map_err(|e| PyValueError::new_err(format!("failed to write {}: {}", vocab_tmp, e)))?;
        let rows = self.ivocab.len();
        let cols = self.vector_size;
        let mut flat: Vec<f32> = Vec::with_capacity(rows * cols);
        for i in 0..rows {
            let start = i * cols;
            flat.extend_from_slice(&self.w_in[start..start + cols]);
        }
        write_npy(&npy_tmp, rows, cols, &flat)?;
        fs::rename(&vocab_tmp, &vocab_path).map_err(|e| {
            PyValueError::new_err(format!("failed to finalize {}: {}", vocab_path, e))
        })?;
        fs::rename(&npy_tmp, &npy_path).map_err(|e| {
            PyValueError::new_err(format!("failed to finalize {}: {}", npy_path, e))
        })?;
        Ok(())
    }

    #[pyo3(signature = (corpus_iterable, total_examples=None, epochs=None, progress=None, verbose=None, progress_interval=None))]
    /// Train for one or more epochs. Consumes the Python iterator in short
    /// GIL windows and processes batches in parallel under `allow_threads`.
    fn train(
        &mut self,
        corpus_iterable: Bound<'_, PyAny>,
        total_examples: Option<usize>,
        epochs: Option<usize>,
        progress: Option<Bound<'_, PyAny>>,
        verbose: Option<bool>,
        progress_interval: Option<f64>,
    ) -> PyResult<()> {
        // Ensure vocab contains all tokens and matrices are initialized
        self.ingest_sentences(&corpus_iterable)?;
        // Prepare HS structures if enabled
        if self.hs && self.hs_points.is_empty() {
            if self.counts.is_empty() || self.counts.iter().all(|&c| c == 0) {
                self.counts = vec![1u64; self.ivocab.len()];
            }
            let (codes, points) = crate::training::hs::build_huffman(&self.counts);
            self.hs_codes = codes;
            self.hs_points = points;
            // ensure w_out has capacity for internal nodes
            let n = self.ivocab.len();
            let needed = (2 * n - 1) * self.vector_size;
            if self.w_out.len() < needed {
                let add = needed - self.w_out.len();
                let mut extra: Vec<f32> = Vec::with_capacity(add);
                let rows = (add + self.vector_size - 1) / self.vector_size;
                for _ in 0..rows {
                    extra.extend(random_unit(self.vector_size));
                }
                self.w_out.extend(extra);
            }
            // log HS ready
            if verbose.unwrap_or(self.log_verbose) {
                log_info_msg(&format!(
                    "TRAIN setup: built Huffman tree (vocab={}, nodes={})",
                    n,
                    2 * n - 1
                ));
            }
        }
        // Prepare alias sampler for NS
        if !self.hs && self.negative > 0 {
            if self.counts.is_empty() || self.counts.len() != self.ivocab.len() {
                self.counts = vec![1u64; self.ivocab.len()];
            }
            let mut weights: Vec<f64> =
                self.counts.iter().map(|&c| (c as f64).powf(0.75)).collect();
            let sum: f64 = weights.iter().sum();
            if sum > 0.0 {
                for w in &mut weights {
                    *w /= sum;
                }
            }
            let (prob, alias) = crate::sampling::alias::build_alias(&weights);
            self.alias_prob = prob;
            self.alias_alias = alias;
            if verbose.unwrap_or(self.log_verbose) {
                log_info_msg(&format!(
                    "TRAIN setup: built alias table for negative sampling (vocab={}, negatives={})",
                    self.ivocab.len(),
                    self.negative
                ));
            }
        }

        // Use provided epochs or fall back to the constructor's default.
        let epochs = epochs.unwrap_or(self.epochs);
        let lr0: f32 = self.alpha;
        let min_alpha = self.min_alpha;
        let neg = self.negative;
        let win = self.window;
        let _full_dim = self.vector_size;
        let vocab_len = self.ivocab.len();
        let levels_all = self.levels.clone();
        let sg_flag = self.sg;
        let hs_flag = self.hs;

        let use_parallel = self._workers > 1;
        let interrupt = Arc::new(AtomicBool::new(false));
        // Prepare sentences (read-only)
        let sents_idx = sentences_to_indices(&corpus_iterable, &self.vocab)?;
        // Keep an owned handle to the Python iterable for multi-epoch/branch reuse
        let sentences_owned = corpus_iterable.unbind();
        let total_per_epoch: usize = sents_idx.iter().map(|s| s.len()).sum();
        if verbose.unwrap_or(self.log_verbose) {
            let sg_num = if self.sg { 1 } else { 0 };
            let hs_num = if self.hs { 1 } else { 0 };
            // Render Option nicely without Rust's Some(...)
            let max_final_vocab_str = self
                .max_final_vocab
                .map(|v| v.to_string())
                .unwrap_or_else(|| "None".to_string());
            log_info_msg(&format!(
                "TRAIN setup: vocab={}, vector_size={}, window={}, min_count={}, max_final_vocab={}, workers={}, sg={}, hs={}, cbow_mean={}, negative={}, levels={:?}, alpha_start={:.5}, min_alpha={:.5}, log_interval={:.2}s",
                self.ivocab.len(),
                self.vector_size,
                self.window,
                self._min_count,
                max_final_vocab_str,
                self._workers,
                sg_num,
                hs_num,
                if self.cbow_mean { 1 } else { 0 },
                self.negative,
                self.levels,
                self.alpha,
                self.min_alpha,
                self.log_interval
            ));
            // Hardware / thread-pool info
            let cores = std::thread::available_parallelism()
                .map(|n| n.get())
                .unwrap_or(0);
            let rayon_threads = rayon::current_num_threads();
            log_info_msg(&format!(
                "TRAIN setup: hardware cores={}, rayon_threads={}, workers={}",
                cores, rayon_threads, self._workers
            ));
            // Environment info: PID, Python version, arch + SIMD
            let pid = std::process::id();
            let mut py_ver = String::from("unknown");
            Python::with_gil(|py| {
                if let Ok(sys) = PyModule::import_bound(py, "sys") {
                    if let Ok(v) = sys.getattr("version") {
                        if let Ok(s) = v.extract::<String>() {
                            py_ver = s.split_whitespace().next().unwrap_or(&s).to_string();
                        }
                    }
                }
            });
            let arch = if cfg!(target_arch = "x86_64") {
                "x86_64"
            } else if cfg!(target_arch = "aarch64") {
                "aarch64"
            } else {
                "unknown"
            };
            let simd_feature = if cfg!(feature = "simd") {
                "enabled"
            } else {
                "disabled"
            };
            let simd_runtime = {
                #[cfg(target_arch = "x86_64")]
                unsafe {
                    let avx = std::arch::is_x86_feature_detected!("avx");
                    let fma = std::arch::is_x86_feature_detected!("fma");
                    let sse2 = std::arch::is_x86_feature_detected!("sse2");
                    format!("avx={}, fma={}, sse2={}", avx, fma, sse2)
                }
                #[cfg(target_arch = "aarch64")]
                {
                    String::from("neon=true")
                }
                #[cfg(not(any(target_arch = "x86_64", target_arch = "aarch64")))]
                {
                    String::from("n/a")
                }
            };
            log_info_msg(&format!(
                "TRAIN setup: env pid={}, py={}, arch={}, simd_feature={}, simd_runtime={}",
                pid, py_ver, arch, simd_feature, simd_runtime
            ));
            log_info_msg(&format!(
                "TRAIN setup: total_tokens_per_epoch={}, epochs={}",
                total_per_epoch, epochs
            ));
        }
        let _ = total_examples; // reserved for future

        // Prepare shared weights for parallel path
        let mut w_in_sw_main: Option<SharedWeights> = None;
        let mut w_out_sw_main: Option<SharedWeights> = None;
        if use_parallel {
            w_in_sw_main = Some(SharedWeights::new(
                std::mem::take(&mut self.w_in),
                self.vector_size,
            ));
            w_out_sw_main = Some(SharedWeights::new(
                std::mem::take(&mut self.w_out),
                self.vector_size,
            ));
        }
        for e in 0..epochs {
            // Before starting a new epoch, honor any pending KeyboardInterrupt
            Python::with_gil(|py| -> PyResult<()> { py.check_signals()?; Ok(()) })?;
            if interrupt.load(Ordering::Relaxed) {
                return Err(PyKeyboardInterrupt::new_err("training interrupted"));
            }
            let epoch_start = Instant::now();
            let frac = (e as f32) / (epochs as f32);
            let mut lr = lr0 - (lr0 - min_alpha) * frac;
            if lr < min_alpha {
                lr = min_alpha;
            }
            let verbose_flag = verbose.unwrap_or(self.log_verbose);
            let interval_secs = progress_interval.unwrap_or(self.log_interval);
            let want_progress = verbose_flag || progress.is_some();
            if verbose_flag {
                let sg_num = if sg_flag { 1 } else { 0 };
                let hs_num = if hs_flag { 1 } else { 0 };
                let max_final_vocab_str = self
                    .max_final_vocab
                    .map(|v| v.to_string())
                    .unwrap_or_else(|| "None".to_string());
                log_info_msg(&format!(
                    "EPOCH {}/{}: start, target_tokens={}, vector_size={}, window={}, min_count={}, max_final_vocab={}, lr_start={:.5}, min_alpha={:.5}, interval={:.2}s, sg={}, hs={}, cbow_mean={}, negatives={}, levels={:?}, workers={}",
                    e + 1,
                    epochs,
                    total_per_epoch,
                    self.vector_size,
                    win,
                    self._min_count,
                    max_final_vocab_str,
                    lr,
                    min_alpha,
                    interval_secs,
                    sg_num,
                    hs_num,
                    if self.cbow_mean { 1 } else { 0 },
                    neg,
                    levels_all,
                    self._workers
                ));
            }
            // Emit an initial 0.00% line at epoch start when logging
            if want_progress && verbose_flag {
                let frac0 = 0.0f64;
                let alpha0 = lr; // per-epoch starting lr
                let msg = format!(
                    "EPOCH {}/{}: PROGRESS at {:.2}% tokens, alpha {:.5}, {} tokens/s",
                    e + 1,
                    epochs,
                    frac0 * 100.0,
                    alpha0,
                    0u64
                );
                log_info_msg(&msg);
            }
            if use_parallel {
                // Parallel path with striped locks
                let (processed_opt, stop_flag_opt, reporter_opt) = if want_progress {
                    let processed = Arc::new(AtomicU64::new(0));
                    let stop_flag = Arc::new(AtomicBool::new(false));
                    let total_all = (total_per_epoch as u64) * (epochs as u64);
                    let base_done = (e as u64) * (total_per_epoch as u64);
                    let total_epoch = total_per_epoch as u64;
                    let interval =
                        Duration::from_millis(((interval_secs.max(0.01)) * 1000.0) as u64);
                    let progress_cb: Option<Py<PyAny>> =
                        progress.as_ref().map(|p| p.clone().unbind());
                    let processed_rep = processed.clone();
                    let stop_rep = stop_flag.clone();
                    let interrupt_rep = interrupt.clone();
                    let progress_rep = progress_cb;
                    let verbose_rep = verbose_flag;
                    let lr0_rep = lr0;
                    let min_alpha_rep = min_alpha;
                    let epoch_idx = e + 1;
                    let epochs_total = epochs;
                    let reporter = std::thread::spawn(move || {
                        let t0 = Instant::now();
                        let tick = std::cmp::min(interval, Duration::from_millis(50));
                        let mut acc = Duration::from_millis(0);
                        loop {
                            if stop_rep.load(Ordering::Relaxed) || interrupt_rep.load(Ordering::Relaxed) {
                                break;
                            }
                            std::thread::sleep(tick);
                            acc += tick;
                            // also honor KeyboardInterrupt promptly from the reporter thread
                            Python::with_gil(|py| {
                                if py.check_signals().is_err() {
                                    interrupt_rep.store(true, Ordering::Relaxed);
                                }
                            });
                            if acc >= interval {
                                acc = Duration::from_millis(0);
                                let now = Instant::now();
                                let processed_epoch = processed_rep.load(Ordering::Relaxed);
                                let done = base_done + processed_epoch;
                                if verbose_rep {
                                    // Per-epoch fraction 0..1
                                    let frac = if total_epoch > 0 {
                                        (processed_epoch as f64) / (total_epoch as f64)
                                    } else {
                                        0.0
                                    };
                                    let elapsed = now.duration_since(t0).as_secs_f64();
                                    let rate = if elapsed > 0.0 {
                                        (processed_epoch as f64) / elapsed
                                    } else {
                                        0.0
                                    };
                                    let mut alpha = lr0_rep
                                        - (lr0_rep - min_alpha_rep) * (done as f32)
                                            / (total_all as f32);
                                    if alpha < min_alpha_rep {
                                        alpha = min_alpha_rep;
                                    }
                                    let msg = format!(
                                        "EPOCH {}/{}: PROGRESS at {:.2}% tokens, alpha {:.5}, {} tokens/s",
                                        epoch_idx,
                                        epochs_total,
                                        frac * 100.0,
                                        alpha,
                                        rate.round() as u64
                                    );
                                    log_info_msg(&msg);
                                }
                                if let Some(cb) = &progress_rep {
                                    Python::with_gil(|py| {
                                        let bound = cb.bind(py);
                                        let _ = bound.call1((done, total_all));
                                    });
                                }
                            }
                        }
                    });
                    (Some(processed), Some(stop_flag), Some(reporter))
                } else {
                    (
                        None::<Arc<AtomicU64>>,
                        None::<Arc<AtomicBool>>,
                        None::<std::thread::JoinHandle<()>>,
                    )
                };
                let w_in_sw = w_in_sw_main.as_ref().unwrap().clone();
                let w_out_sw = w_out_sw_main.as_ref().unwrap().clone();
                let hs_codes = Arc::new(self.hs_codes.clone());
                let hs_points = Arc::new(self.hs_points.clone());
                let alias_prob = Arc::new(self.alias_prob.clone());
                let alias_alias = Arc::new(self.alias_alias.clone());
                let levels_ep = levels_all.clone();
                // Chunked prefetch queue: producer reads Python iterable, consumers process chunks in parallel
                // Larger bounded queue to reduce producer/consumer stalls
                let queue_cap = (self._workers.max(1) * 8).min(128);
                let (tx, rx_inner) = mpsc::sync_channel::<Vec<Vec<usize>>>(queue_cap);
                let rx = Arc::new(Mutex::new(rx_inner));
                // Clone a new Py<PyAny> handle for the producer thread
                let sentences_obj = Python::with_gil(|py| sentences_owned.clone_ref(py));
                let vocab = self.vocab.clone();
                let processed_arc = processed_opt.clone();
                std::thread::spawn(move || {
                    // Larger batch size amortizes GIL and channel overhead
                    let chunk_cap: usize = std::env::var("W2V_CHUNK")
                        .ok()
                        .and_then(|s| s.parse().ok())
                        .unwrap_or(8192);
                    // Create a persistent Python iterator handle, then pull items in short GIL windows
                    let iter_handle: Option<Py<PyAny>> = Python::with_gil(|py| {
                        let bound = sentences_obj.bind(py);
                        match bound.call_method0("__iter__") {
                            Ok(it) => Some(it.unbind()),
                            Err(_) => None,
                        }
                    });
                    if let Some(iter_obj) = iter_handle {
                        let mut chunk: Vec<Vec<usize>> = Vec::with_capacity(chunk_cap);
                        loop {
                            let mut ended = false;
                            // Pull up to CHUNK items under the GIL, then release to let other threads (e.g., logger) run
                            Python::with_gil(|py| {
                                let it = iter_obj.bind(py);
                                for _ in 0..chunk_cap {
                                    match it.call_method0("__next__") {
                                        Ok(item) => {
                                            if let Ok(seq) = item.extract::<Vec<String>>() {
                                                let mut s = Vec::with_capacity(seq.len());
                                                for tok in seq {
                                                    if let Some(&ix) = vocab.get(&tok) {
                                                        s.push(ix);
                                                    }
                                                }
                                                if !s.is_empty() {
                                                    chunk.push(s);
                                                }
                                            }
                                        }
                                        Err(_) => {
                                            ended = true;
                                            break;
                                        }
                                    }
                                }
                            });
                            if !chunk.is_empty() {
                                let _ = tx.send(std::mem::take(&mut chunk));
                            }
                            if ended {
                                break;
                            }
                        }
                    }
                });
                let run_res: PyResult<()> = Python::with_gil(|py| -> PyResult<()> {
                    let total_epoch_u64 = total_per_epoch as u64;
                    use std::sync::mpsc::RecvTimeoutError;
                    loop {
                        // Fast-exit if we've already processed the full epoch
                        if let Some(proc) = &processed_opt {
                            if proc.load(Ordering::Relaxed) >= total_epoch_u64 {
                                break;
                            }
                        }
                        // Receive one chunk without holding the GIL; timeout to allow liveness checks
                        let rx_clone = rx.clone();
                        let recv_res = py.allow_threads(|| {
                            rx_clone
                                .lock()
                                .unwrap()
                                .recv_timeout(Duration::from_millis(200))
                        });
                        let chunk = match recv_res {
                            Ok(c) => c,
                            Err(RecvTimeoutError::Disconnected) => break,
                            Err(RecvTimeoutError::Timeout) => {
                                if let Some(proc) = &processed_opt {
                                    if proc.load(Ordering::Relaxed) >= total_epoch_u64 {
                                        break;
                                    }
                                }
                                continue;
                            }
                        };
                        // Process this chunk without holding the GIL
                        py.allow_threads(|| {
                            chunk.par_iter().for_each(|sent| {
                                // Use TLS RNG; borrow mutably for the scope of this sentence
                                TLS_RNG.with(|cell| {
                                    let mut state = cell.borrow_mut();
                                    let epoch_now = SEED_EPOCH.load(Ordering::Relaxed);
                                    if state.0 != epoch_now || state.1.is_none() {
                                        let base = BASE_SEED.load(Ordering::Relaxed);
                                        let tid_hash = {
                                            use std::hash::{Hash, Hasher};
                                            let mut h = std::collections::hash_map::DefaultHasher::new();
                                            std::thread::current().id().hash(&mut h);
                                            h.finish()
                                        };
                                        let mixed = base ^ tid_hash;
                                        state.1 = Some(StdRng::seed_from_u64(mixed));
                                        state.0 = epoch_now;
                                    }
                                    let rng = state.1.as_mut().unwrap();
                                    // Now do the work with rng
                                    for (i, &center) in sent.iter().enumerate() {
                                        let b = rng.gen_range(0..=win);
                                        let start = i.saturating_sub(win - b);
                                        let end = (i + win - b + 1).min(sent.len());
                                        if sg_flag {
                                            for j in start..end {
                                                if j == i { continue; }
                                                let context = sent[j];
                                                if hs_flag {
                                                    for &ldim in &levels_ep {
                                                        crate::training::hs::hs_update_striped(
                                                            &w_in_sw,
                                                            &w_out_sw,
                                                            center,
                                                            &hs_codes[context],
                                                            &hs_points[context],
                                                            lr / (levels_ep.len() as f32),
                                                            ldim,
                                                        );
                                                    }
                                                } else if !alias_prob.is_empty() {
                                                    crate::training::ns::sgns_update_levels_alias_striped_batched(
                                                        &w_in_sw,
                                                        &w_out_sw,
                                                        center,
                                                        context,
                                                        neg,
                                                        lr,
                                                        &levels_ep,
                                                        self.vector_size,
                                                        &alias_prob,
                                                        &alias_alias,
                                                        rng,
                                                    );
                                                } else {
                                                    crate::training::ns::sgns_update_levels_striped_batched(
                                                        &w_in_sw,
                                                        &w_out_sw,
                                                        center,
                                                        context,
                                                        neg,
                                                        lr,
                                                        &levels_ep,
                                                        self.vector_size,
                                                        vocab_len,
                                                        rng,
                                                    );
                                                }
                                            }
                                        } else {
                                            let mut ctx_indices: Vec<usize> = Vec::new();
                                            for j in start..end { if j != i { ctx_indices.push(sent[j]); } }
                                            if !ctx_indices.is_empty() {
                                                if hs_flag {
                                                    for &ldim in &levels_ep {
                                                        crate::training::hs::hs_update_cbow_striped(
                                                            &w_in_sw,
                                                            &w_out_sw,
                                                            &ctx_indices,
                                                            &hs_codes[center],
                                                            &hs_points[center],
                                                            lr / (levels_ep.len() as f32),
                                                            ldim,
                                                            self.cbow_mean,
                                                        );
                                                    }
                                                } else {
                                                    for &ldim in &levels_ep {
                                                        if !alias_prob.is_empty() {
                                                            crate::training::ns::sgns_update_cbow_alias_striped(
                                                                &w_in_sw,
                                                                &w_out_sw,
                                                                &ctx_indices,
                                                                center,
                                                                neg,
                                                                lr / (levels_ep.len() as f32),
                                                                ldim,
                                                                &alias_prob,
                                                                &alias_alias,
                                                                rng,
                                                                self.cbow_mean,
                                                            );
                                                        } else {
                                                            crate::training::ns::sgns_update_cbow_striped(
                                                                &w_in_sw,
                                                                &w_out_sw,
                                                                &ctx_indices,
                                                                center,
                                                                neg,
                                                                lr / (levels_ep.len() as f32),
                                                                ldim,
                                                                vocab_len,
                                                                rng,
                                                                self.cbow_mean,
                                                            );
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    if let Some(ref proc) = processed_arc {
                                        proc.fetch_add(sent.len() as u64, Ordering::Relaxed);
                                    }
                                });
                            });
                        });
                        // Propagate KeyboardInterrupt after each chunk and set shared flag
                        if let Err(e) = py.check_signals() {
                            interrupt.store(true, Ordering::Relaxed);
                            return Err(e);
                        }
                    }
                    Ok(())
                });
                // Signal the reporter to stop and drain any remaining updates
                if let Some(flag) = &stop_flag_opt {
                    flag.store(true, Ordering::Relaxed);
                }
                if let Some(rep) = reporter_opt {
                    let _ = rep.join();
                }
                // Propagate any interrupt after cleaning up background threads
                if let Err(e) = run_res {
                    return Err(e);
                }
                // Catch any pending signals which may have arrived between the last
                // chunk and loop exit (e.g., right at epoch boundary)
                if let Err(e) = Python::with_gil(|py| -> PyResult<()> { py.check_signals()?; Ok(()) }) {
                    interrupt.store(true, Ordering::Relaxed);
                    return Err(e);
                }
                if interrupt.load(Ordering::Relaxed) {
                    return Err(PyKeyboardInterrupt::new_err("training interrupted"));
                }
                // Epoch end summary for parallel path (after reporter stops)
                if verbose_flag && !interrupt.load(Ordering::Relaxed) {
                    let tokens_epoch: u64 = processed_opt
                        .as_ref()
                        .map(|p| p.load(Ordering::Relaxed))
                        .unwrap_or(0);
                    let elapsed = epoch_start.elapsed().as_secs_f64();
                    let wps = if elapsed > 0.0 {
                        (tokens_epoch as f64 / elapsed).round() as u64
                    } else {
                        0
                    };
                    let total_all = (total_per_epoch as u64) * (epochs as u64);
                    let base_done = (e as u64) * (total_per_epoch as u64);
                    let done = base_done + tokens_epoch;
                    let mut alpha_end =
                        lr0 - (lr0 - min_alpha) * (done as f32) / (total_all as f32);
                    if alpha_end < min_alpha {
                        alpha_end = min_alpha;
                    }
                    log_info_msg(&format!(
                        "EPOCH {}/{}: end, elapsed={:.2}s, tokens={}, tokens/s={}, lr_end={:.5}",
                        e + 1,
                        epochs,
                        elapsed,
                        tokens_epoch,
                        wps,
                        alpha_end
                    ));
                }
            } else {
                // Sequential deterministic streaming path
                let progress_cb: Option<Py<PyAny>> = progress.as_ref().map(|p| p.clone().unbind());
                Python::with_gil(|py| -> PyResult<()> {
                    let mut rng = StdRng::seed_from_u64(
                        BASE_SEED.load(Ordering::Relaxed).wrapping_add(e as u64),
                    );
                    let bound = sentences_owned.bind(py);
                    let it = PyIterator::from_bound_object(&bound)?;
                    let mut processed_epoch: u64 = 0;
                    let total_all = (total_per_epoch as u64) * (epochs as u64);
                    let base_done = (e as u64) * (total_per_epoch as u64);
                    let interval = interval_secs.max(0.01);
                    let mut last = Instant::now();
                    let t0 = last;
                    for item in it {
                        let seq: Vec<String> = item?.extract()?;
                        let mut sent_idx: Vec<usize> = Vec::with_capacity(seq.len());
                        for tok in seq {
                            if let Some(&ix) = self.vocab.get(&tok) {
                                sent_idx.push(ix);
                            }
                        }
                        if sent_idx.is_empty() {
                            continue;
                        }
                        // compute step moved below under py.allow_threads
                        if want_progress {
                            // Training compute without the GIL; count processed centers
                            let tokens_done = py.allow_threads(|| {
                                let mut processed = 0u64;
                                // Reuse a single context buffer across centers
                                let mut ctx_indices: Vec<usize> = Vec::with_capacity(2 * win + 1);
                                for (i, &center) in sent_idx.iter().enumerate() {
                                    let b = rng.gen_range(0..=win);
                                    let start = i.saturating_sub(win - b);
                                    let end = (i + win - b + 1).min(sent_idx.len());
                                    if sg_flag {
                                        for j in start..end {
                                            if j == i { continue; }
                                            let context = sent_idx[j];
                                            if hs_flag {
                                                for &ldim in &levels_all {
                                                    crate::training::hs::hs_update(
                                                        &mut self.w_in,
                                                        &mut self.w_out,
                                                        center,
                                                        &self.hs_codes[context],
                                                        &self.hs_points[context],
                                                        lr / (levels_all.len() as f32),
                                                        ldim,
                                                    );
                                                }
                                            } else if !self.alias_prob.is_empty() {
                                                crate::training::ns::sgns_update_levels_alias(
                                                    &mut self.w_in,
                                                    &mut self.w_out,
                                                    center,
                                                    context,
                                                    neg,
                                                    lr,
                                                    &levels_all,
                                                    self.vector_size,
                                                    &self.alias_prob,
                                                    &self.alias_alias,
                                                    &mut rng,
                                                );
                                            } else {
                                                crate::training::ns::sgns_update_levels(
                                                    &mut self.w_in,
                                                    &mut self.w_out,
                                                    center,
                                                    context,
                                                    neg,
                                                    lr,
                                                    &levels_all,
                                                    self.vector_size,
                                                    vocab_len,
                                                    &mut rng,
                                                );
                                            }
                                        }
                                    } else {
                                        ctx_indices.clear();
                                        for j in start..end { if j != i { ctx_indices.push(sent_idx[j]); } }
                                        if !ctx_indices.is_empty() {
                                            if hs_flag {
                                                for &ldim in &levels_all {
                                                    crate::training::hs::hs_update_cbow(
                                                        &mut self.w_in,
                                                        &mut self.w_out,
                                                        &ctx_indices,
                                                        &self.hs_codes[center],
                                                        &self.hs_points[center],
                                                        lr / (levels_all.len() as f32),
                                                        ldim,
                                                        self.cbow_mean,
                                                    );
                                                }
                                            } else {
                                                for &ldim in &levels_all {
                                                    if !self.alias_prob.is_empty() {
                                                        crate::training::ns::sgns_update_cbow_alias(
                                                            &mut self.w_in,
                                                            &mut self.w_out,
                                                            &ctx_indices,
                                                            center,
                                                            neg,
                                                            lr / (levels_all.len() as f32),
                                                            ldim,
                                                            &self.alias_prob,
                                                            &self.alias_alias,
                                                            &mut rng,
                                                            self.cbow_mean,
                                                        );
                                                    } else {
                                                        crate::training::ns::sgns_update_cbow(
                                                            &mut self.w_in,
                                                            &mut self.w_out,
                                                            &ctx_indices,
                                                            center,
                                                            neg,
                                                            lr / (levels_all.len() as f32),
                                                            ldim,
                                                            vocab_len,
                                                            &mut rng,
                                                            self.cbow_mean,
                                                        );
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    processed += 1;
                                }
                                processed
                            });
                            processed_epoch += tokens_done;
                            let now = Instant::now();
                            if now.duration_since(last).as_secs_f64() >= interval {
                                last = now;
                                let done = base_done + processed_epoch;
                                if verbose_flag {
                                    let frac = if total_all > 0 { (done as f64) / (total_all as f64) } else { 0.0 };
                                    let elapsed = now.duration_since(t0).as_secs_f64();
                                    let rate = if elapsed > 0.0 { (done as f64) / elapsed } else { 0.0 };
                                    let mut alpha = lr0 - (lr0 - min_alpha) * (done as f32) / (total_all as f32);
                                    if alpha < min_alpha { alpha = min_alpha; }
                                    let msg = format!(
                                        "EPOCH {}/{}: PROGRESS at {:.2}% tokens, alpha {:.5}, {} tokens/s",
                                        e + 1, epochs, frac * 100.0, alpha, rate.round() as u64
                                    );
                                    log_info_msg(&msg);
                                }
                                if let Some(cb) = &progress_cb {
                                    let bound = cb.bind(py);
                                    let _ = bound.call1((done, total_all));
                                }
                            }
                            // Propagate KeyboardInterrupt promptly and set shared flag
                            if let Err(e) = py.check_signals() {
                                interrupt.store(true, Ordering::Relaxed);
                                return Err(e);
                            }
                        } else {
                            // No progress requested: still compute without the GIL
                            let _ = py.allow_threads(|| {
                                // Reuse a single context buffer across centers
                                let mut ctx_indices: Vec<usize> = Vec::with_capacity(2 * win + 1);
                                for (i, &center) in sent_idx.iter().enumerate() {
                                    let b = rng.gen_range(0..=win);
                                    let start = i.saturating_sub(win - b);
                                    let end = (i + win - b + 1).min(sent_idx.len());
                                    if sg_flag {
                                        for j in start..end {
                                            if j == i { continue; }
                                            let context = sent_idx[j];
                                            if hs_flag {
                                                for &ldim in &levels_all {
                                                    crate::training::hs::hs_update(
                                                        &mut self.w_in, &mut self.w_out, center,
                                                        &self.hs_codes[context], &self.hs_points[context],
                                                        lr / (levels_all.len() as f32), ldim,
                                                    );
                                                }
                                            } else if !self.alias_prob.is_empty() {
                                                crate::training::ns::sgns_update_levels_alias(
                                                    &mut self.w_in, &mut self.w_out, center, context,
                                                    neg, lr, &levels_all, self.vector_size,
                                                    &self.alias_prob, &self.alias_alias, &mut rng,
                                                );
                                            } else {
                                                crate::training::ns::sgns_update_levels(
                                                    &mut self.w_in, &mut self.w_out, center, context,
                                                    neg, lr, &levels_all, self.vector_size, vocab_len, &mut rng,
                                                );
                                            }
                                        }
                                    } else {
                                        ctx_indices.clear();
                                        for j in start..end { if j != i { ctx_indices.push(sent_idx[j]); } }
                                        if !ctx_indices.is_empty() {
                                            if hs_flag {
                                                for &ldim in &levels_all {
                                                    crate::training::hs::hs_update_cbow(
                                                        &mut self.w_in, &mut self.w_out, &ctx_indices, &self.hs_codes[center],
                                                        &self.hs_points[center], lr / (levels_all.len() as f32), ldim, self.cbow_mean,
                                                    );
                                                }
                                            } else {
                                                for &ldim in &levels_all {
                                                    if !self.alias_prob.is_empty() {
                                                        crate::training::ns::sgns_update_cbow_alias(
                                                            &mut self.w_in, &mut self.w_out, &ctx_indices, center, neg,
                                                            lr / (levels_all.len() as f32), ldim,
                                                            &self.alias_prob, &self.alias_alias, &mut rng, self.cbow_mean,
                                                        );
                                                    } else {
                                                        crate::training::ns::sgns_update_cbow(
                                                            &mut self.w_in, &mut self.w_out, &ctx_indices, center, neg,
                                                            lr / (levels_all.len() as f32), ldim, vocab_len, &mut rng, self.cbow_mean,
                                                        );
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                            processed_epoch += sent_idx.len() as u64;
                            // Propagate KeyboardInterrupt promptly and set shared flag
                            if let Err(e) = py.check_signals() {
                                interrupt.store(true, Ordering::Relaxed);
                                return Err(e);
                            }
                        }
                    }
                    if want_progress && verbose_flag {
                        // Final flush (per-epoch)
                        let now = Instant::now();
                        let frac = if total_per_epoch > 0 {
                            (processed_epoch as f64) / (total_per_epoch as f64)
                        } else {
                            0.0
                        };
                        let elapsed = now.duration_since(t0).as_secs_f64();
                        let rate = if elapsed > 0.0 {
                            (processed_epoch as f64) / elapsed
                        } else {
                            0.0
                        };
                        let done = base_done + processed_epoch;
                        let mut alpha =
                            lr0 - (lr0 - min_alpha) * (done as f32) / (total_all as f32);
                        if alpha < min_alpha {
                            alpha = min_alpha;
                        }
                        let msg = format!(
                            "EPOCH {}/{}: PROGRESS at {:.2}% tokens, alpha {:.5}, {} tokens/s",
                            e + 1,
                            epochs,
                            frac * 100.0,
                            alpha,
                            rate.round() as u64
                        );
                        log_info_msg(&msg);
                    }
                    Ok(())
                })?;
                // Catch any pending signals at epoch end before continuing
                if let Err(e) = Python::with_gil(|py| -> PyResult<()> { py.check_signals()?; Ok(()) }) {
                    interrupt.store(true, Ordering::Relaxed);
                    return Err(e);
                }
                if interrupt.load(Ordering::Relaxed) {
                    return Err(PyKeyboardInterrupt::new_err("training interrupted"));
                }
            }
        }
        // Move weights back for parallel path
        if use_parallel {
            self.w_in = w_in_sw_main.take().unwrap().into_vec();
            self.w_out = w_out_sw_main.take().unwrap().into_vec();
        }
        Ok(())
    }

    #[getter]
    fn wv<'py>(&self, py: Python<'py>) -> PyResult<Py<KeyedVectors>> {
        // Build the KeyedVectors payload without holding the GIL
        let (map, vocab, index) = py.allow_threads(|| {
            let mut map = HashMap::default();
            let mut vocab = Vec::with_capacity(self.ivocab.len());
            let mut index = HashMap::default();
            for (idx, w) in self.ivocab.iter().enumerate() {
                vocab.push(w.clone());
                index.insert(w.clone(), idx);
                map.insert(w.clone(), self.get_in_vec(idx).to_vec());
            }
            (map, vocab, index)
        });
        let kv = KeyedVectors {
            vectors: Some(map),
            vector_size: self.vector_size,
            vocab,
            index,
            npy_path: None,
            memmap: None,
        };
        Py::new(py, kv)
    }

    #[getter]
    fn vector_size(&self) -> PyResult<usize> {
        Ok(self.vector_size)
    }
}

#[pymodule]
fn _core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Word2Vec>()?;
    m.add_class::<KeyedVectors>()?;
    m.add_function(wrap_pyfunction!(set_seed, m)?)?;
    Ok(())
}

impl Word2Vec {
    /// Build or update vocabulary and initialize weights if needed.
    fn ingest_sentences(&mut self, sentences: &Bound<'_, PyAny>) -> PyResult<()> {
        // If vocab is not yet built, count all tokens first, then build vocab
        if self.ivocab.is_empty() {
            let mut counts_map: HashMap<String, u64> = HashMap::default();
            let it = PyIterator::from_bound_object(sentences)?;
            for item in it {
                let seq: Vec<String> = item?.extract()?;
                for token in seq.iter() {
                    let e = counts_map.entry(token.clone()).or_insert(0);
                    *e += 1;
                }
            }

            // Determine automatic min_count from max_final_vocab, if requested
            let mut auto_min_count: usize = 1;
            if let Some(maxv) = self.max_final_vocab {
                if maxv > 0 {
                    let mut freqs: Vec<u64> = counts_map.values().cloned().collect();
                    freqs.sort_unstable_by(|a, b| b.cmp(a)); // desc
                    if freqs.len() > maxv {
                        let mut thr = freqs[maxv - 1].max(1);
                        // increase thr if ties cause > maxv kept
                        loop {
                            let keep = freqs.iter().filter(|&&c| c >= thr).count();
                            if keep <= maxv {
                                break;
                            }
                            thr += 1;
                        }
                        auto_min_count = thr as usize;
                    }
                }
            }
            let final_min_count = self._min_count.max(auto_min_count);

            // Filter and sort words deterministically: by count desc, then key asc
            let mut items: Vec<(String, u64)> = counts_map
                .into_iter()
                .filter(|(_, c)| *c >= final_min_count as u64)
                .collect();
            items.sort_unstable_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));

            // Build vocab, counts, and initialize weights
            self.ivocab = items.iter().map(|(w, _)| w.clone()).collect();
            self.vocab.clear();
            self.vocab.reserve(self.ivocab.len());
            for (i, w) in self.ivocab.iter().enumerate() {
                self.vocab.insert(w.clone(), i);
            }
            self.counts = items.iter().map(|(_, c)| *c).collect();

            self.w_in.clear();
            self.w_out.clear();
            for _ in 0..self.ivocab.len() {
                self.w_in.extend(random_unit(self.vector_size));
                self.w_out.extend(random_unit(self.vector_size));
            }
        } else {
            // Vocab already built: only update counts for known tokens; ignore unknowns
            let it = PyIterator::from_bound_object(sentences)?;
            for item in it {
                let seq: Vec<String> = item?.extract()?;
                for token in seq.iter() {
                    if let Some(&idx) = self.vocab.get(token) {
                        if self.counts.len() <= idx {
                            self.counts.resize(idx + 1, 0);
                        }
                        self.counts[idx] += 1;
                    }
                }
            }
        }
        Ok(())
    }

    #[allow(dead_code)]
    fn ensure_word(&mut self, w: &str) -> usize {
        if !self.vocab.contains_key(w) {
            let idx = self.ivocab.len();
            self.vocab.insert(w.to_string(), idx);
            self.ivocab.push(w.to_string());
            // grow matrices
            self.w_in.extend(random_unit(self.vector_size));
            self.w_out.extend(random_unit(self.vector_size));
            self.counts.push(0);
            idx
        } else {
            *self.vocab.get(w).unwrap()
        }
    }

    fn get_in_vec(&self, idx: usize) -> &[f32] {
        let start = idx * self.vector_size;
        &self.w_in[start..start + self.vector_size]
    }

    #[allow(dead_code)]
    fn get_in_vec_mut(&mut self, idx: usize) -> &mut [f32] {
        let start = idx * self.vector_size;
        &mut self.w_in[start..start + self.vector_size]
    }

    #[allow(dead_code)]
    fn get_out_vec_mut(&mut self, idx: usize) -> &mut [f32] {
        let start = idx * self.vector_size;
        &mut self.w_out[start..start + self.vector_size]
    }
}

fn random_unit(dim: usize) -> Vec<f32> {
    let mut rng = GLOBAL_RNG.lock().unwrap();
    let mut v: Vec<f32> = (0..dim).map(|_| rng.gen::<f32>()).collect();
    // normalize
    let norm: f32 = v.iter().map(|x| x * x).sum::<f32>().sqrt();
    if norm > 0.0 {
        for x in &mut v {
            *x /= norm;
        }
    }
    v
}

// Math kernels and TLS buffers moved to ops module

// removed legacy alias sampling and cbow helpers now provided by modules

fn sentences_to_indices(
    sentences: &Bound<'_, PyAny>,
    vocab: &HashMap<String, usize>,
) -> PyResult<Vec<Vec<usize>>> {
    let it = PyIterator::from_bound_object(sentences)?;
    let mut out: Vec<Vec<usize>> = Vec::new();
    for item in it {
        let seq: Vec<String> = item?.extract()?;
        let mut s: Vec<usize> = Vec::new();
        for token in seq.into_iter() {
            if let Some(&ix) = vocab.get(&token) {
                s.push(ix);
            }
        }
        if !s.is_empty() {
            out.push(s);
        }
    }
    Ok(out)
}

fn default_levels(dim: usize) -> Vec<usize> {
    let mut lv = vec![dim / 4, dim / 2, dim];
    lv.retain(|&d| d >= 1);
    lv.sort_unstable();
    lv.dedup();
    if lv.is_empty() {
        lv.push(dim.max(1));
    }
    lv
}

#[pyfunction]
fn set_seed(seed: u64) -> PyResult<()> {
    BASE_SEED.store(seed, Ordering::Relaxed);
    // Reseed global RNG and reset counter
    if let Ok(mut rng) = GLOBAL_RNG.lock() {
        *rng = StdRng::seed_from_u64(seed);
    }
    RNG_COUNTER.store(1, Ordering::Relaxed);
    // Advance seed epoch so TLS RNGs are reinitialized lazily on next use
    SEED_EPOCH.fetch_add(1, Ordering::Relaxed);
    Ok(())
}

// removed legacy HS/Huffman implementations; see training::hs

// NPY helpers moved to io::npy
