from __future__ import annotations

from word2vec_matryoshka import Word2Vec


def test_basic_flow(tmp_path) -> None:
    sentences = [["hello", "world"], ["computer", "science"]]
    m = Word2Vec(sentences=sentences, vector_size=8, window=5, min_count=1, workers=2)
    assert m.vector_size == 8

    path = tmp_path / "model.json"
    m.save(str(path))

    m2 = Word2Vec.load(str(path))
    m2.train([["hello", "computer"]], total_examples=1, epochs=1)

    vec = m2.wv["computer"]
    assert vec.shape[0] == 8

    sims = m2.wv.most_similar("computer", topn=3)
    assert isinstance(sims, list) and len(sims) <= 3
