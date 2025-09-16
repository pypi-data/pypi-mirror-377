use ahash::AHashMap as HashMap;
use numpy::{IntoPyArray, PyArray1, PyArray2, PyArrayMethods, PyUntypedArrayMethods};
use pyo3::exceptions::{PyKeyError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyModule, PySlice};

use crate::io::npy::{npy_header_len, read_npy_shape, write_npy};

#[pyclass(module = "word2vec_matryoshka")]
#[derive(Default)]
pub struct KeyedVectors {
    pub(crate) vectors: Option<HashMap<String, Vec<f32>>>,
    pub(crate) vector_size: usize,
    pub(crate) vocab: Vec<String>,
    pub(crate) index: HashMap<String, usize>,
    pub(crate) npy_path: Option<String>,
    pub(crate) memmap: Option<Py<PyAny>>,
}

#[pymethods]
impl KeyedVectors {
    #[new]
    fn new() -> Self {
        Self {
            vectors: Some(HashMap::new()),
            vector_size: 0,
            vocab: Vec::new(),
            index: HashMap::default(),
            npy_path: None,
            memmap: None,
        }
    }

    #[staticmethod]
    #[pyo3(signature = (path, mmap=None))]
    fn load(path: &str, mmap: Option<&str>) -> PyResult<Self> {
        let base = path;
        let vocab_path = format!("{}.vocab.json", base);
        let npy_path = format!("{}.npy", base);

        let vocab_text = std::fs::read_to_string(&vocab_path)
            .map_err(|e| PyValueError::new_err(format!("failed to read {}: {}", vocab_path, e)))?;
        let vocab: Vec<String> = serde_json::from_str(&vocab_text)
            .map_err(|e| PyValueError::new_err(format!("failed to parse vocab json: {}", e)))?;
        let mut index: HashMap<String, usize> = HashMap::default();
        for (i, w) in vocab.iter().enumerate() {
            index.insert(w.clone(), i);
        }

        let (_rows, cols) = read_npy_shape(&npy_path)?;

        if mmap == Some("r") {
            let memmap = Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let np = PyModule::import_bound(py, "numpy")?;
                let kwargs = PyDict::new_bound(py);
                kwargs.set_item("mmap_mode", "r")?;
                let arr = np.getattr("load")?.call((npy_path.as_str(),), Some(&kwargs))?;
                Ok(arr.into_py(py))
            })?;
            Ok(Self {
                vectors: None,
                vector_size: cols,
                vocab,
                index,
                npy_path: Some(npy_path),
                memmap: Some(memmap),
            })
        } else {
            let buf = std::fs::read(&npy_path)
                .map_err(|e| PyValueError::new_err(format!("failed to read {}: {}", npy_path, e)))?;
            let header_len = npy_header_len(&buf)?;
            let data_bytes = &buf[header_len..];
            let rows = vocab.len();
            let mut vectors: HashMap<String, Vec<f32>> = HashMap::default();
            let mut offset = 0usize;
            for i in 0..rows {
                let mut row = vec![0f32; cols];
                let bytes = &data_bytes[offset..offset + cols * 4];
                for j in 0..cols {
                    let start = j * 4;
                    row[j] = f32::from_le_bytes(bytes[start..start + 4].try_into().unwrap());
                }
                vectors.insert(vocab[i].clone(), row);
                offset += cols * 4;
            }
            Ok(Self {
                vectors: Some(vectors),
                vector_size: cols,
                vocab,
                index,
                npy_path: None,
                memmap: None,
            })
        }
    }

    fn save(&self, path: &str) -> PyResult<()> {
        let base = path;
        let vocab_path = format!("{}.vocab.json", base);
        let npy_path = format!("{}.npy", base);
        if let Some(map) = &self.vectors {
            // Preserve existing vocab order if available, fall back to map iteration
            let words: Vec<String> = if !self.vocab.is_empty() {
                self.vocab.clone()
            } else {
                map.keys().cloned().collect()
            };
            let cols = self.vector_size;
            // Atomic temp files
            let vocab_tmp = format!("{}.tmp", &vocab_path);
            let npy_tmp = format!("{}.tmp", &npy_path);
            std::fs::write(&vocab_tmp, serde_json::to_string(&words).unwrap()).map_err(|e| {
                PyValueError::new_err(format!("failed to write {}: {}", vocab_tmp, e))
            })?;
            let mut flat: Vec<f32> = Vec::with_capacity(words.len() * cols);
            for w in &words {
                let v = map
                    .get(w)
                    .ok_or_else(|| PyValueError::new_err("missing vector"))?;
                if v.len() != cols {
                    return Err(PyValueError::new_err("inconsistent vector size"));
                }
                flat.extend_from_slice(v);
            }
            write_npy(&npy_tmp, words.len(), cols, &flat)?;
            std::fs::rename(&vocab_tmp, &vocab_path).map_err(|e| {
                PyValueError::new_err(format!("failed to finalize {}: {}", vocab_path, e))
            })?;
            std::fs::rename(&npy_tmp, &npy_path).map_err(|e| {
                PyValueError::new_err(format!("failed to finalize {}: {}", npy_path, e))
            })?;
            Ok(())
        } else if let Some(src) = &self.npy_path {
            // Atomic temp files
            let vocab_tmp = format!("{}.tmp", &vocab_path);
            let npy_tmp = format!("{}.tmp", &npy_path);
            std::fs::write(&vocab_tmp, serde_json::to_string(&self.vocab).unwrap()).map_err(|e| {
                PyValueError::new_err(format!("failed to write {}: {}", vocab_tmp, e))
            })?;
            std::fs::copy(src, &npy_tmp)
                .map_err(|e| PyValueError::new_err(format!("failed to copy npy: {}", e)))?;
            std::fs::rename(&vocab_tmp, &vocab_path).map_err(|e| {
                PyValueError::new_err(format!("failed to finalize {}: {}", vocab_path, e))
            })?;
            std::fs::rename(&npy_tmp, &npy_path).map_err(|e| {
                PyValueError::new_err(format!("failed to finalize {}: {}", npy_path, e))
            })?;
            Ok(())
        } else {
            Err(PyValueError::new_err("no vectors to save"))
        }
    }

    #[pyo3(signature = (word, topn=None, level=None))]
    fn most_similar<'py>(
        &self,
        py: Python<'py>,
        word: &str,
        topn: Option<usize>,
        level: Option<usize>,
    ) -> PyResult<Vec<(String, f32)>> {
        let topn = topn.unwrap_or(10);
        let use_dim = level.unwrap_or(self.vector_size).min(self.vector_size);
        if use_dim == 0 || topn == 0 {
            return Ok(Vec::new());
        }
        // In-memory fast path
        if let Some(map) = &self.vectors {
            // Heavy O(n·d) loop: release the GIL
            let heap: Vec<(String, f32)> = py.allow_threads(|| {
                let v = map
                    .get(word)
                    .expect("checked above");
                let v_slice = &v[..use_dim];
                let mut na = 0.0f32;
                for i in 0..use_dim { na += v_slice[i] * v_slice[i]; }
                let na_sqrt = if na > 0.0 { na.sqrt() } else { 0.0 };
                let n = self.vocab.len();
                let k = topn.min(n.saturating_sub(1));
                let mut heap: Vec<(String, f32)> = Vec::with_capacity(k);
                for (w, u) in map.iter() {
                    if w == word { continue; }
                    let mut dot = 0.0f32; let mut nb = 0.0f32;
                    for i in 0..use_dim { let a = v_slice[i]; let b = u[i]; dot += a * b; nb += b * b; }
                    let sim = if na_sqrt == 0.0 || nb == 0.0 { 0.0 } else { dot / (na_sqrt * nb.sqrt()) };
                    if heap.len() < k {
                        heap.push((w.clone(), sim));
                    } else if let Some(pos) = heap.iter().enumerate().min_by(|a, b| a.1 .1.partial_cmp(&b.1 .1).unwrap()).map(|p| p.0) {
                        if sim > heap[pos].1 { heap[pos] = (w.clone(), sim); }
                    }
                }
                heap
            });
            let mut heap = heap;
            heap.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
            return Ok(heap);
        }
        // Memmap-backed path: copy each row prefix into Rust slices and compute on the fly
        let idx = *self
            .index
            .get(word)
            .ok_or_else(|| PyKeyError::new_err(format!("word '{}' not in vocab", word)))?;
        let memmap = self
            .memmap
            .as_ref()
            .ok_or_else(|| PyValueError::new_err("memmap not initialized"))?;
        // Bind array and capture raw metadata under the GIL
        let mm = memmap.bind(py);
        let arr: Bound<PyArray2<f32>> = mm.clone().downcast_into()?;
        let shape = arr.shape();
        let rows = shape[0];
        let cols = shape[1];
        let dim = use_dim.min(cols);
        // Pointer address to the first element; .npy is row-major (fortran_order=False)
        let base_addr = unsafe { arr.uget_raw([0, 0]) as *const f32 as usize };
        // Release the GIL for the O(n·d) similarity scan
        let heap: Vec<(usize, f32)> = py.allow_threads(|| {
            let base_ptr = base_addr as *const f32;
            // Read query prefix
            let qptr = unsafe { base_ptr.add(idx * cols) };
            let mut v_slice: Vec<f32> = vec![0.0; dim];
            for i in 0..dim {
                v_slice[i] = unsafe { std::ptr::read_unaligned(qptr.add(i)) };
            }
            // Precompute query norm
            let mut na = 0.0f32;
            for i in 0..dim { na += v_slice[i] * v_slice[i]; }
            let na_sqrt = if na > 0.0 { na.sqrt() } else { 0.0 };
            let mut heap: Vec<(usize, f32)> = Vec::with_capacity(topn.min(rows.saturating_sub(1)));
            for r in 0..rows {
                if r == idx { continue; }
                let uptr = unsafe { base_ptr.add(r * cols) };
                let mut dot = 0.0f32; let mut nb = 0.0f32;
                for i in 0..dim {
                    let a = v_slice[i];
                    let b = unsafe { std::ptr::read_unaligned(uptr.add(i)) };
                    dot += a * b; nb += b * b;
                }
                let sim = if na_sqrt == 0.0 || nb == 0.0 { 0.0 } else { dot / (na_sqrt * nb.sqrt()) };
                if heap.len() < topn {
                    heap.push((r, sim));
                } else if let Some(pos) = heap.iter().enumerate().min_by(|a, b| a.1 .1.partial_cmp(&b.1 .1).unwrap()).map(|p| p.0) {
                    if sim > heap[pos].1 { heap[pos] = (r, sim); }
                }
            }
            heap
        });
        // Sort and map to tokens under the GIL again
        let mut heap = heap;
        heap.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        Ok(heap.into_iter().map(|(i, s)| (self.vocab[i].clone(), s)).collect())
    }

    #[pyo3(signature = (key, level=None))]
    fn get_vector<'py>(
        &self,
        py: Python<'py>,
        key: &str,
        level: Option<usize>,
    ) -> PyResult<Bound<'py, PyArray1<f32>>> {
        let use_dim = level.unwrap_or(self.vector_size).min(self.vector_size);
        if let Some(map) = &self.vectors {
            let v = map
                .get(key)
                .ok_or_else(|| PyKeyError::new_err(format!("word '{}' not in vocab", key)))?;
            return Ok(v[..use_dim].to_vec().into_pyarray_bound(py));
        }
        let idx = *self
            .index
            .get(key)
            .ok_or_else(|| PyKeyError::new_err(format!("word '{}' not in vocab", key)))?;
        let memmap = self
            .memmap
            .as_ref()
            .ok_or_else(|| PyValueError::new_err("memmap not initialized"))?;
        let row = memmap.bind(py).get_item(idx)?;
        if use_dim == self.vector_size {
            let arr: Bound<PyArray1<f32>> = row.downcast_into()?;
            Ok(arr)
        } else {
            let sl = PySlice::new_bound(py, 0, use_dim as isize, 1);
            let sub = row.get_item(sl)?;
            let arr: Bound<PyArray1<f32>> = sub.downcast_into()?;
            Ok(arr)
        }
    }

    #[getter]
    fn vector_size(&self) -> PyResult<usize> {
        Ok(self.vector_size)
    }

    fn __getitem__<'py>(&self, py: Python<'py>, key: &str) -> PyResult<Bound<'py, PyArray1<f32>>> {
        self.get_vector(py, key, None)
    }

    #[getter]
    fn vectors<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
        if let Some(map) = &self.vectors {
            let rows = self.vocab.len();
            let cols = self.vector_size;
            // Build the flat buffer without the GIL
            let flat: Vec<f32> = py.allow_threads(|| {
                let mut flat = Vec::with_capacity(rows * cols);
                for w in &self.vocab {
                    let v = map.get(w).expect("vocab and map out of sync");
                    debug_assert_eq!(v.len(), cols);
                    flat.extend_from_slice(v);
                }
                flat
            });
            let arr1d = flat.into_pyarray_bound(py);
            let reshaped = arr1d.getattr("reshape")?.call1((rows, cols))?;
            let arr2d: Bound<PyArray2<f32>> = reshaped.downcast_into()?;
            Ok(arr2d)
        } else {
            // memmap-backed numpy array
            let memmap = self
                .memmap
                .as_ref()
                .ok_or_else(|| PyValueError::new_err("memmap not initialized"))?;
            let mm = memmap.bind(py);
            let arr: Bound<PyArray2<f32>> = mm.clone().downcast_into()?;
            Ok(arr)
        }
    }

    #[getter]
    fn index_to_key(&self) -> PyResult<Vec<String>> {
        Ok(self.vocab.clone())
    }
}
