from __future__ import annotations

import pytest

from word2vec_matryoshka import KeyedVectors, Word2Vec


def test_missing_word_raises():
    m = Word2Vec(vector_size=8)
    with pytest.raises(KeyError):
        _ = m.wv["__unknown__"]


def test_kv_load_accepts_mmap(tmp_path):
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    base = tmp_path / "kv"
    m.wv.save(str(base))
    # should accept mmap kw and not crash
    kv = KeyedVectors.load(str(base), mmap="r")
    _ = kv["a"]


def test_most_similar_missing_word_inmemory():
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    with pytest.raises(KeyError):
        _ = m.wv.most_similar("__unknown__", topn=3)


def test_most_similar_missing_word_memmap(tmp_path):
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    base = tmp_path / "kv"
    m.wv.save(str(base))
    kv = KeyedVectors.load(str(base), mmap="r")
    with pytest.raises(KeyError):
        _ = kv.most_similar("__unknown__", topn=3)


def test_kv_load_shape_mismatch_raises(tmp_path):
    import json
    import numpy as np

    base = tmp_path / "bad"
    # vocab 3 rows
    (tmp_path / "bad.vocab.json").write_text(json.dumps(["a", "b", "c"]))
    # npy only 2 rows -> mismatch
    np.save(str(base) + ".npy", np.zeros((2, 4), dtype=np.float32))

    with pytest.raises(ValueError):
        _ = KeyedVectors.load(str(base))
    with pytest.raises(ValueError):
        _ = KeyedVectors.load(str(base), mmap="r")


def test_kv_load_mmap_r_plus_supported(tmp_path):
    m = Word2Vec(vector_size=8, min_count=1)
    m.train([["a", "b"]], total_examples=1, epochs=1)
    base = tmp_path / "kv_rplus"
    m.wv.save(str(base))
    # 'r+' should be accepted and treated as read-only mmap
    kv = KeyedVectors.load(str(base), mmap="r+")
    assert kv.get_vector("a").shape[0] == 8


def test_npy_wrong_dtype_or_fortran_raises(tmp_path):
    import json
    import numpy as np

    # dtype mismatch: float64
    base = tmp_path / "bad_dtype"
    (tmp_path / "bad_dtype.vocab.json").write_text(json.dumps(["a", "b"]))
    np.save(str(base) + ".npy", np.zeros((2, 4), dtype=np.float64))
    with pytest.raises(ValueError):
        _ = KeyedVectors.load(str(base))
    with pytest.raises(ValueError):
        _ = Word2Vec.load(str(base))

    # Fortran order True
    base2 = tmp_path / "bad_fortran"
    (tmp_path / "bad_fortran.vocab.json").write_text(json.dumps(["a", "b"]))
    arrF = np.asfortranarray(np.zeros((2, 4), dtype=np.float32))
    np.save(str(base2) + ".npy", arrF)
    with pytest.raises(ValueError):
        _ = KeyedVectors.load(str(base2))
    with pytest.raises(ValueError):
        _ = Word2Vec.load(str(base2))


def test_npy_long_header_parsing(tmp_path):
    import json
    import numpy as np
    import struct

    def write_npy_long_header(path: str, rows: int, cols: int) -> None:
        magic = b"\x93NUMPY" + bytes([1, 0])
        dict_str = (
            "{'descr': '<f4', 'fortran_order': False, "
            f"'shape': ({rows}, {cols})}}"
        )
        # Pad header to exceed 512 bytes total (10 bytes pre + 2 bytes len + header)
        header = dict_str.encode("ascii")
        # Compute padding for 16-byte alignment (as per NPY v1.0)
        header_len_pos = 10  # magic(6)+ver(2)+hlen(2)
        unpadded_len_with_newline = len(header) + 1
        total_len = header_len_pos + 2 + unpadded_len_with_newline
        pad = (16 - (total_len % 16)) % 16
        header += b" " * pad + b"\n"
        # If still short, add extra padding up to >512 total
        while header_len_pos + 2 + len(header) <= 520:
            header = b" " + header
        hlen = struct.pack("<H", len(header))
        payload = (np.zeros((rows, cols), dtype=np.float32)).tobytes()
        with open(path, "wb") as f:
            f.write(magic)
            f.write(hlen)
            f.write(header)
            f.write(payload)

    base = tmp_path / "longhdr"
    (tmp_path / "longhdr.vocab.json").write_text(json.dumps(["a", "b"]))
    write_npy_long_header(str(base) + ".npy", 2, 4)

    # Should load fine (header > 512B)
    kv = KeyedVectors.load(str(base), mmap="r")
    assert kv.get_vector("a").shape[0] == 4
