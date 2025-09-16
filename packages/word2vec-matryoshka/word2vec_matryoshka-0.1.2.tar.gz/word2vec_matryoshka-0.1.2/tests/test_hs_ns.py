from __future__ import annotations

import numpy as np
import pytest

from word2vec_matryoshka import Word2Vec


def small_corpus():
    return [["a", "b", "c"], ["b", "c", "d"], ["c", "d", "e"]]


@pytest.mark.parametrize(
    "cfg",
    [
        dict(sg=1, negative=5, hs=0),
        dict(sg=1, negative=0, hs=1),
        dict(sg=0, negative=5, hs=0),
    ],
)
def test_train_variants(cfg):
    corpus = small_corpus()
    m = Word2Vec(
        sentences=corpus, vector_size=16, window=2, min_count=1, workers=2, levels=[4, 8, 16], **cfg
    )
    m.train(corpus, total_examples=len(corpus), epochs=1)
    # basic checks
    vec = m.wv["b"]
    assert isinstance(vec, np.ndarray) and vec.shape == (16,)
    sims = m.wv.most_similar("b", topn=5)
    tokens = sorted({t for s in corpus for t in s})
    expected = min(5, len(tokens) - 1)
    assert isinstance(sims, list) and len(sims) == expected
    assert all(isinstance(w, str) and isinstance(s, float) for w, s in sims)
