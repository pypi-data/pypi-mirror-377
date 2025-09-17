import h5py
import pytest
from silx.io.url import DataUrl

from est.core.io import read_from_url
from est.core.types import XASObject
from est.tests.data import example_spectra

try:
    import PyMca5
except ImportError:
    PyMca5 = None
else:
    from est.core.process.pymca.normalization import pymca_normalization


@pytest.mark.skipif(PyMca5 is None, reason="PyMca5 is not installed")
def test_single_spectrum(spectrum_cu_from_pymca):
    """Make sure the process is processing correctly on a spectrum"""
    xas_obj = XASObject(
        spectra=(spectrum_cu_from_pymca,),
        energy=spectrum_cu_from_pymca.energy,
        dim1=1,
        dim2=1,
    )
    res_spectrum = xas_obj.spectra.data.flat[0]
    assert res_spectrum.normalized_energy is None
    assert res_spectrum.normalized_mu is None
    assert res_spectrum.post_edge is None
    pymca_normalization(xas_obj=xas_obj)
    assert xas_obj.normalized_energy is not None
    assert res_spectrum.normalized_energy is not None
    assert res_spectrum.normalized_mu is not None
    assert res_spectrum.post_edge is not None


@pytest.mark.skipif(PyMca5 is None, reason="PyMca5 is not installed")
def test_single_spectrum_asdict(spectrum_cu_from_pymca):
    """Make sure the process is processing correctly on a spectrum"""
    xas_obj = XASObject(
        spectra=(spectrum_cu_from_pymca,),
        energy=spectrum_cu_from_pymca.energy,
        dim1=1,
        dim2=1,
    )
    res_spectrum = xas_obj.spectra.data.flat[0]
    assert res_spectrum.normalized_energy is None
    assert res_spectrum.normalized_mu is None
    assert res_spectrum.post_edge is None
    xas_obj = pymca_normalization(xas_obj=xas_obj.to_dict())
    res_spectrum = xas_obj.spectra.data.flat[0]
    assert xas_obj.normalized_energy is not None
    assert res_spectrum.normalized_energy is not None
    assert res_spectrum.normalized_mu is not None
    assert res_spectrum.post_edge is not None


@pytest.mark.skipif(PyMca5 is None, reason="PyMca5 is not installed")
def test_multiple_spectra(tmpdir):
    """Make sure computation on spectra is valid (n spectrum)"""
    energy, spectra = example_spectra(shape=(256, 20, 10))
    spectra_path = "/data/NXdata/data"
    channel_path = "/data/NXdata/Channel"
    filename = str(tmpdir / "myfile.h5")
    with h5py.File(filename, "a") as f:
        f[spectra_path] = spectra
        f[channel_path] = energy

    xas_obj = read_from_url(
        spectra_url=DataUrl(file_path=filename, data_path=spectra_path, scheme="silx"),
        channel_url=DataUrl(file_path=filename, data_path=channel_path, scheme="silx"),
        dimensions=(2, 1, 0),
    )

    pymca_normalization(xas_obj=xas_obj)
    for spectrum in xas_obj.spectra.data.flat:
        assert spectrum.normalized_mu is not None
        assert spectrum.normalized_energy is not None
        assert spectrum.post_edge is not None
