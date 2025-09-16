# Contributor Guide

This repository implements a Python library backed by Rust (PyO3) for Word2Vec with Matryoshka multi‑level representations. This guide explains how to develop, test, and contribute using the project’s tooling and conventions.

## Repository Layout
- Root: `pyproject.toml` (PEP 621 single source of truth), `Cargo.toml` for Rust, and `uv.lock` for reproducible Python environments.
- `src/`: Rust core and PyO3 bindings.
  - `lib.rs`: PyO3 module entry (`_core`), high‑level model/types, logging/RNG glue.
  - `io/npy.rs`: NPY read/write helpers.
  - `ops/`: math kernels, SIMD paths, and thread‑local scratch buffers.
  - `weights.rs`: striped‑lock shared weight storage (`SharedWeights`, `SHARDS`).
  - `training/ns.rs`: Skip‑gram/CBOW with Negative Sampling (sequential + striped variants).
  - `training/hs.rs`: Hierarchical Softmax updates and Huffman tree build.
  - `sampling/alias.rs`: alias method build/sample utilities.
- `python/word2vec_matryoshka/`: Thin Python package surface and typing stubs.
- `tests/`: Python tests for API, I/O, mmap, streaming, and HS/NS variants.
- Optional: `benches/` for performance benchmarks, `examples/` for end‑to‑end demos (kept small).

## Tools and Versions
- Python env/packaging: `uv` (PEP 582/venv compatible). Use `uv sync` to materialize the environment.
- Build Rust extension: `maturin` via `uvx maturin` (no global install needed).
- Lint/format: `ruff` for Python; `cargo fmt` and `cargo clippy -- -D warnings` for Rust.
- Test runner: `pytest` via `uv run -m pytest` (ensures it sees the dev install built by maturin).

## Common Tasks
- Sync environment: `uv sync`
- Add runtime deps: `uv add <package>`; dev deps: `uv add --dev ruff pytest maturin`
- Dev install Rust extension: `uvx maturin develop`
- Build wheels: `uvx maturin build --release`
- Run tests: `uv run -m pytest -q` (after `uvx maturin develop`)
- Lint Python: `uv run ruff check .` and `uv run ruff format .`
- Rust quality: `cargo fmt` and `cargo clippy -- -D warnings`

Notes
- Prefer `uv run -m pytest` over `uvx pytest`. The former uses the project’s environment and sees the extension installed by `maturin develop`.
- When adding or updating dependencies, commit the updated `uv.lock` for reproducibility.

## Coding Conventions
### Python
- Style enforced by Ruff; follow `snake_case` for functions/variables, `CapWords` for classes, modules lower_snake_case.
- Public API mirrors gensim when sensible: `Word2Vec`, `KeyedVectors`, `wv[...]`, `wv.get_vector`, `wv.most_similar`.
- All vector returns are `numpy.ndarray`. Saving/loading vectors supports memory‑mapping (`mmap='r'`).

### Rust
- Keep `cargo fmt` and `cargo clippy -- -D warnings` clean. Use `snake_case` for functions/variables, `UpperCamelCase` for types/traits, and `SCREAMING_SNAKE_CASE` for constants.
- PyO3 0.22 Bound API: use `Bound<'py, T>` and `Py<T>` appropriately; avoid deprecated patterns.
- Cloning Python handles: use `clone_ref(py)` under the GIL; don’t call `clone()` on `Py<T>`.
- Release the GIL for blocking/CPU work using `Python::with_gil(|py| py.allow_threads(|| { ... }))`.
- Parallelism via `rayon`; guard data races with lock striping if mutating shared weights (see `weights.rs`).
- Place compute kernels and SIMD in `ops/`, training steps in `training/`, I/O in `io/`, and sampling helpers in `sampling/`. Keep `lib.rs` as a thin integration layer.

## Word2Vec + Matryoshka Model
- Matryoshka levels: train/update on multiple prefix dimensions (e.g., `[d/4, d/2, d]`). Queries can request a `level` to limit the prefix length without recomputing vectors.
- Training variants: Skip‑gram/CBOW, Negative Sampling/Hierarchical Softmax are supported.
- Persisting vectors: `KeyedVectors.save(base)` writes `base.vocab.json` and `base.npy`. `KeyedVectors.load(base, mmap='r')` memory‑maps `.npy` for zero‑copy queries.
- Determinism: `set_seed(seed)` sets the process‑wide seed; per‑thread RNGs derive from it.
- Streaming: Accept any restartable iterable of token sequences for multi‑epoch training. For `workers > 1`, a bounded channel is used to prefetch chunks.

## GIL and Concurrency Guidelines
- Never block while holding the GIL if another thread needs it. Wrap channel consumption and CPU‑heavy loops in `allow_threads`.
- When iterating Python objects from a background thread, re‑bind under the GIL inside that thread.
- Use `rayon` for data parallelism; avoid holding locks across long computations. Use shard/striped locks for weight updates.

## Testing
- Organize tests under `tests/test_*.py`.
- Coverage targets:
  - Basic API: construction, `vector_size`, `wv[...]`, save/load.
  - Training: SG/CBOW with HS/NS; deterministic behavior with `set_seed`.
  - I/O: `KeyedVectors.save/load`, `mmap='r'` queries, top‑k similarity path.
  - Matryoshka: multiple levels during train and query.
  - Streaming: restartable iterable across multiple epochs, `workers=1` and `workers>1`.
- Run sequence locally:
  1) `uv sync`
  2) `uvx maturin develop`
  3) `uv run -m pytest -q`

## Benchmarks
- Keep micro‑benchmarks small and deterministic. Include comparisons for HS vs NS and effects of levels.
- Suggested layout: `benches/` with Python scripts invoking the installed module; document CPU, Python/Rust versions, and data sizes.

## Commit and Pull Requests
- Conventional Commits are encouraged (e.g., `feat(py): add Word2Vec API`, `fix(rust): avoid GIL deadlock`).
- PRs should describe motivation, changes, and risks; link issues; include before/after perf where relevant; call out breaking changes.

## Troubleshooting
- Build fails with PyO3 handle clone: use `clone_ref(py)` instead of `clone()` on `Py<T>`.
- Deadlock during tests: ensure blocking loops are inside `allow_threads` and that iterators from background threads acquire the GIL locally.
- Borrow after move of `Bound<'_, PyAny>`: if an object is needed across branches/epochs, `unbind()` once to `Py<PyAny>` and bind per‑use under the GIL.
- Delimiter/brace mismatches in long closures: prefer extracting helpers when editing complex loops.

## Acceptance Checklist (Quick)
- `uvx maturin develop` builds successfully.
- Examples and tests run via `uv run -m pytest -q`.
- Vectors save/load and `mmap='r'` queries work.
- `ruff`, `cargo fmt`, and `cargo clippy -- -D warnings` report no issues.
