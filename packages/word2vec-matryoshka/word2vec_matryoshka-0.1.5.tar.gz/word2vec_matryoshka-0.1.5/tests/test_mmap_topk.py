from __future__ import annotations

import numpy as np

from word2vec_matryoshka import KeyedVectors, Word2Vec


def test_mmap_most_similar_topk(tmp_path):
    corpus = [["x", "y", "z"], ["y", "z", "w"], ["z", "w", "v"]]
    m = Word2Vec(
        sentences=corpus,
        vector_size=32,
        window=2,
        min_count=1,
        workers=2,
        negative=3,
        sg=1,
        hs=0,
        levels=[8, 16, 32],
    )
    base = tmp_path / "wv"
    m.wv.save(str(base))

    # mmap load
    wv = KeyedVectors.load(str(base), mmap="r")
    # topk should exclude self and be sorted
    sims = wv.most_similar("y", topn=3)
    assert len(sims) == 3
    words = [w for w, _ in sims]
    assert "y" not in words
    scores = [s for _, s in sims]
    assert scores == sorted(scores, reverse=True)

    # level prefix should change only the dimension (shape), not crash
    vec8 = wv.get_vector("y", level=8)
    assert isinstance(vec8, np.ndarray) and vec8.shape == (8,)
