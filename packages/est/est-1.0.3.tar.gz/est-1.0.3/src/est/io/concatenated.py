from __future__ import annotations

import logging
from typing import Any
from typing import Dict
from typing import Tuple

import numpy
import pint

from est import settings
from est.core.monotonic import split_piecewise_monotonic
from est.core.sections import split_section_size
from est.io.information import InputInformation
from est.io.utils.read import get_data_from_url

_logger = logging.getLogger(__name__)


def read_concatenated_xas(
    information: InputInformation, timeout: float = settings.DEFAULT_READ_TIMEOUT
) -> Tuple[numpy.ndarray, pint.Quantity, Dict[str, Any]]:
    """
    Method to read spectra acquired with the energy ramping up and down, with any number of repetitions.

    When the scan is uni-directional, the ramp is always up. When the scan is bi-directional the ramp is
    alternating up and down.

    The spectra are then interpolated to produce a 3D data aray (nb_energy_pts, nb_of_ramps, 1).

    Limitations: the original spectra and energy datasets must be 1D.
    """
    raw_spectra = get_data_from_url(information.spectra_url, retry_timeout=timeout)
    raw_energy = get_data_from_url(information.channel_url, retry_timeout=timeout)
    config_url = information.config_url
    if config_url:
        config = get_data_from_url(config_url, retry_timeout=timeout)
    else:
        config = None

    section_size = information.concatenated_spectra_section_size
    if section_size:
        ramp_slices = split_section_size(raw_energy, section_size)
    else:
        ramp_slices = split_piecewise_monotonic(raw_energy)

    if not ramp_slices:
        if len(raw_energy) >= 10:
            raise RuntimeError("Not enough data to detect monotonic slices.")
        _logger.warning(
            "Not enough data to detect monotonic slices. Less than 10 data points so return empty result.",
        )
        ramp_slices = [slice(0, 0)]

    energy = raw_energy[ramp_slices[0]]

    if information.skip_concatenated_n_spectra:
        ramp_slices = ramp_slices[information.skip_concatenated_n_spectra :]

    interpolated_spectra = numpy.zeros(
        (len(energy), len(ramp_slices), 1), dtype=raw_spectra.dtype
    )
    for i, ramp_slice in enumerate(ramp_slices):
        raw_energy_i = raw_energy[ramp_slice]
        if raw_energy_i.size == 0:
            continue
        raw_spectrum_i = raw_spectra[ramp_slice]

        if len(raw_energy_i) != len(raw_spectrum_i):
            n = min(len(raw_energy_i), len(raw_spectrum_i))
            raw_energy_i = raw_energy_i[:n]
            raw_spectrum_i = raw_spectrum_i[:n]

        if information.trim_concatenated_n_points:
            raw_spectrum_i[: information.trim_concatenated_n_points] = numpy.nan
            raw_spectrum_i[-information.trim_concatenated_n_points :] = numpy.nan

        interpolated_spectra[:, i, 0] = numpy.interp(
            energy,
            raw_energy_i,
            raw_spectrum_i,
            left=numpy.nan,
            right=numpy.nan,
        )

    return interpolated_spectra, energy * information.energy_unit, config
