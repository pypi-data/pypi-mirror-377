from __future__ import annotations

import numpy as np

from word2vec_matryoshka import Word2Vec, set_seed


def test_deterministic_with_seed():
    set_seed(12345)
    corpus = [["a", "b"], ["b", "c"], ["c", "d"]]

    m1 = Word2Vec(
        sentences=corpus,
        vector_size=12,
        window=2,
        min_count=1,
        workers=1,
        negative=3,
        sg=1,
        hs=0,
        levels=[6, 12],
    )
    m1.train(corpus, total_examples=len(corpus), epochs=1)
    v1 = m1.wv["b"].copy()

    set_seed(12345)
    m2 = Word2Vec(
        sentences=corpus,
        vector_size=12,
        window=2,
        min_count=1,
        workers=1,
        negative=3,
        sg=1,
        hs=0,
        levels=[6, 12],
    )
    m2.train(corpus, total_examples=len(corpus), epochs=1)
    v2 = m2.wv["b"].copy()

    assert np.allclose(v1, v2, rtol=1e-4, atol=1e-6)
