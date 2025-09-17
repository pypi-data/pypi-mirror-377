import logging
from typing import List
from typing import Optional

import h5py
import numpy
import silx.io.h5py_utils
import silx.io.utils
from silx.io.dictdump import h5todict
from silx.io.url import DataUrl
from silx.utils.retry import RetryError

try:
    is_h5py_exception = silx.io.h5py_utils.is_h5py_exception
except AttributeError:
    is_h5py_exception = silx.io.h5py_utils._is_h5py_exception

from est import settings
from est.core.types import Spectrum
from est.units import ur

from .ascii import read_spectrum
from .ascii import split_ascii_url
from .readers import fabio_reader
from .readers import silx_reader

_logger = logging.getLogger(__name__)


def _retry_on_error(e):
    if is_h5py_exception(e):
        return isinstance(e, (OSError, RuntimeError, KeyError))
    return isinstance(e, RetryError)


@silx.io.h5py_utils.retry(
    retry_timeout=settings.DEFAULT_READ_TIMEOUT, retry_on_error=_retry_on_error
)
def get_data_from_url(url) -> numpy.ndarray:
    """Returns a numpy data from an URL.

    Examples:

    >>> # 1st frame from an EDF using silx.io.open
    >>> data = silx.io.get_data("silx:/users/foo/image.edf::/scan_0/instrument/detector_0/data[0]")

    >>> # 1st frame from an EDF using fabio
    >>> data = silx.io.get_data("fabio:/users/foo/image.edf::[0]")

    Yet 2 schemes are supported by the function.

    - If `silx` scheme is used, the file is opened using
        :meth:`silx.io.open`
        and the data is reach using usually NeXus paths.
    - If `fabio` scheme is used, the file is opened using :meth:`fabio.open`
        from the FabIO library.
        No data path have to be specified, but each frames can be accessed
        using the data slicing.
        This shortcut of :meth:`silx.io.open` allow to have a faster access to
        the data.

    .. seealso:: :class:`silx.io.url.DataUrl`

    :param Union[str,silx.io.url.DataUrl]: A data URL
    :rtype: Union[numpy.ndarray, numpy.generic]
    :raises ImportError: If the mandatory library to read the file is not
        available.
    :raises ValueError: If the URL is not valid or do not match the data
    :raises IOError: If the file is not found or in case of internal error of
        :meth:`fabio.open` or :meth:`silx.io.open`. In this last case more
        informations are displayed in debug mode.
    """
    if not isinstance(url, silx.io.url.DataUrl):
        url = silx.io.url.DataUrl(url)
    if not url.is_valid():
        raise ValueError("URL '%s' is not valid" % url.path())
    if url.scheme() == "silx":
        return silx_reader.get_data(url)
    if url.scheme() == "fabio":
        return fabio_reader.get_data(url)
    raise ValueError("Scheme '%s' not supported" % url.scheme())


def get_ascii_data(
    url: DataUrl,
    name: str,
    columns_names: Optional[dict] = None,
    energy_unit=ur.eV,
) -> numpy.ndarray:
    scheme = url.scheme().lower()
    if scheme in ("ascii", "spec", "pymca", "pymca5", "larch", "xraylarch"):
        energy, mu = read_spectrum(
            url.file_path(),
            energy_col_name=columns_names["energy"] if columns_names else None,
            absorption_col_name=columns_names["mu"] if columns_names else None,
            monitor_col_name=columns_names["monitor"] if columns_names else None,
            scan_title=split_ascii_url(url)["scan_title"],
            energy_unit=energy_unit,
            scheme=scheme,
        )
        if name == "spectra":
            mu = numpy.ascontiguousarray(mu[:])
            return mu.reshape(-1, 1, 1)
        return energy
    raise ValueError("Scheme '%s' not supported" % url.scheme())


@silx.io.h5py_utils.retry(retry_timeout=settings.DEFAULT_READ_TIMEOUT)
def get_est_data(url) -> List[Spectrum]:
    spectra = []
    with silx.io.h5py_utils.File(url.file_path(), "r") as hdf5:
        # get all possible entries
        entries = filter(
            lambda x: isinstance(hdf5[x], h5py.Group)
            and "est_saving_pt" in hdf5[x].keys(),
            hdf5.keys(),
        )
        entries = list(entries)
        if len(entries) == 0:
            _logger.error("no spectra dataset found in the file", url.file_path())
            return

        if len(entries) > 1:
            _logger.warning(
                "several entry detected, only one will be loaded:", entries[0]
            )
        spectra_path = "/".join((entries[0], "est_saving_pt", "spectra"))
        node_spectra = hdf5[spectra_path]
        spectrum_indexes = list(node_spectra.keys())
        spectrum_indexes = list(map(lambda x: int(x), spectrum_indexes))
        spectrum_indexes.sort()

    for index in spectrum_indexes:
        spectrum_path = "/".join((spectra_path, str(index)))
        dict_ = h5todict(h5file=url.file_path(), path=spectrum_path, asarray=False)
        spectrum = Spectrum.from_dict(dict_)
        spectra.append(spectrum)
    return spectra
