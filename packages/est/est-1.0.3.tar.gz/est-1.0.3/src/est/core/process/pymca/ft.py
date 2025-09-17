"""wrapper to pymca `ft` process"""

import logging
from importlib.metadata import version as get_version
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Union

import numpy
from PyMca5.PyMcaPhysics.xas.XASClass import XASClass

from est.core.process.process import Process
from est.core.types import Spectrum
from est.core.types import XASObject

_logger = logging.getLogger(__name__)


def process_spectr_ft(
    spectrum: Spectrum,
    configuration: Dict[str, Any],
    overwrite: bool = True,
    callbacks: Optional[Sequence[Callable[[], None]]] = None,
) -> Spectrum:
    """
    :param spectrum: spectrum to process.
    :param configuration: configuration of the pymca normalization.
    :param overwrite: `False` if we want to return a new Spectrum instance.
    :param callbacks: callbacks to execute after processing.
    :return: processed spectrum.
    """
    assert isinstance(spectrum, Spectrum)
    _logger.debug(
        "start fourier transform on spectrum (%s, %s)", spectrum.x, spectrum.y
    )

    if spectrum.energy is None or spectrum.mu is None:
        _logger.error("Energy and or Mu is/are not specified, unable to compute exafs")
        return None

    pymca_xas = XASClass()
    if configuration is not None:
        pymca_xas.setConfiguration(configuration)
    pymca_xas.setSpectrum(energy=spectrum.energy, mu=spectrum.mu)

    if spectrum.chi is None:
        _logger.warning(
            "exafs has not been processed yet, unable to process fourier transform"
        )
        return None

    if "EXAFSNormalized" not in spectrum.pymca_dict:
        _logger.warning("ft window need to be defined first")
        return None

    cleanMu = spectrum.chi
    kValues = spectrum.k

    dataSet = numpy.zeros((cleanMu.size, 2), float)
    dataSet[:, 0] = kValues
    dataSet[:, 1] = cleanMu

    set2 = dataSet.copy()
    set2[:, 1] = spectrum.pymca_dict["EXAFSNormalized"]

    k_min = spectrum.pymca_dict.get("KMin", spectrum.k.max())
    k_max = spectrum.pymca_dict.get("KMax", spectrum.k.min())

    # remove points with k<2
    goodi = (set2[:, 0] >= k_min) & (set2[:, 0] <= k_max)
    set2 = set2[goodi, :]

    if set2.size == 0:
        ft = {"FTImaginary": numpy.nan, "FTIntensity": numpy.nan, "FTRadius": numpy.nan}
    else:
        ft = pymca_xas.fourierTransform(
            set2[:, 0],
            set2[:, 1],
            kMin=spectrum.pymca_dict["KMin"],
            kMax=spectrum.pymca_dict["KMax"],
        )
        assert "FTIntensity" in ft
        assert "FTRadius" in ft
        assert ft["FTRadius"] is not None
        assert ft["FTIntensity"] is not None
    if callbacks:
        for callback in callbacks:
            callback()

    if not overwrite:
        spectrum = Spectrum.from_dict(spectrum.to_dict())

    spectrum.ft = ft

    return spectrum


def pymca_ft(xas_obj: Union[XASObject, dict], **optional_inputs) -> Optional[XASObject]:
    process = PyMca_ft(inputs={"xas_obj": xas_obj, **optional_inputs})
    process.run()
    return process.get_output_value("xas_obj", None)


class PyMca_ft(
    Process,
    input_names=["xas_obj"],
    optional_input_names=["ft"],
    output_names=["xas_obj"],
):
    """Fourier transform of the XAS fine-structure."""

    def set_properties(self, properties):
        if "_pymcaSettings" in properties:
            self._settings = properties["_pymcaSettings"]

    def run(self):
        xas_obj = self.getXasObject(xas_obj=self.inputs.xas_obj)

        if self.inputs.ft:
            self.setConfiguration(self.inputs.ft)
            xas_obj.configuration["FT"] = self.inputs.ft

        self._advancement.reset(max_=xas_obj.n_spectrum)
        self._advancement.startProcess()
        self._pool_process(xas_obj=xas_obj)
        self._advancement.endProcess()
        assert hasattr(xas_obj.spectra.data.flat[0], "ft")
        assert hasattr(xas_obj.spectra.data.flat[0].ft, "intensity")
        assert hasattr(xas_obj.spectra.data.flat[0].ft, "imaginary")
        self.outputs.xas_obj = xas_obj

    def _pool_process(self, xas_obj: XASObject):
        n_s = len(xas_obj.spectra.data.flat)
        for i_s, spectrum in enumerate(xas_obj.spectra):
            process_spectr_ft(
                spectrum=spectrum,
                configuration=xas_obj.configuration,
                callbacks=self.callbacks,
                overwrite=True,
            )
            self.progress = i_s / n_s * 100.0

    def definition(self) -> str:
        return "fourier transform"

    def program_version(self) -> str:
        return get_version("PyMca5")

    @staticmethod
    def program_name() -> str:
        return "pymca_ft"
