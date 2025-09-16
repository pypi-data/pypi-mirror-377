import numpy
import pytest

try:
    import PyMca5
except ImportError:
    PyMca5 = None
from silx.io import h5py_utils
from silx.io.url import DataUrl

from est.core.io import read_from_input_information
from est.io.information import InputInformation
from est.io.utils.ascii import build_ascii_data_url
from est.io.utils.ascii import split_ascii_url


@pytest.mark.skipif(PyMca5 is None, reason="PyMca5 is not installed")
def test_input_information(filename_cu_from_pymca):
    """Test providing urls to spec files"""
    input_information = InputInformation(
        channel_url=build_ascii_data_url(
            file_path=filename_cu_from_pymca,
            scan_title=None,
            col_name="Column 1",
            data_slice=None,
        ),
        spectra_url=build_ascii_data_url(
            file_path=filename_cu_from_pymca,
            scan_title=None,
            col_name="Column 2",
            data_slice=None,
        ),
    )
    xas_obj = read_from_input_information(input_information)
    assert xas_obj.energy is not None
    assert xas_obj.spectra.data.flat[0] is not None


def test_spec_url():
    """simple test of the spec url function class"""
    file_path = "test.dat"
    scan_title = "1.1"
    col_name = "energy"
    data_slice = None
    url = build_ascii_data_url(
        file_path=file_path,
        scan_title=scan_title,
        col_name=col_name,
        data_slice=data_slice,
    )
    assert isinstance(url, DataUrl)
    assert split_ascii_url(url) == {
        "file_path": file_path,
        "scan_title": scan_title,
        "col_name": col_name,
        "data_slice": data_slice,
    }


@pytest.mark.skipif(PyMca5 is None, reason="PyMca5 is not installed")
def test_input_information_from_h5(hdf5_filename_cu_from_pymca):
    energy_url = DataUrl(
        f"silx://{hdf5_filename_cu_from_pymca}::/1.1/measurement/energy"
    )
    with h5py_utils.open_item(energy_url.file_path(), energy_url.data_path()) as dset:
        energy = dset[()]

    mu_url = DataUrl(f"silx://{hdf5_filename_cu_from_pymca}::/1.1/measurement/mu")
    with h5py_utils.open_item(mu_url.file_path(), mu_url.data_path()) as dset:
        mu = dset[()]

    I0_url = mu_url
    I0 = mu

    input_information = InputInformation(
        channel_url=energy_url, spectra_url=mu_url, I0_url=I0_url
    )
    xas_obj = read_from_input_information(input_information)

    sp = xas_obj.get_spectrum(0, 0)
    numpy.testing.assert_allclose(sp.energy, energy)
    numpy.testing.assert_allclose(sp.mu, mu)
    numpy.testing.assert_allclose(sp.I0, I0)
