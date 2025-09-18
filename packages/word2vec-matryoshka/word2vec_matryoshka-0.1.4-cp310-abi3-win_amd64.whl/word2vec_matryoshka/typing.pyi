from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

def set_seed(seed: int) -> None: ...

class KeyedVectors:
    vector_size: int
    def __init__(self) -> None: ...
    @staticmethod
    def load(path: str, mmap: str | None = ...) -> KeyedVectors: ...
    def save(self, path: str) -> None: ...
    def most_similar(
        self,
        word: str,
        topn: int = ...,
        level: int | None = ...,
    ) -> list[tuple[str, float]]: ...
    def __getitem__(self, key: str) -> np.ndarray: ...
    def get_vector(self, key: str, level: int | None = ...) -> np.ndarray: ...

class Word2Vec:
    vector_size: int
    def __init__(
        self,
        sentences: Iterable[Sequence[str]] | None = ...,
        *,
        vector_size: int = ...,
        window: int = ...,
        min_count: int = ...,
        max_final_vocab: int | None = ...,
        workers: int = ...,
        negative: int = ...,
        sg: int = ...,
        hs: int = ...,
        cbow_mean: int = ...,
        levels: list[int] | None = ...,
        alpha: float = ...,
        min_alpha: float = ...,
        epochs: int = ...,
        verbose: bool = ...,
        progress_interval: float = ...,
    ) -> None: ...
    @classmethod
    def load(cls, path: str) -> Word2Vec: ...
    def save(self, path: str) -> None: ...
    def train(
        self,
        corpus_iterable: Iterable[Sequence[str]],
        total_examples: int | None = ...,
        epochs: int | None = ...,
    ) -> None: ...
    @property
    def wv(self) -> KeyedVectors: ...
