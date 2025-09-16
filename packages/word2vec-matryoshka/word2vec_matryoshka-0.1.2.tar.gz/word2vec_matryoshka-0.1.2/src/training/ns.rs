//! Skip-gram/CBOW with Negative Sampling (NS), sequential and striped variants.
#![allow(clippy::too_many_arguments, clippy::needless_range_loop)]
use rand::rngs::StdRng;
use rand::Rng;

use crate::ops::{
    accumulate_levels, dot_prefix, dual_axpy_prefix, give_tls_vec1, give_tls_vec2, sigmoid, take_tls_vec1,
    take_tls_vec2,
};
use crate::sampling::alias::sample_alias;
use crate::weights::{SharedWeights, SHARDS};

// removed legacy single-level SGNS helpers in favor of multi-level fused versions

/// Multi-level SGNS step for a single label (positive or negative), reusing
/// dot/norm computations incrementally across levels to avoid rescanning the
/// head prefix.
pub(crate) fn sgns_step_levels(
    w_in: &mut [f32],
    w_out: &mut [f32],
    center: usize,
    target: usize,
    label: f32,
    per_level_lr: f32,
    dim_full: usize,
    levels: &[usize],
) {
    let a_row_start = center * dim_full;
    let b_row_start = target * dim_full;
    let a_row = &mut w_in[a_row_start..a_row_start + dim_full];
    let b_row = &mut w_out[b_row_start..b_row_start + dim_full];
    let mut acc = 0usize;
    let mut head_dot = 0.0f32;
    let mut head_na = 0.0f32;
    let mut head_nb = 0.0f32;
    for &ldim in levels.iter() {
        if ldim == 0 { continue; }
        let to = ldim.min(dim_full);
        if to <= acc { continue; }
        // Use SIMD-optimized accumulation
        let mut dot_before = head_dot;
        let mut na_before = head_na;
        let mut nb_before = head_nb;
        accumulate_levels(a_row, b_row, acc, to, &mut dot_before, &mut na_before, &mut nb_before);
        let pred = sigmoid(dot_before);
        let g = per_level_lr * (label - pred);
        // Update 0..to in-place
        dual_axpy_prefix(&mut a_row[..to], &mut b_row[..to], g, to);
        // Update accumulators for next level using algebraic relations
        let gg = g * g;
        let new_dot = (1.0 + gg) * dot_before + g * (na_before + nb_before);
        let two_g = 2.0 * g;
        let new_na = na_before + two_g * dot_before + gg * nb_before;
        let new_nb = nb_before + two_g * dot_before + gg * na_before;
        head_dot = new_dot;
        head_na = new_na;
        head_nb = new_nb;
        acc = to;
    }
}

/// CBOW variant of NS: accumulate context into hidden, then update center.
pub(crate) fn sgns_update_cbow(
    w_in: &mut [f32],
    w_out: &mut [f32],
    context_indices: &[usize],
    target_center: usize,
    negative: usize,
    lr: f32,
    dim: usize,
    vocab_size: usize,
    rng: &mut StdRng,
    cbow_mean: bool,
) {
    let c = context_indices.len() as f32;
    let mut h = take_tls_vec1(dim);
    for &idx in context_indices {
        let start = idx * dim;
        for k in 0..dim {
            h[k] += w_in[start + k];
        }
    }
    if cbow_mean {
        for k in 0..dim {
            h[k] /= c.max(1.0);
        }
    }
    let mut neu1e = take_tls_vec2(dim);
    cbow_step(&h, w_out, target_center, 1.0, lr, dim, &mut neu1e);
    for _ in 0..negative {
        let mut neg = rng.gen_range(0..vocab_size);
        if neg == target_center {
            neg = (neg + 1) % vocab_size;
        }
        cbow_step(&h, w_out, neg, 0.0, lr, dim, &mut neu1e);
    }
    for &idx in context_indices {
        let start = idx * dim;
        for k in 0..dim {
            w_in[start + k] += if cbow_mean {
                neu1e[k] / c.max(1.0)
            } else {
                neu1e[k]
            };
        }
    }
    give_tls_vec1(h);
    give_tls_vec2(neu1e);
}

