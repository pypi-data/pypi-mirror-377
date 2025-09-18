# word2vec‑matryoshka

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/feisan/word2vec_matryoshka)

Lightweight Word2Vec for Python, backed by Rust (PyO3). It implements a small, practical subset of Word2Vec (Skip‑gram/CBOW with Negative Sampling or Hierarchical Softmax) and adds Matryoshka multi‑level representations: you can train on multiple prefix dimensions and query a prefix level without recomputing vectors.

This project is a learning/practice (“vibe coding”) effort inspired by gensim. It intentionally covers only a tiny part of gensim’s functionality and adds Matryoshka prefix representations. If you need a full‑featured Word2Vec, please try gensim first.

## Install

```bash
pip install word2vec-matryoshka
```

## Quick start

```python
from word2vec_matryoshka import Word2Vec, KeyedVectors, set_seed

set_seed(42)
corpus = [["hello", "world"], ["computer", "science"]]

model = Word2Vec(
    sentences=corpus,
    vector_size=64,
    window=5,
    min_count=1,
    workers=2,
    negative=5,
    sg=1,    # 1=Skip-gram, 0=CBOW
    hs=0,    # 1=Hierarchical Softmax, 0=Negative Sampling
    levels=[16, 32, 64],  # Matryoshka prefix dimensions
)

# Full vector
vec = model.wv["hello"]

# Top-5 similar at a prefix level (e.g., 32 dims)
sims = model.wv.most_similar("hello", topn=5, level=32)

# Save/load vectors (base path creates .vocab.json + .npy)
model.wv.save("vectors")
wv = KeyedVectors.load("vectors", mmap="r")  # zero-copy memmap
vec16 = wv.get_vector("hello", level=16)

# Inspect vocabulary and the vector matrix
print(wv.index_to_key[:5])    # e.g., ['hello', 'computer', ...]
M = wv.vectors                # numpy.ndarray with shape (n_words, vector_size)
print(M.shape)
```

## What’s inside

- Word2Vec training: Skip‑gram or CBOW with Negative Sampling or Hierarchical Softmax
- Matryoshka levels: train multiple prefix dimensions and query by `level`
- Vector I/O: `KeyedVectors.save(base)` → `base.vocab.json` + `base.npy`; `KeyedVectors.load(base, mmap='r')` for fast, memory‑mapped reads
- Determinism: `set_seed(seed)` for reproducible runs

## Scope and disclaimer

- Not a drop‑in replacement for gensim. Only a minimal API is provided (`Word2Vec`, `KeyedVectors`, `wv[...]`, `most_similar`, `get_vector`).
- Built as a small practice project to explore PyO3/Rust performance and Matryoshka prefix training.
- For most production needs, start with gensim first, then evaluate if this project’s Matryoshka feature helps your use case.

## License

MIT — see `LICENSE`.
