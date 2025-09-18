#![allow(
    clippy::arc_with_non_send_sync,
    clippy::needless_lifetimes,
    clippy::mut_from_ref
)]
use std::cell::UnsafeCell;
use std::sync::Arc;
use std::sync::Mutex;

pub const SHARDS: usize = 64;

#[derive(Clone)]
/// Shared, stripe-locked weight matrix for parallel training.
///
/// - Data is stored as a flat row-major `Vec<f32>` inside `UnsafeCell` and
///   shared via `Arc`.
/// - A fixed number of shard mutexes reduces contention; row i is guarded by
///   `shards[i % SHARDS]`.
/// - Methods operating on rows are `unsafe` because callers must acquire the
///   appropriate locks before mutating.
pub struct SharedWeights {
    pub(crate) data: Arc<UnsafeCell<Vec<f32>>>,
    pub(crate) shards: Arc<Vec<Mutex<()>>>,
    pub(crate) dim: usize,
    pub(crate) _rows: usize,
}

unsafe impl Sync for SharedWeights {}
unsafe impl Send for SharedWeights {}

impl SharedWeights {
    pub fn new(vec: Vec<f32>, dim: usize) -> Self {
        let rows = if dim == 0 { 0 } else { vec.len() / dim };
        let data = Arc::new(UnsafeCell::new(vec));
        let shards = Arc::new((0..SHARDS).map(|_| Mutex::new(())).collect());
        Self {
            data,
            shards,
            dim,
            _rows: rows,
        }
    }
    /// Consume and return the underlying vector. Panics if other `Arc` refs exist.
    pub fn into_vec(self) -> Vec<f32> {
        Arc::try_unwrap(self.data).unwrap().into_inner()
    }
    /// Lock the shard mutexes for two rows in a consistent order to avoid deadlocks.
    #[allow(dead_code)]
    pub fn lock_two<'a>(
        &'a self,
        r1: usize,
        r2: usize,
    ) -> (
        std::sync::MutexGuard<'a, ()>,
        Option<std::sync::MutexGuard<'a, ()>>,
    ) {
        let s1 = r1 % SHARDS;
        let s2 = r2 % SHARDS;
        if s1 == s2 {
            let g1 = self.shards[s1].lock().unwrap();
            (g1, None)
        } else if s1 < s2 {
            let g1 = self.shards[s1].lock().unwrap();
            let g2 = self.shards[s2].lock().unwrap();
            (g1, Some(g2))
        } else {
            let g2 = self.shards[s2].lock().unwrap();
            let g1 = self.shards[s1].lock().unwrap();
            (g1, Some(g2))
        }
    }
    #[allow(dead_code)]
    /// Borrow a mutable view of a full row. Caller must hold the row's shard lock.
    pub unsafe fn row_mut<'a>(&'a self, row: usize) -> &'a mut [f32] {
        let v = &mut *self.data.get();
        let start = row * self.dim;
        &mut v[start..start + self.dim]
    }
    /// Borrow a mutable view of the first `dim` elements of a row. Caller must hold the lock.
    pub unsafe fn row_prefix_mut<'a>(&'a self, row: usize, dim: usize) -> &'a mut [f32] {
        let v = &mut *self.data.get();
        let start = row * self.dim;
        &mut v[start..start + dim]
    }
    /// Borrow an immutable view of the first `dim` elements of a row.
    pub unsafe fn row_prefix<'a>(&'a self, row: usize, dim: usize) -> &'a [f32] {
        let v = &*self.data.get();
        let start = row * self.dim;
        &v[start..start + dim]
    }
}