#[inline]
fn sgns_step_levels_locked_rows(
    a_row: &mut [f32],
    b_row: &mut [f32],
    label: f32,
    per_level_lr: f32,
    levels: &[usize],
    dim_full: usize,
) {
    let mut acc = 0usize;
    let mut head_dot = 0.0f32;
    let mut head_na = 0.0f32;
    let mut head_nb = 0.0f32;
    for &ldim in levels.iter() {
        if ldim == 0 { continue; }
        let to = ldim.min(dim_full);
        if to <= acc { continue; }
        let mut tail_dot = 0.0f32;
        let mut tail_na = 0.0f32;
        let mut tail_nb = 0.0f32;
        for k in acc..to {
            let a = a_row[k];
            let b = b_row[k];
            tail_dot += a * b;
            tail_na += a * a;
            tail_nb += b * b;
        }
        let dot_before = head_dot + tail_dot;
        let na_before = head_na + tail_na;
        let nb_before = head_nb + tail_nb;
        let pred = sigmoid(dot_before);
        let g = per_level_lr * (label - pred);
        dual_axpy_prefix(&mut a_row[..to], &mut b_row[..to], g, to);
        let gg = g * g;
        let new_dot = (1.0 + gg) * dot_before + g * (na_before + nb_before);
        let two_g = 2.0 * g;
        let new_na = na_before + two_g * dot_before + gg * nb_before;
        let new_nb = nb_before + two_g * dot_before + gg * na_before;
        head_dot = new_dot;
        head_na = new_na;
        head_nb = new_nb;
        acc = to;
    }
}

/// SGNS updates across levels with shared weights; batches all targets under a single w_in shard lock.
pub(crate) fn sgns_update_levels_striped_batched(
    w_in: &SharedWeights,
    w_out: &SharedWeights,
    center: usize,
    context: usize,
    negative: usize,
    lr: f32,
    levels: &[usize],
    dim_full: usize,
    vocab_size: usize,
    rng: &mut StdRng,
) {
    let per = lr / (levels.len() as f32).max(1.0);
    let _gin = w_in.shards[center % SHARDS].lock().unwrap();
    unsafe {
        let a_row = w_in.row_mut(center);
        // positive
        {
            let _gout = w_out.shards[context % SHARDS].lock().unwrap();
            let b_row = w_out.row_mut(context);
            sgns_step_levels_locked_rows(a_row, b_row, 1.0, per, levels, dim_full);
        }
        for _ in 0..negative {
            let mut neg = rng.gen_range(0..vocab_size);
            if neg == context { neg = (neg + 1) % vocab_size; }
            let _gout = w_out.shards[neg % SHARDS].lock().unwrap();
            let b_row = w_out.row_mut(neg);
            sgns_step_levels_locked_rows(a_row, b_row, 0.0, per, levels, dim_full);
        }
    }
}

/// SGNS updates across levels with alias negatives; batches under a single w_in shard lock.
pub(crate) fn sgns_update_levels_alias_striped_batched(
    w_in: &SharedWeights,
    w_out: &SharedWeights,
    center: usize,
    context: usize,
    negative: usize,
    lr: f32,
    levels: &[usize],
    dim_full: usize,
    prob: &[f32],
    alias: &[usize],
    rng: &mut StdRng,
) {
    let per = lr / (levels.len() as f32).max(1.0);
    let vocab_size = prob.len();
    let _gin = w_in.shards[center % SHARDS].lock().unwrap();
    unsafe {
        let a_row = w_in.row_mut(center);
        // positive
        {
            let _gout = w_out.shards[context % SHARDS].lock().unwrap();
            let b_row = w_out.row_mut(context);
            sgns_step_levels_locked_rows(a_row, b_row, 1.0, per, levels, dim_full);
        }
        for _ in 0..negative {
            let mut neg = sample_alias(prob, alias, rng);
            if neg == context { neg = (neg + 1) % vocab_size; }
            let _gout = w_out.shards[neg % SHARDS].lock().unwrap();
            let b_row = w_out.row_mut(neg);
            sgns_step_levels_locked_rows(a_row, b_row, 0.0, per, levels, dim_full);
        }
    }
}

