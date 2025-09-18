use pyo3::exceptions::PyKeyboardInterrupt;
use pyo3::prelude::*;
use pyo3::types::PyModule;
use std::sync::atomic::{AtomicBool, Ordering};

// Global flag to ensure we only set up the logger once per process.
pub static LOGGING_READY: AtomicBool = AtomicBool::new(false);

/// Ensure the module logger is configured and emit an INFO message.
///
/// Safe to call from any thread; acquires the GIL internally. Returns an
/// error if logging raised (notably propagating `KeyboardInterrupt`).
pub fn log_info_msg(msg: &str) -> PyResult<()> {
    Python::with_gil(|py| -> PyResult<()> {
        let logging = PyModule::import_bound(py, "logging")?;
        let get_logger = logging.getattr("getLogger")?;
        let logger = get_logger.call1(("word2vec_matryoshka",))?;
        if !LOGGING_READY.swap(true, Ordering::Relaxed) {
            let handlers = logger.getattr("handlers")?;
            let len: usize = handlers.getattr("__len__")?.call0()?.extract()?;
            if len == 0 {
                let sh = logging.getattr("StreamHandler")?.call0()?;
                let fmtmod = logging.getattr("Formatter")?;
                let fmt = fmtmod.call1((
                    "%(asctime)s: %(levelname)s: %(message)s",
                    "%Y-%m-%d %H:%M:%S",
                ))?;
                sh.call_method1("setFormatter", (fmt,))?;
                logger.call_method1("addHandler", (sh,))?;
                let info = logging.getattr("INFO")?;
                logger.call_method1("setLevel", (info,))?;
                logger.setattr("propagate", true)?;
            }
        }
        logger.call_method1("info", (msg.to_string(),))?;
        Ok(())
    })
    .or_else(|err| {
        Python::with_gil(|py| {
            if err.is_instance_of::<PyKeyboardInterrupt>(py) {
                Err(err)
            } else {
                err.print(py);
                Ok(())
            }
        })
    })
}
