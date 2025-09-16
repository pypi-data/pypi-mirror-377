from __future__ import annotations

import numpy as np

from word2vec_matryoshka import KeyedVectors, Word2Vec, set_seed


def test_kv_vectors_and_index_inmemory() -> None:
    set_seed(42)
    corpus = [["hello", "world"], ["hello", "computer"], ["computer", "science"]]
    m = Word2Vec(sentences=corpus, vector_size=8, window=2, min_count=1, workers=1)
    m.train(corpus, epochs=1)

    wv = m.wv
    idx = wv.index_to_key
    assert isinstance(idx, list) and all(isinstance(k, str) for k in idx)
    vecs = wv.vectors
    assert isinstance(vecs, np.ndarray)
    assert vecs.shape == (len(idx), m.vector_size)
    # Row order should correspond to index_to_key order
    for i, key in enumerate(idx):
        v = wv.get_vector(key)
        assert np.allclose(v, vecs[i])


def test_kv_vectors_and_index_memmap(tmp_path) -> None:
    set_seed(7)
    corpus = [["a", "b"], ["a", "c"], ["c", "d"], ["d", "e"]]
    m = Word2Vec(sentences=corpus, vector_size=6, window=2, min_count=1, workers=1)
    m.train(corpus, epochs=1)

    base = tmp_path / "kv"
    m.wv.save(str(base))

    wv = KeyedVectors.load(str(base), mmap="r")
    idx = wv.index_to_key
    vecs = wv.vectors
    assert isinstance(idx, list) and isinstance(vecs, np.ndarray)
    assert vecs.shape == (len(idx), m.vector_size)
