import pytest

from est.core.types import XASObject

try:
    import larch
except ImportError:
    larch = None
else:
    from est.core.process.larch.autobk import process_spectr_autobk
    from est.core.process.larch.xftf import larch_xftf
    from est.core.process.larch.xftf import process_spectr_xftf


@pytest.mark.skipif(larch is None, reason="xraylarch not installed")
def test_single_spectrum(spectrum_cu_from_larch):
    """Make sure computation on one spectrum is valid"""
    configuration = {
        "window": "hanning",
        "kweight": 2,
        "kmin": 3,
        "kmax": 13,
        "dk": 1,
    }
    # for xftf we need to compute pre edge before
    process_spectr_autobk(spectrum_cu_from_larch, configuration={}, overwrite=True)
    assert hasattr(spectrum_cu_from_larch, "k")
    assert hasattr(spectrum_cu_from_larch, "chi")

    process_spectr_xftf(spectrum_cu_from_larch, configuration, overwrite=True)
    assert hasattr(spectrum_cu_from_larch, "chir_re")
    assert hasattr(spectrum_cu_from_larch, "chir_im")
    assert hasattr(spectrum_cu_from_larch, "chir")
    assert hasattr(spectrum_cu_from_larch, "chir_mag")


@pytest.fixture()
def xas_object(spectrum_cu_from_larch):
    configuration = {"z": 29}
    process_spectr_autobk(spectrum_cu_from_larch, configuration={}, overwrite=True)
    xas_object = XASObject(
        spectra=(spectrum_cu_from_larch,),
        energy=spectrum_cu_from_larch.energy,
        dim1=1,
        dim2=1,
        configuration=configuration,
    )
    # for xftf we need to compute pre edge before
    spectrum = xas_object.spectra.data.flat[0]
    assert hasattr(spectrum, "k")
    assert hasattr(spectrum, "chi")
    return xas_object


@pytest.mark.skipif(larch is None, reason="xraylarch not installed")
def test_multiple_spectra(xas_object):
    """Make sure computation on spectra is valid (n spectrum)"""
    res = larch_xftf(xas_object)
    assert isinstance(res, XASObject)
    spectrum = res.spectra.data.flat[0]
    assert hasattr(spectrum, "chir_re")
    assert hasattr(spectrum, "chir_im")
    assert hasattr(spectrum, "chir")
    assert hasattr(spectrum, "chir_mag")


@pytest.mark.skipif(larch is None, reason="xraylarch not installed")
def test_multiple_spectra_asdict(xas_object):
    """Make sure computation on spectra is valid (n spectrum)"""
    res = larch_xftf(xas_object.to_dict())
    assert isinstance(res, XASObject)
    spectrum = res.spectra.data.flat[0]
    assert hasattr(spectrum, "chir_re")
    assert hasattr(spectrum, "chir_im")
    assert hasattr(spectrum, "chir")
    assert hasattr(spectrum, "chir_mag")
