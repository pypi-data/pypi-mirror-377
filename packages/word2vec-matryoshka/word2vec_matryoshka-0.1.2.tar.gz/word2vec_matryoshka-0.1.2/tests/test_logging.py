from __future__ import annotations

import logging

from word2vec_matryoshka import Word2Vec, set_seed


def test_training_verbose_logging(caplog, capsys) -> None:
    # Arrange: capture INFO logs from our module logger
    caplog.set_level(logging.INFO, logger="word2vec_matryoshka")
    set_seed(123)

    # A small-but-nontrivial corpus to ensure we cross the 10ms reporting interval
    corpus = [["hello", "world"] for _ in range(4000)]

    m = Word2Vec(sentences=corpus, vector_size=16, window=2, min_count=1, workers=1)

    # Act: enable verbose logging with the minimal interval (10ms floor inside)
    m.train(corpus, epochs=1, verbose=True, progress_interval=0.01)

    # Assert: at least one gensim-like progress line was logged
    text = caplog.text or capsys.readouterr().err
    assert (
        (" PROGRESS at " in text or "PROGRESS: at " in text)
        and ", alpha " in text
        and " tokens/s" in text
    ), f"no progress log found; captured text: {text[:200]}..."


def test_verbose_defaults_override(caplog, capsys) -> None:
    # By default, configure capture for our logger
    caplog.set_level(logging.INFO, logger="word2vec_matryoshka")

    corpus = [["a", "b"] for _ in range(2000)]

    # verbose False at init: training without override should not log
    m = Word2Vec(sentences=corpus, vector_size=8, workers=1, verbose=False)
    caplog.clear()
    m.train(corpus, epochs=1)
    assert not any(rec.name == "word2vec_matryoshka" for rec in caplog.records)

    # override to True at train: should log
    caplog.clear()
    m.train(corpus, epochs=1, verbose=True, progress_interval=0.01)
    text = caplog.text or capsys.readouterr().err
    assert " PROGRESS at " in text or "PROGRESS: at " in text, (
        "expected progress logs when verbose=True override"
    )
