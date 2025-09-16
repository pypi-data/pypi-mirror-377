import h5py
import numpy
from silx.io.url import DataUrl

from est.core.io import read_from_url
from est.core.process.roi import xas_roi
from est.tests.data import example_spectra


def test_roi(tmpdir):
    """Test output of the roi process"""
    energy, spectra = example_spectra(shape=(16, 100, 30))
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

    original_spectra = xas_obj.spectra.as_ndarray("mu").copy()
    assert original_spectra.shape == (16, 100, 30)
    res_xas_obj = xas_roi(
        xas_obj,
        roi_origin=(20, 50),
        roi_size=(10, 20),
    )
    assert res_xas_obj.n_spectrum == 20 * 10
    reduces_spectra = res_xas_obj.spectra.as_ndarray("mu").copy()
    assert reduces_spectra.shape == (16, 20, 10)
    numpy.testing.assert_array_equal(original_spectra[:, 50:70, 20:30], reduces_spectra)
