"""Minimal usage example for docs/tests."""

from __future__ import annotations

from . import KeyedVectors, Word2Vec


def main() -> None:
    common_texts = [["hello", "world"], ["computer", "science"], ["hello", "computer"]]
    model = Word2Vec(sentences=common_texts, vector_size=16, window=5, min_count=1, workers=2)
    model.save("word2vec.model")

    model = Word2Vec.load("word2vec.model")
    model.train([["hello", "world"]], total_examples=1, epochs=1)

    vector = model.wv["computer"]
    sims = model.wv.most_similar("computer", topn=5)
    print("vector shape:", vector.shape)
    print("top sims:", sims[:3])

    model.wv.save("word2vec.wordvectors")
    wv = KeyedVectors.load("word2vec.wordvectors", mmap="r")
    _ = wv["computer"]


if __name__ == "__main__":
    main()
