from __future__ import annotations

from word2vec_matryoshka import Word2Vec


class RestartableCorpus:
    """A restartable iterable over tokenized sentences.

    Each call to __iter__ returns a fresh iterator, allowing multiple epochs.
    """

    def __init__(self, data):
        self._data = list(data)

    def __iter__(self):
        for sent in self._data:
            yield list(sent)


def test_restartable_iterable_epochs2():
    corpus = RestartableCorpus([["a", "b", "c"], ["b", "c", "d"]])

    # workers=1 to demonstrate true streaming compatibility
    m = Word2Vec(sentences=corpus, vector_size=16, window=2, min_count=1, workers=1, levels=[8, 16])
    # Train for two epochs; RestartableCorpus supports multiple passes
    m.train(corpus, total_examples=2, epochs=2)

    # Basic sanity
    assert m.wv["a"].shape == (16,)
