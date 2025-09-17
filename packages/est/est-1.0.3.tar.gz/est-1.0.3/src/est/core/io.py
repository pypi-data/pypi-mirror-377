"""simple helper functions to insure a simple link with the `io` module (and XASObject)"""

from __future__ import annotations

import logging
from typing import Optional
from typing import Union

from silx.io.url import DataUrl

from est import settings
from est.core.types import XASObject
from est.core.types import dimensions as dimensions_mod
from est.io import read_xas
from est.io import write_xas
from est.io.concatenated import read_concatenated_xas
from est.io.information import InputInformation
from est.io.utils.ascii import build_ascii_data_url
from est.units import ur

_logger = logging.getLogger(__name__)

DEFAULT_SPECTRA_PATH = "/data/NXdata/data"

DEFAULT_CHANNEL_PATH = "/data/NXdata/Channel"

DEFAULT_CONF_PATH = "/configuration"


def read_from_input_information(
    information: InputInformation, timeout: float = settings.DEFAULT_READ_TIMEOUT
) -> XASObject:
    if information.is_concatenated:
        spectra, energy, configuration = read_concatenated_xas(information, timeout)
    else:
        spectra, energy, configuration = read_xas(information, timeout)

    xas_obj = XASObject(spectra=spectra, energy=energy, configuration=configuration)
    I0_url = information.I0_url
    if I0_url:
        xas_obj.attach_3d_array("I0", I0_url)

    I1_url = information.I0_url
    if I1_url:
        xas_obj.attach_3d_array("I1", I1_url)

    I2_url = information.I2_url
    if I2_url:
        xas_obj.attach_3d_array("I2", I2_url)

    mu_ref_url = information.mu_ref_url
    if mu_ref_url:
        xas_obj.attach_3d_array("mu_ref", mu_ref_url)

    return xas_obj


def read_from_url(
    spectra_url: DataUrl,
    channel_url: DataUrl,
    dimensions: Optional[dimensions_mod.DimensionsType] = None,
    config_url: DataUrl | None = None,
    energy_unit=ur.eV,
    I0_url: DataUrl | None = None,
    I1_url: DataUrl | None = None,
    I2_url: DataUrl | None = None,
    mu_ref_url: DataUrl | None = None,
    is_concatenated: bool = False,
    trim_concatenated_n_points: int = 0,
    skip_concatenated_n_spectra: int = 0,
    concatenated_spectra_section_size: int = 0,
    timeout: float = settings.DEFAULT_READ_TIMEOUT,
) -> XASObject:
    """

    :param DataUrl spectra_url: data url to the spectra
    :param DataUrl channel_url: data url to the channel / energy
    :param DataUrl config_url: data url to the process configuration
    :param dimensions: way the data has been stored.
                       Usually is (X, Y, channels) of (Channels, Y, X).
                       If None, by default is considered to be (Z, Y, X)
    :type: tuple
    :return:
    :rtype: XASObject
    """
    input_information = InputInformation(
        spectra_url=spectra_url,
        channel_url=channel_url,
        config_url=config_url,
        dimensions=dimensions,
        energy_unit=energy_unit,
        I0_url=I0_url,
        I1_url=I1_url,
        I2_url=I2_url,
        mu_ref_url=mu_ref_url,
        is_concatenated=is_concatenated,
        trim_concatenated_n_points=trim_concatenated_n_points,
        skip_concatenated_n_spectra=skip_concatenated_n_spectra,
        concatenated_spectra_section_size=concatenated_spectra_section_size,
    )
    return read_from_input_information(input_information, timeout=timeout)


def read_from_ascii(
    file_path: str,
    columns_names: dict,
    energy_unit=ur.eV,
    dimensions: Optional[dimensions_mod.DimensionsType] = None,
    scan_title: Optional[str] = None,
    timeout: float = settings.DEFAULT_READ_TIMEOUT,
) -> XASObject:
    """
    :param file_path: path to the file containing the spectra. Must be a
                          .dat file that pymca can handle
    :param columns_names: name of the columns
    :param dimensions: dimensions of the input data. Can
                             be (X, Y) or (Y, X)
    :return XasObject created from the input
    """
    if file_path in (None, ""):
        raise ValueError("Please supply a file path !")

    input_information = InputInformation(
        spectra_url=build_ascii_data_url(
            file_path=file_path,
            col_name=columns_names["mu"],
            scan_title=scan_title,
        ),
        channel_url=build_ascii_data_url(
            file_path=file_path,
            col_name=columns_names["energy"],
            scan_title=scan_title,
        ),
        energy_unit=energy_unit,
        dimensions=dimensions,
    )
    return read_from_input_information(input_information, timeout=timeout)


def dump_xas(h5_file: str, xas_obj: Union[dict, XASObject]) -> None:
    """
    Save a XASObject in an hdf5 file.
    """
    if isinstance(xas_obj, dict):
        xas_obj = XASObject.from_dict(xas_obj)
    if not isinstance(xas_obj, XASObject):
        raise TypeError(str(type(xas_obj)))

    if not h5_file:
        _logger.warning("no output file defined, please give path to the output file")
        h5_file = input()

    _logger.info("dump xas obj to '%s'", h5_file)

    write_xas(
        h5_file=h5_file,
        energy=xas_obj.energy,
        mu=xas_obj.absorbed_beam(),
        entry=xas_obj.entry,
    )
