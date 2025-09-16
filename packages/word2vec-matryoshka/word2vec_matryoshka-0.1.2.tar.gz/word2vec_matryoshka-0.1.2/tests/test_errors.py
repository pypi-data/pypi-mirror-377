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
