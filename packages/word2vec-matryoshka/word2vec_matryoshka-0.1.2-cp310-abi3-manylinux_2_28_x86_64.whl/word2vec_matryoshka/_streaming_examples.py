"""Demonstrate training with a restartable streaming iterable.

Run:
  uv run python -m word2vec_matryoshka._streaming_examples
"""

from __future__ import annotations

from word2vec_matryoshka import Word2Vec


class RestartableCorpus:
    def __init__(self, data):
        self._data = list(data)

    def __iter__(self):
        for sent in self._data:
            yield list(sent)


def main():
    corpus = RestartableCorpus([["hello", "world"], ["computer", "science"], ["hello", "computer"]])
    model = Word2Vec(
        sentences=corpus,
        vector_size=32,
        window=5,
        min_count=1,
        workers=1,
        levels=[16, 32],
    )
    # Multiple epochs require the iterable to be restartable
    model.train(corpus, total_examples=3, epochs=2)
    print("vector shape:", model.wv["hello"].shape)


if __name__ == "__main__":
    main()
