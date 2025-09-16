"""Word2Vec with Matryoshka multi-level representations (Python API).

This package exposes a small, gensim-like Python surface backed by a
Rust/PyO3 core. It provides the ``Word2Vec`` training interface and a
``KeyedVectors`` container for standalone vectors that can be saved,
loaded, and memory-mapped for zero-copy queries.

Quick example
-------------
>>> from word2vec_matryoshka import Word2Vec, KeyedVectors, set_seed
>>> set_seed(42)
>>> model = Word2Vec(sentences=[["hello", "world"]], vector_size=32, workers=2)
>>> vector = model.wv["hello"]  # numpy.ndarray
>>> sims = model.wv.most_similar("hello", topn=5)
>>> model.wv.save("vectors")
>>> wv = KeyedVectors.load("vectors", mmap='r')
>>> _ = wv.get_vector("hello", level=16)  # Matryoshka prefix

Notes
-----
- Matryoshka levels allow training on multiple prefix dimensions
  (e.g., ``[d/4, d/2, d]``) and querying a specific prefix via
  ``level`` without recomputing.
- Use ``set_seed(seed)`` for deterministic behavior across processes;
  per-thread RNGs derive from this seed.
"""

from ._core import KeyedVectors, Word2Vec, set_seed

__all__ = ["Word2Vec", "KeyedVectors", "set_seed"]


def _inject_docs() -> None:
    """Attach docstrings to public classes and methods exposed from Rust.

    Some attributes implemented in Rust may have read-only ``__doc__``.
    We guard assignments with ``try/except`` to avoid import-time errors.
    """

    # Module-level functions
    try:
        set_seed.__doc__ = (
            "Set the process-wide random seed for deterministic training.\n\n"
            "Parameters\n"
            "----------\n"
            "seed : int\n"
            "    Seed used to initialize the global RNG; per-thread RNGs\n"
            "    are derived from this value."
        )
    except Exception:
        pass

    # KeyedVectors class and methods
    try:
        KeyedVectors.__doc__ = (
            "Lightweight container for word vectors and vocabulary.\n\n"
            "Supports saving/loading to a pair of files (``.vocab.json`` and\n"
            "``.npy``). ``load(..., mmap='r')`` memory-maps the array for\n"
            "zero-copy read-only queries."
        )
    except Exception:
        pass

    for name, doc in {
        "load": (
            "Load vectors previously saved with ``save``.\n\n"
            "Parameters\n"
            "----------\n"
            "path : str\n"
            "    Base path used at save time (without extensions).\n"
            "mmap : Optional[str]\n"
            "    If ``'r'`` or ``'r+'``, memory-map the underlying ``.npy``\n"
            "    file for zero-copy access.\n\n"
            "Returns\n"
            "-------\n"
            "KeyedVectors\n"
        ),
        "save": (
            "Persist vectors to disk.\n\n"
            "Writes ``{path}.vocab.json`` (vocabulary and order) and\n"
            "``{path}.npy`` (float32 array in row-major order)."
        ),
        "most_similar": (
            "Return top-N most similar words by cosine similarity.\n\n"
            "Parameters\n"
            "----------\n"
            "word : str\n"
            "    Query token.\n"
            "topn : int, default 10\n"
            "    Number of results to return.\n"
            "level : Optional[int]\n"
            "    Optional Matryoshka prefix length. If provided, similarity\n"
            "    is computed on the vector prefix of the given length.\n\n"
            "Returns\n"
            "-------\n"
            "List[Tuple[str, float]]\n"
        ),
        "__getitem__": (
            "Return the vector for a single word.\n\n"
            "Equivalent to ``get_vector(word)``. Returns a NumPy array with\n"
            "dtype ``float32``."
        ),
        "get_vector": (
            "Return the vector for ``key`` as a NumPy array.\n\n"
            "Parameters\n"
            "----------\n"
            "key : str\n"
            "    Token to look up.\n"
            "level : Optional[int]\n"
            "    Optional Matryoshka prefix length. If provided, returns the\n"
            "    prefix of length ``level``. If ``None``, returns the full\n"
            "    vector (``vector_size``)."
        ),
    }.items():
        try:
            getattr(KeyedVectors, name).__doc__ = doc
        except Exception:
            # Some built-in descriptors may not allow docstring assignment
            pass

    # Word2Vec class and methods
    try:
        Word2Vec.__doc__ = (
            "Train Word2Vec models with optional Matryoshka levels.\n\n"
            "This class mirrors the common gensim API while delegating\n"
            "heavy lifting to a Rust backend for performance."
        )
    except Exception:
        pass

    # __init__ may or may not expose a descriptor that accepts docstrings
    try:
        Word2Vec.__init__.__doc__ = (
            "Initialize a Word2Vec model.\n\n"
            "Parameters\n"
            "----------\n"
            "sentences : Optional[Iterable[Sequence[str]]]\n"
            "    Optional training corpus provided at construction.\n"
            "vector_size : int\n"
            "    Dimensionality of word vectors.\n"
            "window : int\n"
            "    Maximum distance between the current and predicted word.\n"
            "min_count : int\n"
            "    Ignore tokens with total frequency lower than this.\n"
            "max_final_vocab : Optional[int]\n"
            "    Limit final vocabulary size after pruning (if provided).\n"
            "workers : int\n"
            "    Number of worker threads for training.\n"
            "negative : int\n"
            "    Number of negative samples (0 disables NS).\n"
            "sg : int\n"
            "    1 for skip-gram; 0 for CBOW.\n"
            "hs : int\n"
            "    1 to use hierarchical softmax.\n"
            "cbow_mean : int\n"
            "    Use mean (1) or sum (0) for CBOW context representation.\n"
            "levels : Optional[List[int]]\n"
            "    Matryoshka prefix lengths (e.g., ``[d//4, d//2, d]``). If\n"
            "    ``None``, trains a single-level model."
        )
    except Exception:
        pass

    for name, doc in {
        "load": (
            "Load a previously saved model.\n\n"
            "Parameters\n"
            "----------\n"
            "path : str\n"
            "    Path passed to ``save`` previously.\n\n"
            "Returns\n"
            "-------\n"
            "Word2Vec\n"
        ),
        "save": ("Save the full model to disk (training state + vectors)."),
        "train": (
            "Train on an iterable of tokenized sentences.\n\n"
            "Parameters\n"
            "----------\n"
            "corpus_iterable : Iterable[Sequence[str]]\n"
            "    The corpus can be a list of lists of tokens, but for larger\n"
            "    corpora consider streaming from disk/network to limit RAM usage.\n"
            "total_examples : Optional[int]\n"
            "    Total number of sentences per epoch; improves progress and\n"
            "    learning rate scheduling.\n"
            "epochs : Optional[int]\n"
            "    Number of passes over the corpus."
        ),
    }.items():
        try:
            getattr(Word2Vec, name).__doc__ = doc
        except Exception:
            pass

    # Property docstring for wv
    try:
        Word2Vec.wv.__doc__ = (
            "Return a ``KeyedVectors`` view of the model's learned vectors.\n\n"
            "Use this for inference-time operations such as indexing a word,\n"
            "retrieving vectors (optionally with a Matryoshka ``level``),\n"
            "and computing similarities."
        )
    except Exception:
        pass


# Best-effort docstring injection at import time
_inject_docs()
