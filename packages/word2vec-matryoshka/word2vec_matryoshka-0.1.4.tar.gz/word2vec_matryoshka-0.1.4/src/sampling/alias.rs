// Vose's alias method for O(1) sampling from a discrete distribution.
use rand::rngs::StdRng;
use rand::Rng;

/// Build alias tables (`prob`, `alias`) from normalized weights.
pub(crate) fn build_alias(weights: &[f64]) -> (Vec<f32>, Vec<usize>) {
    let n = weights.len();
    if n == 0 {
        return (Vec::new(), Vec::new());
    }
    let mut prob: Vec<f64> = vec![0.0; n];
    let mut alias: Vec<usize> = vec![0; n];
    let mut small: Vec<usize> = Vec::new();
    let mut large: Vec<usize> = Vec::new();
    let scale = n as f64;
    for (i, &w) in weights.iter().enumerate() {
        let p = w * scale;
        prob[i] = p;
        if p < 1.0 {
            small.push(i);
        } else {
            large.push(i);
        }
    }
    while let (Some(s), Some(l)) = (small.pop(), large.pop()) {
        alias[s] = l;
        prob[l] = prob[l] + prob[s] - 1.0;
        if prob[l] < 1.0 {
            small.push(l);
        } else {
            large.push(l);
        }
    }
    let prob_f32 = prob.into_iter().map(|x| x as f32).collect();
    (prob_f32, alias)
}

/// Sample a category using precomputed alias tables.
pub(crate) fn sample_alias(prob: &[f32], alias: &[usize], rng: &mut StdRng) -> usize {
    let n = prob.len();
    if n == 0 {
        return 0;
    }
    let i = rng.gen_range(0..n);
    let r: f32 = rng.gen();
    if r < prob[i] {
        i
    } else {
        alias[i]
    }
}
