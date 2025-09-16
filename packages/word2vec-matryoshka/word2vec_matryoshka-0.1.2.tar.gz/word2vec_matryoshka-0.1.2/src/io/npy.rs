// Minimal NPY v1.0 read/write helpers used for persisting vectors.
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Write a Fortran-order=False, little-endian float32 NPY array of shape (rows, cols).
pub fn write_npy(path: &str, rows: usize, cols: usize, data: &[f32]) -> PyResult<()> {
    use std::io::BufWriter;
    use std::io::Write;
    let file = std::fs::File::create(path)
        .map_err(|e| PyValueError::new_err(format!("failed to create {}: {}", path, e)))?;
    let mut file = BufWriter::new(file);
    // NPY v1.0 header
    let magic = b"\x93NUMPY";
    file.write_all(magic).unwrap();
    file.write_all(&[1u8, 0u8]).unwrap(); // version 1.0
                                          // Dict without trailing comma, newline appended after padding
    let dict = format!(
        "{{'descr': '<f4', 'fortran_order': False, 'shape': ({}, {})}}",
        rows, cols
    );
    // pad to 16-byte alignment including header len field (2 bytes), with terminating newline
    let header_len_pos = 10usize; // 6 magic + 2 ver + 2 len
    let mut header = dict.into_bytes();
    // Compute padding so that 10 + 2 + (header.len + 1 newlines + pad) is divisible by 16
    let unpadded_len_with_newline = header.len() + 1;
    let total_len = header_len_pos + 2 + unpadded_len_with_newline;
    let pad = (16 - (total_len % 16)) % 16;
    // Avoid clippy's manual_repeat_n: just resize with spaces
    if pad > 0 {
        let new_len = header.len() + pad;
        header.resize(new_len, b' ');
    }
    header.push(b'\n');
    let hlen: u16 = header.len() as u16;
    file.write_all(&hlen.to_le_bytes()).unwrap();
    file.write_all(&header).unwrap();
    // Raw little-endian data payload
    if data.len() != rows * cols {
        return Err(PyValueError::new_err("npy write: data size mismatch"));
    }
    let bytes: &[u8] =
        unsafe { core::slice::from_raw_parts(data.as_ptr() as *const u8, data.len() * 4) };
    file.write_all(bytes).unwrap();
    Ok(())
}

/// Return the total header length (including magic and header bytes) for NPY v1.0.
pub fn npy_header_len(buf: &[u8]) -> PyResult<usize> {
    if buf.len() < 10 || &buf[0..6] != b"\x93NUMPY" {
        return Err(PyValueError::new_err("invalid npy magic"));
    }
    let major = buf[6];
    let minor = buf[7];
    if major != 1 || minor != 0 {
        return Err(PyValueError::new_err("unsupported npy version"));
    }
    let hlen = u16::from_le_bytes([buf[8], buf[9]]) as usize;
    Ok(10 + hlen)
}

/// Parse the (rows, cols) shape from an on-disk NPY v1.0 header.
pub fn read_npy_shape(path: &str) -> PyResult<(usize, usize)> {
    use std::io::BufReader;
    use std::io::Read;
    let f = std::fs::File::open(path)
        .map_err(|e| PyValueError::new_err(format!("failed to open {}: {}", path, e)))?;
    let mut f = BufReader::new(f);
    let mut head = vec![0u8; 512];
    let n = f.read(&mut head).unwrap_or(0);
    if n < 10 || &head[0..6] != b"\x93NUMPY" {
        return Err(PyValueError::new_err("invalid npy magic"));
    }
    if head[6] != 1 || head[7] != 0 {
        return Err(PyValueError::new_err("unsupported npy version"));
    }
    let hlen = u16::from_le_bytes([head[8], head[9]]) as usize;
    let start = 10;
    let end = start + hlen;
    if end > n {
        return Err(PyValueError::new_err("short npy header"));
    }
    let header_str = std::str::from_utf8(&head[start..end])
        .map_err(|_| PyValueError::new_err("invalid header"))?;
    // very naive parse: find "shape": (rows, cols)
    let shape_pos = header_str
        .find("shape")
        .ok_or_else(|| PyValueError::new_err("no shape in header"))?;
    let open = header_str[shape_pos..]
        .find('(')
        .ok_or_else(|| PyValueError::new_err("bad shape"))?
        + shape_pos;
    let close = header_str[open..]
        .find(')')
        .ok_or_else(|| PyValueError::new_err("bad shape"))?
        + open;
    let inside = &header_str[open + 1..close];
    let parts: Vec<&str> = inside
        .split(',')
        .map(|s| s.trim())
        .filter(|s| !s.is_empty())
        .collect();
    if parts.len() < 2 {
        return Err(PyValueError::new_err("shape expects 2 dims"));
    }
    let rows: usize = parts[0]
        .parse()
        .map_err(|_| PyValueError::new_err("bad rows"))?;
    let cols: usize = parts[1]
        .parse()
        .map_err(|_| PyValueError::new_err("bad cols"))?;
    Ok((rows, cols))
}
