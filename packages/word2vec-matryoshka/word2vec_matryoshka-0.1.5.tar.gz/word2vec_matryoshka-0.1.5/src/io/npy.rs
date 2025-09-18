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
    file
        .write_all(magic)
        .map_err(|e| PyValueError::new_err(format!("write {}: magic: {}", path, e)))?;
    // version 1.0
    file
        .write_all(&[1u8, 0u8])
        .map_err(|e| PyValueError::new_err(format!("write {}: version: {}", path, e)))?;
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
    file
        .write_all(&hlen.to_le_bytes())
        .map_err(|e| PyValueError::new_err(format!("write {}: header-len: {}", path, e)))?;
    file
        .write_all(&header)
        .map_err(|e| PyValueError::new_err(format!("write {}: header-bytes: {}", path, e)))?;
    // Raw little-endian data payload
    if data.len() != rows * cols {
        return Err(PyValueError::new_err("npy write: data size mismatch"));
    }
    let bytes: &[u8] =
        unsafe { core::slice::from_raw_parts(data.as_ptr() as *const u8, data.len() * 4) };
    file
        .write_all(bytes)
        .map_err(|e| PyValueError::new_err(format!("write {}: payload: {}", path, e)))?;
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
    use std::io::Read;
    let mut f = std::fs::File::open(path)
        .map_err(|e| PyValueError::new_err(format!("failed to open {}: {}", path, e)))?;
    // Read magic (6), version (2), header length (2)
    let mut head10 = [0u8; 10];
    f.read_exact(&mut head10)
        .map_err(|_| PyValueError::new_err("short npy header"))?;
    if &head10[0..6] != b"\x93NUMPY" {
        return Err(PyValueError::new_err("invalid npy magic"));
    }
    if head10[6] != 1 || head10[7] != 0 {
        return Err(PyValueError::new_err("unsupported npy version"));
    }
    let hlen = u16::from_le_bytes([head10[8], head10[9]]) as usize;
    let mut header = vec![0u8; hlen];
    f.read_exact(&mut header)
        .map_err(|_| PyValueError::new_err("short npy header"))?;
    let header_str = std::str::from_utf8(&header)
        .map_err(|_| PyValueError::new_err("invalid header"))?;

    // Parse minimal dict fields: 'descr', 'fortran_order', 'shape'
    // descr: scan after the ':' following the key and capture the quoted string value
    let descr = {
        let key = "'descr'";
        let kpos = header_str
            .find(key)
            .ok_or_else(|| PyValueError::new_err("no descr in header"))?;
        let colon = header_str[kpos..]
            .find(':')
            .ok_or_else(|| PyValueError::new_err("bad descr"))?
            + kpos;
        let after = &header_str[colon + 1..];
        let q1_rel = after
            .find('\'')
            .ok_or_else(|| PyValueError::new_err("bad descr"))?;
        let q1 = colon + 1 + q1_rel;
        let q2_rel = header_str[q1 + 1..]
            .find('\'')
            .ok_or_else(|| PyValueError::new_err("bad descr"))?;
        let q2 = q1 + 1 + q2_rel;
        header_str[q1 + 1..q2].to_string()
    };
    let fortran_true: bool = {
        let key = "fortran_order";
        let kpos = header_str
            .find(key)
            .ok_or_else(|| PyValueError::new_err("no fortran_order in header"))?;
        let colon = header_str[kpos..]
            .find(':')
            .ok_or_else(|| PyValueError::new_err("bad fortran_order"))?
            + kpos;
        let after = header_str[colon + 1..].trim_start();
        after.starts_with("True")
    };

    // shape: (rows, cols)
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

    // Enforce dtype and order expectations
    if descr != "<f4" || fortran_true {
        return Err(PyValueError::new_err(format!(
            "npy expects C-order float32 ('<f4'), got descr='{}', fortran_order={}",
            descr,
            if fortran_true { "True" } else { "False" }
        )));
    }
    Ok((rows, cols))
}
