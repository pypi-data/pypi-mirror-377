use pyo3::prelude::*;
use pyo3::types::PyModule;
use std::sync::atomic::{AtomicBool, Ordering};

// Global flag to ensure we only set up the logger once per process.
pub static LOGGING_READY: AtomicBool = AtomicBool::new(false);

/// Ensure the module logger is configured and emit an INFO message.
///
/// Safe to call from any thread; acquires the GIL internally.
pub fn log_info_msg(msg: &str) {
    Python::with_gil(|py| {
        if let Ok(logging) = PyModule::import_bound(py, "logging") {
            // Lazy logger initialization
            if !LOGGING_READY.swap(true, Ordering::Relaxed) {
                if let Ok(logger0) = logging
                    .getattr("getLogger")
                    .and_then(|f| f.call1(("word2vec_matryoshka",)))
                {
                    if let Ok(handlers) = logger0.getattr("handlers") {
                        let len: usize = handlers
                            .getattr("__len__")
                            .and_then(|l| l.call0())
                            .and_then(|v| v.extract())
                            .unwrap_or(0);
                        if len == 0 {
                            if let (Ok(sh), Ok(fmtmod)) = (
                                logging.getattr("StreamHandler").and_then(|c| c.call0()),
                                logging.getattr("Formatter"),
                            ) {
                                if let Ok(fmt) = fmtmod.call1((
                                    "%(asctime)s: %(levelname)s: %(message)s",
                                    "%Y-%m-%d %H:%M:%S",
                                )) {
                                    let _ = sh.call_method1("setFormatter", (fmt,));
                                }
                                let _ = logger0.call_method1("addHandler", (sh,));
                                if let Ok(info) = logging.getattr("INFO") {
                                    let _ = logger0.call_method1("setLevel", (info,));
                                }
                                // allow propagation so external handlers (e.g., pytest caplog) can capture
                                let _ = logger0.setattr("propagate", true);
                            }
                        }
                    }
                }
            }
            if let Ok(logger) = logging
                .getattr("getLogger")
                .and_then(|f| f.call1(("word2vec_matryoshka",)))
            {
                let _ = logger.call_method1("info", (msg.to_string(),));
            }
        }
    });
}

