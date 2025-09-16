//! Hierarchical Softmax (HS) updates and Huffman tree construction.
#![allow(clippy::type_complexity, clippy::needless_range_loop)]
use std::cmp::Reverse;
use std::collections::BinaryHeap;

use crate::ops::{give_tls_vec1, give_tls_vec2, sigmoid, take_tls_vec1, take_tls_vec2};
use crate::training::ns::cbow_step_with_hidden;
use crate::weights::{SharedWeights, SHARDS};

/// Build Huffman codes and internal-node indices for each word.
pub(crate) fn build_huffman(counts: &[u64]) -> (Vec<Vec<u8>>, Vec<Vec<usize>>) {
    let n = counts.len();
    if n == 0 {
        return (Vec::new(), Vec::new());
    }
    let mut heap: BinaryHeap<(Reverse<u64>, usize, Option<usize>, Option<usize>)> =
        BinaryHeap::new();
    for (i, &c) in counts.iter().enumerate() {
        heap.push((Reverse(c.max(1)), i, None, None));
    }
    let mut next_index = n;
    let mut parents: Vec<(usize, usize)> = Vec::new();
    let mut is_leaf: Vec<bool> = vec![true; 2 * n - 1];
    while heap.len() > 1 {
        let (Reverse(w1), i1, _l1, _r1) = heap.pop().unwrap();
        let (Reverse(w2), i2, _l2, _r2) = heap.pop().unwrap();
        if parents.len() <= i1.max(i2) {
            parents.resize(i1.max(i2) + 1, (0, 0));
        }
        parents.push((i1, i2));
        is_leaf.push(false);
        heap.push((Reverse(w1 + w2), next_index, Some(i1), Some(i2)));
        next_index += 1;
    }
    let mut codes: Vec<Vec<u8>> = vec![Vec::new(); n];
    let mut points: Vec<Vec<usize>> = vec![Vec::new(); n];
    let mut nodes: Vec<(usize, Option<usize>, Option<usize>)> = vec![(0, None, None); 2 * n - 1];
    for (i, &(Reverse(_w), idx, l, r)) in heap.into_vec().iter().enumerate() {
        if i == 0 {
            nodes[idx] = (idx, l, r);
        }
    }
    // Build explicit tree representation
    let mut heap2: BinaryHeap<(Reverse<u64>, usize, Option<usize>, Option<usize>)> =
        BinaryHeap::new();
    for (i, &c) in counts.iter().enumerate() {
        heap2.push((Reverse(c.max(1)), i, None, None));
    }
    let mut parent: Vec<usize> = vec![0; 2 * n - 1];
    let mut left: Vec<usize> = vec![0; 2 * n - 1];
    let mut right: Vec<usize> = vec![0; 2 * n - 1];
    let mut next = n;
    while heap2.len() > 1 {
        let (Reverse(w1), i1, _l1, _r1) = heap2.pop().unwrap();
        let (Reverse(w2), i2, _l2, _r2) = heap2.pop().unwrap();
        left[next] = i1;
        right[next] = i2;
        parent[i1] = next;
        parent[i2] = next;
        heap2.push((Reverse(w1 + w2), next, Some(i1), Some(i2)));
        next += 1;
    }
    for i in 0..n {
        let mut code: Vec<u8> = Vec::new();
        let mut pts: Vec<usize> = Vec::new();
        let mut node = i;
        while parent[node] != 0 {
            let p = parent[node];
            code.push(if right[p] == node { 1 } else { 0 });
            pts.push(p);
            node = p;
        }
        code.reverse();
        pts.reverse();
        codes[i] = code;
        points[i] = pts;
    }
    (codes, points)
}