/// SGNS updates across all levels for non-striped weights (uniform negatives).
pub(crate) fn sgns_update_levels(
    w_in: &mut [f32],
    w_out: &mut [f32],
    center: usize,
    context: usize,
    negative: usize,
    lr: f32,
    levels: &[usize],
    dim_full: usize,
    vocab_size: usize,
    rng: &mut StdRng,
) {
    let per = lr / (levels.len() as f32).max(1.0);
    sgns_step_levels(w_in, w_out, center, context, 1.0, per, dim_full, levels);
    for _ in 0..negative {
        let mut neg = rng.gen_range(0..vocab_size);
        if neg == context { neg = (neg + 1) % vocab_size; }
        sgns_step_levels(w_in, w_out, center, neg, 0.0, per, dim_full, levels);
    }
}

/// SGNS updates across all levels for non-striped weights (alias sampling).
pub(crate) fn sgns_update_levels_alias(
    w_in: &mut [f32],
    w_out: &mut [f32],
    center: usize,
    context: usize,
    negative: usize,
    lr: f32,
    levels: &[usize],
    dim_full: usize,
    prob: &[f32],
    alias: &[usize],
    rng: &mut StdRng,
) {
    let per = lr / (levels.len() as f32).max(1.0);
    sgns_step_levels(w_in, w_out, center, context, 1.0, per, dim_full, levels);
    let vocab_size = prob.len();
    for _ in 0..negative {
        let mut neg = sample_alias(prob, alias, rng);
        if neg == context { neg = (neg + 1) % vocab_size; }
        sgns_step_levels(w_in, w_out, center, neg, 0.0, per, dim_full, levels);
    }
}

/// CBOW NS updates using shared weights.
pub(crate) fn sgns_update_cbow_striped(
    w_in: &SharedWeights,
    w_out: &SharedWeights,
    context_indices: &[usize],
    target_center: usize,
    negative: usize,
    lr: f32,
    dim: usize,
    vocab_size: usize,
    rng: &mut StdRng,
    cbow_mean: bool,
) {
    let c = context_indices.len() as f32;
    let mut h = take_tls_vec1(dim);
    // Group reads by shard to reduce lock acquisition overhead
    let mut by_shard: [Vec<usize>; SHARDS] = std::array::from_fn(|_| Vec::new());
    for &idx in context_indices { by_shard[idx % SHARDS].push(idx); }
    for (s, rows) in by_shard.iter().enumerate() {
        if rows.is_empty() { continue; }
        let _g = w_in.shards[s].lock().unwrap();
        for &idx in rows {
            unsafe {
                let r = w_in.row_prefix(idx, dim);
                for k in 0..dim { h[k] += r[k]; }
            }
        }
    }
    if cbow_mean {
        for k in 0..dim {
            h[k] /= c.max(1.0);
        }
    }
    let mut neu1e = take_tls_vec2(dim);
    cbow_step_with_hidden(&h, w_out, target_center, 1.0, lr, dim, &mut neu1e);
    for _ in 0..negative {
        let mut neg = rng.gen_range(0..vocab_size);
        if neg == target_center {
            neg = (neg + 1) % vocab_size;
        }
        cbow_step_with_hidden(&h, w_out, neg, 0.0, lr, dim, &mut neu1e);
    }
    // Group writes by shard to reduce lock traffic
    let mut by_shard_w: [Vec<usize>; SHARDS] = std::array::from_fn(|_| Vec::new());
    for &idx in context_indices { by_shard_w[idx % SHARDS].push(idx); }
    for (s, rows) in by_shard_w.iter().enumerate() {
        if rows.is_empty() { continue; }
        let _g = w_in.shards[s].lock().unwrap();
        for &idx in rows {
            unsafe {
                let r = w_in.row_prefix_mut(idx, dim);
                for k in 0..dim {
                    r[k] += if cbow_mean { neu1e[k] / c.max(1.0) } else { neu1e[k] };
                }
            }
        }
    }
    give_tls_vec1(h);
    give_tls_vec2(neu1e);
}

