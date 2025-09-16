// Math ops, optional SIMD kernels (via cfg), and thread-local buffers for training.

#[allow(dead_code)]
pub fn cosine(a: &[f32], b: &[f32]) -> f32 {
    let mut dot = 0.0f32;
    let mut na = 0.0f32;
    let mut nb = 0.0f32;
    for i in 0..a.len() {
        dot += a[i] * b[i];
        na += a[i] * a[i];
        nb += b[i] * b[i];
    }
    if na == 0.0 || nb == 0.0 {
        return 0.0;
    }
    dot / (na.sqrt() * nb.sqrt())
}

pub fn sigmoid(x: f32) -> f32 {
    #[cfg(feature = "fast_sigmoid")]
    {
        let y = x / (1.0 + x.abs());
        0.5 + 0.5 * y
    }
    #[cfg(not(feature = "fast_sigmoid"))]
    {
        1.0 / (1.0 + (-x).exp())
    }
}

use std::cell::RefCell;
// Reusable per-thread scratch buffers to avoid repeated allocations.
thread_local! {
    static TL_BUF1: RefCell<Vec<f32>> = const { RefCell::new(Vec::new()) };
    static TL_BUF2: RefCell<Vec<f32>> = const { RefCell::new(Vec::new()) };
}

pub fn take_tls_vec1(dim: usize) -> Vec<f32> {
    TL_BUF1.with(|b| {
        let mut v = b.borrow_mut();
        let mut out = Vec::new();
        std::mem::swap(&mut *v, &mut out);
        out.resize(dim, 0.0);
        out
    })
}

pub fn give_tls_vec1(mut v: Vec<f32>) {
    v.clear();
    TL_BUF1.with(|b| {
        let mut slot = b.borrow_mut();
        *slot = v;
    });
}

pub fn take_tls_vec2(dim: usize) -> Vec<f32> {
    TL_BUF2.with(|b| {
        let mut v = b.borrow_mut();
        let mut out = Vec::new();
        std::mem::swap(&mut *v, &mut out);
        out.resize(dim, 0.0);
        out
    })
}

pub fn give_tls_vec2(mut v: Vec<f32>) {
    v.clear();
    TL_BUF2.with(|b| {
        let mut slot = b.borrow_mut();
        *slot = v;
    });
}

#[inline]
pub fn dot_prefix(a: &[f32], b: &[f32], dim: usize) -> f32 {
    #[cfg(all(feature = "simd", target_arch = "x86_64"))]
    unsafe {
        dot_prefix_x86(a, b, dim)
    }
    #[cfg(all(feature = "simd", target_arch = "aarch64"))]
    unsafe {
        dot_prefix_aarch64(a, b, dim)
    }
    #[cfg(not(any(
        all(feature = "simd", target_arch = "x86_64"),
        all(feature = "simd", target_arch = "aarch64")
    )))]
    {
        let mut s = 0.0f32;
        for i in 0..dim {
            s += a[i] * b[i];
        }
        s
    }
}

#[inline]
#[cfg(all(feature = "simd", target_arch = "x86_64"))]
#[inline(always)]
unsafe fn accumulate_levels_x86(a: &[f32], b: &[f32], start: usize, end: usize, head_dot: &mut f32, head_na: &mut f32, head_nb: &mut f32) {
    use std::arch::x86_64::*;
    let mut i = start;
    let mut vdot = _mm256_setzero_ps();
    let mut vna = _mm256_setzero_ps();
    let mut vnb = _mm256_setzero_ps();
    
    while i + 8 <= end {
        let va = _mm256_loadu_ps(a.as_ptr().add(i));
        let vb = _mm256_loadu_ps(b.as_ptr().add(i));
        vdot = _mm256_fmadd_ps(va, vb, vdot);
        vna = _mm256_fmadd_ps(va, va, vna);
        vnb = _mm256_fmadd_ps(vb, vb, vnb);
        i += 8;
    }
    
    // Horizontal sum
    let dot_sum = _mm256_reduce_add_ps(vdot);
    let na_sum = _mm256_reduce_add_ps(vna);
    let nb_sum = _mm256_reduce_add_ps(vnb);
    
    // Add remaining elements
    while i < end {
        let a_val = *a.get_unchecked(i);
        let b_val = *b.get_unchecked(i);
        *head_dot += a_val * b_val;
        *head_na += a_val * a_val;
        *head_nb += b_val * b_val;
        i += 1;
    }
    
}

