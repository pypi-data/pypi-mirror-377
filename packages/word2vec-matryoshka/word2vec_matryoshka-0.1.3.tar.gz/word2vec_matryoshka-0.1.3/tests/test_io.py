from __future__ import annotations

from word2vec_matryoshka import KeyedVectors, Word2Vec


def test_save_load_vectors(tmp_path) -> None:
    m = Word2Vec(vector_size=4, min_count=1)
    m.train([["hello", "world"]], total_examples=1, epochs=1)
    vec_path = tmp_path / "wv.json"
    m.wv.save(str(vec_path))

    wv = KeyedVectors.load(str(vec_path), mmap="r")
    v = wv["hello"]
    assert v.shape[0] == 4
