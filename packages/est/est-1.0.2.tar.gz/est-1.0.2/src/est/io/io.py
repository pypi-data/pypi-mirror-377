import logging
from datetime import datetime
from typing import Optional
from typing import Union

import numpy
from silx.io.dictdump import dicttoh5
from silx.io.dictdump import dicttonx
from silx.io.h5py_utils import File as HDF5File
from silx.io.url import DataUrl
from silx.utils.enum import Enum

from est import settings
from est.core.types import Spectra
from est.core.types import dimensions as dimensions_mod
from est.io.information import InputInformation
from est.io.utils import get_ascii_data
from est.io.utils import get_data_from_url
from est.io.utils import get_est_data
from est.io.utils.ascii import split_ascii_url
from est.units import ur

_logger = logging.getLogger(__name__)


class InputType(Enum):
    ascii_spectrum = "ascii"  # single or multi scan, single spectrum
    hdf5_spectra = "hdf5"  # multi scan, multi spectra


def load_data(
    data_url: DataUrl,
    name: str,
    dimensions: dimensions_mod.DimensionsType,
    columns_names: Optional[dict] = None,
    energy_unit=ur.eV,
    timeout=settings.DEFAULT_READ_TIMEOUT,
) -> Union[None, dict, numpy.ndarray, Spectra]:
    """
    Load a specific data from a url. Manage the different scheme (silx, fabio,
    numpy, PyMca, xraylarch)

    :param data_url: silx DataUrl with path to the data
    :type: DataUrl
    :param str name: name of the data we want to load. Should be in
                    ('spectra', 'energy', 'configuration')
    :param Union[None,dict] columns_names: name of the column to pick for .dat
                                           files... Expect key 'mu' and
                                                    'energy' to be registered
    :return: data loaded
    :rtype: Union[None,dict,numpy.ndarray]
    """
    if data_url is None:
        return None
    assert isinstance(data_url, DataUrl)
    scheme = data_url.scheme().lower()

    if scheme in ("ascii", "spec", "pymca", "pymca5", "larch", "xraylarch"):
        return get_ascii_data(
            data_url, name, columns_names=columns_names, energy_unit=energy_unit
        )

    if scheme == "numpy":
        return _move_axes_to_standard(numpy.load(data_url.file_path()), dimensions)

    if scheme == "est":
        assert name == "spectra"
        spectra = get_est_data(data_url, retry_timeout=timeout)
        return Spectra(energy=spectra[0].energy, spectra=spectra)

    if not data_url.is_valid():
        _logger.warning("invalid url for %s: %s", name, data_url)
        return

    try:
        data = get_data_from_url(data_url, retry_timeout=timeout)
    except ValueError as e:
        _logger.error(e)
        return
    if name == "spectra":
        if data.ndim == 1:
            return data.reshape(data.shape[0], 1, 1)
        elif data.ndim == 3:
            return _move_axes_to_standard(data, dimensions=dimensions)
    return data


def _move_axes_to_standard(spectra, dimensions: dimensions_mod.DimensionsType):
    if isinstance(spectra, Spectra):
        spectra.data = dimensions_mod.transform_to_standard(spectra.data, dimensions)
    elif isinstance(spectra, numpy.ndarray):
        spectra = dimensions_mod.transform_to_standard(spectra, dimensions)
    return spectra


def read_xas(information: InputInformation, timeout=settings.DEFAULT_READ_TIMEOUT):
    """
    Read the given spectra, configuration... from the provided input
    Information


    :return: spectra, energy, configuration
    """
    _spectra_url = _get_url(original_url=information.spectra_url, name="spectra")
    _energy_url = _get_url(original_url=information.channel_url, name="energy")
    _config_url = information.config_url
    if type(_config_url) is str and _config_url == "":
        _config_url = None
    if not (_config_url is None or isinstance(_config_url, DataUrl)):
        raise TypeError("given input for configuration is invalid")

    # build column name
    columns_names = {}
    for url, col_name in zip(
        [information.spectra_url, information.channel_url, information.mu_ref_url],
        ["mu", "energy", "monitor"],
    ):
        if url is not None:
            columns_names[col_name] = split_ascii_url(url)["col_name"]
        else:
            columns_names[col_name] = None

    # this should be extractable and done in the InputInformation class
    spectra = load_data(
        _spectra_url,
        name="spectra",
        dimensions=information.dimensions,
        columns_names=columns_names,
        energy_unit=information.energy_unit,
        timeout=timeout,
    )
    energy = load_data(
        _energy_url,
        name="energy",
        dimensions=information.dimensions,
        columns_names=columns_names,
        energy_unit=information.energy_unit,
        timeout=timeout,
    )
    configuration = load_data(
        _config_url,
        name="configuration",
        dimensions=information.dimensions,
        columns_names=columns_names,
        energy_unit=information.energy_unit,
        timeout=timeout,
    )

    if energy is None:
        raise ValueError("Unable to load energy from {}".format(_energy_url))
    if not energy.ndim == 1:
        raise ValueError("Energy / channel is not 1D")
    if energy.shape[0] > spectra.shape[0]:
        energy = energy[: spectra.shape[0]]
        _logger.warning("energy has less value than spectra. Clip energy.")
    if not energy.shape[0] == spectra.shape[0]:
        _logger.warning(
            "Energy / channel and spectra dim1 have incoherent length (%s vs %s)"
            % (
                energy.shape[0],
                spectra.shape[0],
            )
        )
        if energy.shape[0] < spectra.shape[0]:
            spectra = spectra[: energy.shape[0]]
        else:
            energy = energy[: spectra.shape[0]]

    not_strictly_increasing = numpy.diff(energy) <= 0
    if not_strictly_increasing.any():
        _logger.warning("Energy is not strictly increasing: sort data by energy")
        idx = numpy.argsort(energy)
        energy = energy[idx]
        spectra = spectra[idx]
        has_duplicates = numpy.diff(energy) == 0
        if has_duplicates.any():
            _logger.warning("Energy has duplicate values: remove duplicates")
            energy, idx = numpy.unique(energy, return_index=True)
            spectra = spectra[idx]

    return spectra, energy * information.energy_unit, configuration


