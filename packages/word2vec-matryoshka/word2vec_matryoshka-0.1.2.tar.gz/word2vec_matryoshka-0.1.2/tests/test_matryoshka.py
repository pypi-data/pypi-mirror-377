from __future__ import annotations

from word2vec_matryoshka import Word2Vec


def test_levels_training_and_query() -> None:
    sentences = [["a", "b", "c"], ["b", "c", "d"], ["c", "d", "e"]]
    m = Word2Vec(
        sentences=sentences,
        vector_size=16,
        window=2,
        min_count=1,
        workers=2,
        negative=3,
        sg=1,
        levels=[4, 8, 16],
    )
    # train a couple of epochs
    m.train(sentences, total_examples=None, epochs=2)
    # full vector
    v_full = m.wv["b"]
    assert v_full.shape[0] == 16
    # lower level vector
    v_l4 = m.wv.get_vector("b", level=4)
    assert v_l4.shape[0] == 4
    # most_similar at different levels should run
    sims_full = m.wv.most_similar("b", topn=3)
    sims_l4 = m.wv.most_similar("b", topn=3, level=4)
    assert isinstance(sims_full, list) and isinstance(sims_l4, list)