/// CBOW NS updates using alias sampling for negatives with shared weights.
pub(crate) fn sgns_update_cbow_alias_striped(
    w_in: &SharedWeights,
    w_out: &SharedWeights,
    context_indices: &[usize],
    target_center: usize,
    negative: usize,
    lr: f32,
    dim: usize,
    prob: &[f32],
    alias: &[usize],
    rng: &mut StdRng,
    cbow_mean: bool,
) {
    let c = context_indices.len() as f32;
    let mut h = take_tls_vec1(dim);
    for &idx in context_indices {
        let _g = w_in.shards[idx % SHARDS].lock().unwrap();
        unsafe {
            let r = w_in.row_prefix(idx, dim);
            for k in 0..dim {
                h[k] += r[k];
            }
        }
    }
    if cbow_mean {
        for k in 0..dim {
            h[k] /= c.max(1.0);
        }
    }
    let mut neu1e = take_tls_vec2(dim);
    cbow_step_with_hidden(&h, w_out, target_center, 1.0, lr, dim, &mut neu1e);
    let vocab_size = prob.len();
    for _ in 0..negative {
        let mut neg = sample_alias(prob, alias, rng);
        if neg == target_center {
            neg = (neg + 1) % vocab_size;
        }
        cbow_step_with_hidden(&h, w_out, neg, 0.0, lr, dim, &mut neu1e);
    }
    for &idx in context_indices {
        let _g = w_in.shards[idx % SHARDS].lock().unwrap();
        unsafe {
            let r = w_in.row_prefix_mut(idx, dim);
            for k in 0..dim {
                r[k] += if cbow_mean {
                    neu1e[k] / c.max(1.0)
                } else {
                    neu1e[k]
                };
            }
        }
    }
    give_tls_vec1(h);
    give_tls_vec2(neu1e);
}

pub(crate) fn cbow_step(
    h: &[f32],
    w_out: &mut [f32],
    target: usize,
    label: f32,
    lr: f32,
    dim: usize,
    neu1e: &mut [f32],
) {
    let b_start = target * dim;
    // First pass: compute score without allocating
    let mut score = 0.0f32;
    for k in 0..dim {
        score += h[k] * w_out[b_start + k];
    }
    let pred = sigmoid(score);
    let g = lr * (label - pred);
    // Second pass: use the previously-read "old" values per element
    for k in 0..dim {
        let old = w_out[b_start + k];
        neu1e[k] += g * old;
        w_out[b_start + k] = old + g * h[k];
    }
}

pub(crate) fn cbow_step_with_hidden(
    h: &[f32],
    w_out: &SharedWeights,
    target: usize,
    label: f32,
    lr: f32,
    dim: usize,
    neu1e: &mut [f32],
) {
    let _g = w_out.shards[target % SHARDS].lock().unwrap();
    unsafe {
        let b = w_out.row_prefix_mut(target, dim);
        // First pass: compute score directly from current values
        let score = dot_prefix(h, b, dim);
        let pred = sigmoid(score);
        let g = lr * (label - pred);
        // Second pass: update with local "old" per element
        for k in 0..dim {
            let old = b[k];
            neu1e[k] += g * old;
            b[k] = old + g * h[k];
        }
    }
}

// removed alias non-striped update wrapper in favor of multi-level fused variant

pub(crate) fn sgns_update_cbow_alias(
    w_in: &mut [f32],
    w_out: &mut [f32],
    context_indices: &[usize],
    target_center: usize,
    negative: usize,
    lr: f32,
    dim: usize,
    prob: &[f32],
    alias: &[usize],
    rng: &mut StdRng,
    cbow_mean: bool,
) {
    let c = context_indices.len() as f32;
    let mut h = take_tls_vec1(dim);
    for &idx in context_indices {
        let start = idx * dim;
        for k in 0..dim {
            h[k] += w_in[start + k];
        }
    }
    if cbow_mean {
        for k in 0..dim {
            h[k] /= c.max(1.0);
        }
    }
    let mut neu1e = take_tls_vec2(dim);
    cbow_step(&h, w_out, target_center, 1.0, lr, dim, &mut neu1e);
    let vocab_size = prob.len();
    for _ in 0..negative {
        let mut neg = sample_alias(prob, alias, rng);
        if neg == target_center {
            neg = (neg + 1) % vocab_size;
        }
        cbow_step(&h, w_out, neg, 0.0, lr, dim, &mut neu1e);
    }
    for &idx in context_indices {
        let start = idx * dim;
        for k in 0..dim {
            w_in[start + k] += if cbow_mean {
                neu1e[k] / c.max(1.0)
            } else {
                neu1e[k]
            };
        }
    }
    give_tls_vec1(h);
    give_tls_vec2(neu1e);
}