def _get_url(original_url, name):
    url_ = original_url
    if isinstance(url_, str):
        try:
            url_ = DataUrl(path=url_)
        except Exception:
            url_ = DataUrl(file_path=url_, scheme="PyMca")

    if not isinstance(url_, DataUrl):
        raise TypeError("given input for {} is invalid ({})".format(name, url_))
    return url_


def write_xas_proc(
    h5_file,
    entry,
    process,
    results,
    processing_order,
    data_path="/",
    overwrite=True,
):
    """
    Write a xas :class:`.Process` into .h5

    :param str h5_file: path to the hdf5 file
    :param str entry: entry name
    :param process: process executed
    :type: :class:`.Process`
    :param results: process result data
    :type: numpy.ndarray
    :param processing_order: processing order of treatment
    :type: int
    :param data_path: path to store the data
    :type: str
    """
    process_name = "xas_process_" + str(processing_order)
    # write the xasproc default information
    with HDF5File(h5_file, "a") as h5f:
        nx_entry = h5f.require_group("/".join((data_path, entry)))
        nx_entry.attrs["NX_class"] = "NXentry"

        nx_process = nx_entry.require_group(process_name)
        nx_process.attrs["NX_class"] = "NXprocess"
        if overwrite:
            for key in (
                "program",
                "version",
                "date",
                "processing_order",
                "class_instance",
                "ft",
            ):
                if key in nx_process:
                    del nx_process[key]
        nx_process["program"] = process.program_name()
        nx_process["version"] = process.program_version()
        nx_process["date"] = datetime.now().replace(microsecond=0).isoformat()
        nx_process["processing_order"] = numpy.int32(processing_order)
        _class = process.__class__
        nx_process["class_instance"] = ".".join((_class.__module__, _class.__name__))

        nx_data = nx_entry.require_group("data")
        nx_data.attrs["NX_class"] = "NXdata"
        nx_data.attrs["signal"] = "data"
        nx_process_path = nx_process.name

    if isinstance(results, numpy.ndarray):
        data_ = {"data": results}
    else:
        data_ = results

    def get_interpretation(my_data):
        """Return hdf5 attribute for this type of data"""
        if isinstance(my_data, numpy.ndarray):
            if my_data.ndim == 1:
                return "spectrum"
            elif my_data.ndim in (2, 3):
                return "image"
        return None

    # save results
    def save_key(key_path, value, attrs):
        """Save the given value to the associated path. Manage numpy arrays
        and dictionaries.
        """
        if attrs is not None:
            assert value is None, "can save value or attribute not both"
        if value is not None:
            assert attrs is None, "can save value or attribute not both"
        key_path = key_path.replace(".", "/")
        # save if is dict
        if isinstance(value, dict):
            h5_path = "/".join((entry, process_name, key_path))
            dicttoh5(
                value,
                h5file=h5_file,
                h5path=h5_path,
                update_mode="replace",
                mode="a",
            )
        else:
            with HDF5File(h5_file, "a") as h5f:
                nx_process = h5f.require_group(nx_process_path)
                if attrs is None:
                    if key_path in nx_process:
                        del nx_process[key_path]
                    try:
                        nx_process[key_path] = value
                    except TypeError as e:
                        _logger.warning(
                            "Unable to write at {} reason is {}"
                            "".format(str(key_path), str(e))
                        )
                    else:
                        interpretation = get_interpretation(value)
                        if interpretation:
                            nx_process[key_path].attrs[
                                "interpretation"
                            ] = interpretation
                else:
                    for key, value in attrs.items():
                        try:
                            nx_process[key_path].attrs[key] = value
                        except Exception as e:
                            _logger.warning(e)

    for key, value in data_.items():
        if isinstance(key, tuple):
            key_path = "/".join(("results", key[0]))
            save_key(key_path=key_path, value=None, attrs={key[1]: value})
        else:
            key_path = "/".join(("results", str(key)))
            save_key(key_path=key_path, value=value, attrs=None)

    if process.getConfiguration() is not None:
        h5_path = "/".join((nx_process_path, "configuration"))
        dicttoh5(
            process.getConfiguration(),
            h5file=h5_file,
            h5path=h5_path,
            update_mode="add",
            mode="a",
        )


