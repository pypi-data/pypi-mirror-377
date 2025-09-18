use pyo3::{pyfunction, Bound, PyAny, PyResult, Python};
use pepecore::real_size::{get_full_original_size, get_original_height_only, get_original_width_only};
use crate::structure::svec_traits::PySvec;

#[pyfunction(name = "real_hw")]
#[pyo3(signature = (img))]
pub fn real_hw<'py>(py: Python<'_>,img: Bound<'py, PyAny>)->PyResult<(usize,usize)>{
    let img = img.to_svec(py).unwrap();
    let (h,w) = py.allow_threads(|| get_full_original_size(&img));
    Ok((h,w))
}
#[pyfunction(name = "real_h")]
#[pyo3(signature = (img))]
pub fn real_h<'py>(py: Python<'_>,img: Bound<'py, PyAny>)->PyResult<usize>{
    let img = img.to_svec(py).unwrap();
    let h = py.allow_threads(|| get_original_height_only(&img));
    Ok(h)
}
#[pyfunction(name = "real_w")]
#[pyo3(signature = (img))]
pub fn real_w<'py>(py: Python<'_>,img: Bound<'py, PyAny>)->PyResult<usize>{
    let img = img.to_svec(py).unwrap();
    let w = py.allow_threads(|| get_original_width_only(&img));
    Ok(w)
}