from __future__ import annotations

import numpy as np

from word2vec_matryoshka import Word2Vec


def test_prefix_slice_matches_full():
    corpus = [["hello", "computer"], ["hello", "world"]]
    m = Word2Vec(
        sentences=corpus,
        vector_size=24,
        window=2,
        min_count=1,
        workers=1,
        levels=[6, 12, 24],
    )
    v_full = m.wv["hello"]
    v12 = m.wv.get_vector("hello", level=12)
    assert np.allclose(v_full[:12], v12)