#[cfg(all(feature = "simd", target_arch = "aarch64"))]
#[inline(always)]
unsafe fn accumulate_levels_aarch64(a: &[f32], b: &[f32], start: usize, end: usize, head_dot: &mut f32, head_na: &mut f32, head_nb: &mut f32) {
    use std::arch::aarch64::*;
    let mut i = start;
    let mut vdot = vdupq_n_f32(0.0);
    let mut vna = vdupq_n_f32(0.0);
    let mut vnb = vdupq_n_f32(0.0);
    
    while i + 4 <= end {
        let va = vld1q_f32(a.as_ptr().add(i));
        let vb = vld1q_f32(b.as_ptr().add(i));
        vdot = vmlaq_f32(vdot, va, vb);
        vna = vmlaq_f32(vna, va, va);
        vnb = vmlaq_f32(vnb, vb, vb);
        i += 4;
    }
    
    // Horizontal sum
    let dot_sum = vaddvq_f32(vdot);
    let na_sum = vaddvq_f32(vna);
    let nb_sum = vaddvq_f32(vnb);
    
    // Add remaining elements
    while i < end {
        let a_val = *a.get_unchecked(i);
        let b_val = *b.get_unchecked(i);
        *head_dot += a_val * b_val;
        *head_na += a_val * a_val;
        *head_nb += b_val * b_val;
        i += 1;
    }
    
}

pub fn accumulate_levels(a: &[f32], b: &[f32], start: usize, end: usize, head_dot: &mut f32, head_na: &mut f32, head_nb: &mut f32) {
    #[cfg(all(feature = "simd", target_arch = "x86_64"))]
    {
        unsafe {
            accumulate_levels_x86(a, b, start, end, head_dot, head_na, head_nb);
            return;
        }
    }
    #[cfg(all(feature = "simd", target_arch = "aarch64"))]
    {
        unsafe {
            accumulate_levels_aarch64(a, b, start, end, head_dot, head_na, head_nb);
            return;
        }
    }
    // Fallback to scalar
    for i in start..end {
        let a_val = a[i];
        let b_val = b[i];
        *head_dot += a_val * b_val;
        *head_na += a_val * a_val;
        *head_nb += b_val * b_val;
    }
}

pub fn dual_axpy_prefix(a: &mut [f32], b: &mut [f32], g: f32, dim: usize) {
    #[cfg(all(feature = "simd", target_arch = "x86_64"))]
    {
        unsafe {
            if dual_axpy_prefix_x86(a, b, g, dim) {
                return;
            }
        }
    }
    #[cfg(all(feature = "simd", target_arch = "aarch64"))]
    {
        unsafe {
            if dual_axpy_prefix_aarch64(a, b, g, dim) {
                return;
            }
        }
    }
    for i in 0..dim {
        let a_k = a[i];
        let b_k = b[i];
        a[i] = a_k + g * b_k;
        b[i] = b_k + g * a_k;
    }
}

#[cfg(all(feature = "simd", target_arch = "x86_64"))]
unsafe fn dot_prefix_x86(a: &[f32], b: &[f32], dim: usize) -> f32 {
    use std::arch::x86_64::*;
    let mut i = 0usize;
    let mut sum = 0.0f32;
    if is_x86_feature_detected!("avx") {
        let mut acc = _mm256_setzero_ps();
        while i + 8 <= dim {
            let va = _mm256_loadu_ps(a.as_ptr().add(i));
            let vb = _mm256_loadu_ps(b.as_ptr().add(i));
            acc = _mm256_fmadd_ps(va, vb, acc);
            i += 8;
        }
        let mut tmp = [0.0f32; 8];
        _mm256_storeu_ps(tmp.as_mut_ptr(), acc);
        for t in &tmp {
            sum += *t;
        }
    } else if is_x86_feature_detected!("sse2") {
        let mut acc = _mm_setzero_ps();
        while i + 4 <= dim {
            let va = _mm_loadu_ps(a.as_ptr().add(i));
            let vb = _mm_loadu_ps(b.as_ptr().add(i));
            let prod = _mm_mul_ps(va, vb);
            acc = _mm_add_ps(acc, prod);
            i += 4;
        }
        let mut tmp = [0.0f32; 4];
        _mm_storeu_ps(tmp.as_mut_ptr(), acc);
        for t in &tmp {
            sum += *t;
        }
    }
    while i < dim {
        sum += a[i] * b[i];
        i += 1;
    }
    sum
}