/// HS update for skip-gram on a code path to the root.
pub(crate) fn hs_update(
    w_in: &mut [f32],
    w_out: &mut [f32],
    center: usize,
    code: &[u8],
    points: &[usize],
    lr: f32,
    dim: usize,
) {
    let a_start = center * dim;
    // Accumulate neu1e and apply to a once at the end (consistent with standard HS)
    let mut neu1e = take_tls_vec2(dim);
    for (bbit, &node) in code.iter().zip(points.iter()) {
        let b_start = node * dim;
        // Compute score using current values
        let mut score = 0.0f32;
        for k in 0..dim {
            score += w_in[a_start + k] * w_out[b_start + k];
        }
        let pred = sigmoid(score);
        let label = if *bbit == 1 { 1.0 } else { 0.0 };
        let g = lr * (label - pred);
        // Update b using old value and accumulate neu1e
        for k in 0..dim {
            let a_k = w_in[a_start + k];
            let old = w_out[b_start + k];
            neu1e[k] += g * old;
            w_out[b_start + k] = old + g * a_k;
        }
    }
    // Apply neu1e to a
    for k in 0..dim {
        w_in[a_start + k] += neu1e[k];
    }
    give_tls_vec2(neu1e);
}

/// HS update for CBOW: accumulate context into hidden, then update along code path.
pub(crate) fn hs_update_cbow(
    w_in: &mut [f32],
    w_out: &mut [f32],
    context_indices: &[usize],
    code: &[u8],
    points: &[usize],
    lr: f32,
    dim: usize,
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
    for (bbit, &node) in code.iter().zip(points.iter()) {
        let b_start = node * dim;
        // First pass: score
        let mut score = 0.0f32;
        for k in 0..dim {
            score += h[k] * w_out[b_start + k];
        }
        let pred = sigmoid(score);
        let label = if *bbit == 1 { 1.0 } else { 0.0 };
        let g = lr * (label - pred);
        // Second pass: update and accumulate neu1e using old
        for k in 0..dim {
            let old = w_out[b_start + k];
            neu1e[k] += g * old;
            w_out[b_start + k] = old + g * h[k];
        }
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

pub(crate) fn hs_update_striped(
    w_in: &SharedWeights,
    w_out: &SharedWeights,
    center: usize,
    code: &[u8],
    points: &[usize],
    lr: f32,
    dim: usize,
) {
    let _g = w_in.shards[center % SHARDS].lock().unwrap();
    unsafe {
        // Copy "a" into TLS buffer (no fresh allocation each step)
        let mut a_buf = take_tls_vec1(dim);
        let a_src = w_in.row_prefix(center, dim);
        a_buf[..dim].copy_from_slice(&a_src[..dim]);
        let mut neu1e = take_tls_vec2(dim);
        for (bbit, &node) in code.iter().zip(points.iter()) {
            let _gb = w_out.shards[node % SHARDS].lock().unwrap();
            let label = if *bbit == 1 { 1.0 } else { 0.0 };
            let b = w_out.row_prefix_mut(node, dim);
            // Score from current b and a_buf
            let mut score = 0.0f32;
            for k in 0..dim {
                score += a_buf[k] * b[k];
            }
            let pred = sigmoid(score);
            let g = lr * (label - pred);
            for k in 0..dim {
                let old = b[k];
                neu1e[k] += g * old;
                b[k] = old + g * a_buf[k];
            }
        }
        let a_mut = w_in.row_prefix_mut(center, dim);
        for k in 0..dim {
            a_mut[k] = a_buf[k] + neu1e[k];
        }
        give_tls_vec2(neu1e);
        give_tls_vec1(a_buf);
    }
}

pub(crate) fn hs_update_cbow_striped(
    w_in: &SharedWeights,
    w_out: &SharedWeights,
    context_indices: &[usize],
    code: &[u8],
    points: &[usize],
    lr: f32,
    dim: usize,
    cbow_mean: bool,
) {
    let c = context_indices.len() as f32;
    let mut h = take_tls_vec1(dim);
    // Group reads by shard
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
    for (bbit, &node) in code.iter().zip(points.iter()) {
        let label = if *bbit == 1 { 1.0 } else { 0.0 };
        cbow_step_with_hidden(&h, w_out, node, label, lr, dim, &mut neu1e);
    }
    // Group writes by shard
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
