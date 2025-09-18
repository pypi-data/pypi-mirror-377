from __future__ import annotations

import pytest

from word2vec_matryoshka import KeyedVectors, Word2Vec


def test_missing_word_raises():
    m = Word2Vec(vector_size=8)
    with pytest.raises(KeyError):
        _ = m.wv["__unknown__"]


def test_kv_load_accepts_mmap(tmp_path):
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    base = tmp_path / "kv"
    m.wv.save(str(base))
    # should accept mmap kw and not crash
    kv = KeyedVectors.load(str(base), mmap="r")
    _ = kv["a"]


def test_most_similar_missing_word_inmemory():
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    with pytest.raises(KeyError):
        _ = m.wv.most_similar("__unknown__", topn=3)


def test_most_similar_missing_word_memmap(tmp_path):
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    base = tmp_path / "kv"
    m.wv.save(str(base))
    kv = KeyedVectors.load(str(base), mmap="r")
    with pytest.raises(KeyError):
        _ = kv.most_similar("__unknown__", topn=3)


def test_kv_load_shape_mismatch_raises(tmp_path):
    import json
    import numpy as np

    base = tmp_path / "bad"
    # vocab 3 rows
    (tmp_path / "bad.vocab.json").write_text(json.dumps(["a", "b", "c"]))
    # npy only 2 rows -> mismatch
    np.save(str(base) + ".npy", np.zeros((2, 4), dtype=np.float32))

    with pytest.raises(ValueError):
        _ = KeyedVectors.load(str(base))
    with pytest.raises(ValueError):
        _ = KeyedVectors.load(str(base), mmap="r")