#[cfg(all(feature = "simd", target_arch = "x86_64"))]
unsafe fn dual_axpy_prefix_x86(a: &mut [f32], b: &mut [f32], g: f32, dim: usize) -> bool {
    use std::arch::x86_64::*;
    let mut i = 0usize;
    if is_x86_feature_detected!("avx") {
        let vg = _mm256_set1_ps(g);
        while i + 8 <= dim {
            let va = _mm256_loadu_ps(a.as_ptr().add(i));
            let vb = _mm256_loadu_ps(b.as_ptr().add(i));
            let a_new = _mm256_fmadd_ps(vg, vb, va);
            let b_new = _mm256_fmadd_ps(vg, va, vb);
            _mm256_storeu_ps(a.as_mut_ptr().add(i), a_new);
            _mm256_storeu_ps(b.as_mut_ptr().add(i), b_new);
            i += 8;
        }
        while i < dim {
            let a_k = *a.get_unchecked(i);
            let b_k = *b.get_unchecked(i);
            *a.get_unchecked_mut(i) = a_k + g * b_k;
            *b.get_unchecked_mut(i) = b_k + g * a_k;
            i += 1;
        }
        return true;
    } else if is_x86_feature_detected!("sse2") {
        let vg = _mm_set1_ps(g);
        while i + 4 <= dim {
            let va = _mm_loadu_ps(a.as_ptr().add(i));
            let vb = _mm_loadu_ps(b.as_ptr().add(i));
            let a_new = _mm_add_ps(va, _mm_mul_ps(vg, vb));
            let b_new = _mm_add_ps(vb, _mm_mul_ps(vg, va));
            _mm_storeu_ps(a.as_mut_ptr().add(i), a_new);
            _mm_storeu_ps(b.as_mut_ptr().add(i), b_new);
            i += 4;
        }
        while i < dim {
            let a_k = *a.get_unchecked(i);
            let b_k = *b.get_unchecked(i);
            *a.get_unchecked_mut(i) = a_k + g * b_k;
            *b.get_unchecked_mut(i) = b_k + g * a_k;
            i += 1;
        }
        return true;
    }
    false
}

#[cfg(all(feature = "simd", target_arch = "aarch64"))]
unsafe fn dot_prefix_aarch64(a: &[f32], b: &[f32], dim: usize) -> f32 {
    use std::arch::aarch64::*;
    let mut i = 0usize;
    let mut acc = vdupq_n_f32(0.0);
    while i + 4 <= dim {
        let va = vld1q_f32(a.as_ptr().add(i));
        let vb = vld1q_f32(b.as_ptr().add(i));
        acc = vmlaq_f32(acc, va, vb);
        i += 4;
    }
    let mut sum = vaddvq_f32(acc);
    while i < dim {
        sum += a[i] * b[i];
        i += 1;
    }
    sum
}

#[cfg(all(feature = "simd", target_arch = "aarch64"))]
unsafe fn dual_axpy_prefix_aarch64(a: &mut [f32], b: &mut [f32], g: f32, dim: usize) -> bool {
    use std::arch::aarch64::*;
    let mut i = 0usize;
    let vg = vdupq_n_f32(g);
    while i + 4 <= dim {
        let va = vld1q_f32(a.as_ptr().add(i));
        let vb = vld1q_f32(b.as_ptr().add(i));
        let a_new = vmlaq_f32(va, vg, vb);
        let b_new = vmlaq_f32(vb, vg, va);
        vst1q_f32(a.as_mut_ptr().add(i), a_new);
        vst1q_f32(b.as_mut_ptr().add(i), b_new);
        i += 4;
    }
    while i < dim {
        let a_k = *a.get_unchecked(i);
        let b_k = *b.get_unchecked(i);
        *a.get_unchecked_mut(i) = a_k + g * b_k;
        *b.get_unchecked_mut(i) = b_k + g * a_k;
        i += 1;
    }
    true
}