def write_xas(
    h5_file,
    entry,
    energy,
    mu,
    sample=None,
    start_time=None,
    data_path="/",
    title=None,
    definition=None,
    overwrite=True,
):
    """
    Write raw date in nexus format

    :param str h5_file: path to the hdf5 file
    :param str entry: entry name
    :param sample: definition of the sample
    :type: :class:`.Sample`
    :param energy: beam energy (1D)
    :type: numpy.ndarray
    :param mu: beam absorption (2D)
    :type: numpy.ndarray
    :param start_time:
    :param str data_path:
    :param str title: experiment title
    :param str definition: experiment definition
    """
    h5path = "/".join((data_path, entry))
    nx_dict = {
        "@NX_class": "NXentry",
        "monochromator": {
            "@NX_class": "NXmonochromator",
            "energy": energy,
            "energy@interpretation": "spctrum",
            "energy@NX_class": "NXdata",
            "energy@unit": "eV",
        },
        "absorbed_beam": {
            "@NX_class": "NXdetector",
            "data": mu,
            "data@interpretation": "image",
            "data@NX_class": "NXdata",
        },
        "data": {
            "@NX_class": "NXdata",
            ">energy": "../monochromator/energy",
            ">absorbed_beam": "../absorbed_beam/data",
        },
        "start_time": start_time,
        "title": title,
        "definition": definition,
    }
    if overwrite:
        mode = "w"
        update_mode = "replace"
    else:
        mode = "a"
        update_mode = "add"
    dicttonx(nx_dict, h5_file, h5path=h5path, mode=mode, update_mode=update_mode)


def write_spectrum_saving_pt(h5_file, entry, obj, overwrite=True):
    """Save the current status of an est object

    :param str h5_file: path to the hdf5 file
    :param str entry: entry name
    :param obj: object to save.
    :param str obj_name: name of the object to store
    :param str data_path:
    """
    dicttoh5(obj, h5file=h5_file, h5path=entry, update_mode="replace", mode="a")


def get_xasproc(h5_file, entry):
    """
    Return the list of all NXxasproc existing at the data_path level

    :param str h5_file: hdf5 file
    :param str entry: data location

    :return:
    :rtype: list
    """

    def copy_nx_xas_process(h5_group):
        """copy base information from nx_xas_process"""
        res = {}
        res["_h5py_path"] = h5_group.name
        relevant_keys = (
            "program",
            "version",
            "data",
            "parameters",
            "processing_order",
            "configuration",
            "class_instance",
            "plots",
        )
        from silx.io.dictdump import h5todict

        for key in h5_group.keys():
            # for now we don't want to copy the numpy array (data)
            if key in relevant_keys:
                if key == "configuration":
                    config_path = "/".join((h5_group.name, "configuration"))
                    res[key] = h5todict(h5_file, config_path, asarray=False)
                elif key == "plots":
                    plots_grp = h5_group["plots"]
                    res[key] = {}
                    for plot_key in plots_grp.keys():
                        res[key][plot_key] = dict(plots_grp[plot_key].attrs.items())
                else:
                    res[key] = h5_group[key][...]
        return res

    res = []
    with HDF5File(h5_file, "a") as h5f:
        try:
            root_group = h5f[entry]
        except KeyError:
            _logger.warning(entry + " does not exist in " + h5_file)
        else:
            for key in root_group.keys():
                elmt = root_group[key]
                if hasattr(elmt, "attrs") and "NX_class" in elmt.attrs:
                    if elmt.attrs["NX_class"] == "NXprocess":
                        nx_xas_proc = copy_nx_xas_process(elmt)
                        if len(nx_xas_proc) == 0:
                            _logger.warning(
                                "one xas process was not readable "
                                "from the hdf5 file at:" + key
                            )
                        else:
                            res.append(nx_xas_proc)
    return res


if __name__ == "__main__":
    import os

    from est.core.process.pymca.exafs import PyMca_exafs
    from est.core.process.pymca.normalization import PyMca_normalization
    from est.core.types import Sample

    h5_file = "test_xas_123.h5"
    if os.path.exists(h5_file):
        os.remove(h5_file)
    sample = Sample(name="mysample")
    data = numpy.random.rand(256 * 20 * 10)
    data = data.reshape((256, 20, 10))
    process_data = numpy.random.rand(256 * 20 * 10).reshape((256, 20, 10))
    energy = numpy.linspace(start=3.25, stop=3.69, num=256)

    write_xas(h5_file=h5_file, entry="scan1", sample=sample, energy=energy, mu=data)

    process_norm = PyMca_normalization()
    write_xas_proc(
        h5_file=h5_file,
        entry="scan1",
        process=process_norm,
        results=process_data,
        processing_order=1,
    )
    process_exafs = PyMca_exafs()
    process_data2 = numpy.random.rand(256 * 20 * 10).reshape((256, 20, 10))
    write_xas_proc(
        h5_file=h5_file,
        entry="scan1",
        process=process_exafs,
        results=process_data2,
        processing_order=2,
    )
