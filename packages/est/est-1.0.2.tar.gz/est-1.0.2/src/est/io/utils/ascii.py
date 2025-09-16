import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy
from silx.io.url import DataUrl

from est.units import ur

from .readers.abstract_ascii import AbstractAsciiReader
from .readers.ascii_reader import AsciiReader
from .readers.larch_reader import LarchReader
from .readers.spec_reader import SpecReader


def _get_reader(file_path: str, scheme: Optional[str] = None) -> AbstractAsciiReader:
    _, ext = os.path.splitext(file_path)
    if scheme == "larch" or ext == ".xmu":
        return LarchReader()
    if scheme == "spec" or ext == ".spec" or _is_spec(file_path):
        return SpecReader()
    return AsciiReader()


def _is_spec(file_path: str) -> bool:
    if not os.path.isfile(file_path):
        return False

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                return line.startswith("#F ")

    return False


def read_spectrum(
    file_path: str,
    energy_col_name: Optional[str] = None,
    absorption_col_name: Optional[str] = None,
    monitor_col_name: Optional[str] = None,
    energy_unit=ur.eV,
    scan_title: Optional[str] = None,
    scheme: Optional[str] = None,
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    return _get_reader(file_path, scheme=scheme).read_spectrum(
        file_path,
        energy_col_name=energy_col_name,
        absorption_col_name=absorption_col_name,
        monitor_col_name=monitor_col_name,
        energy_unit=energy_unit,
        scan_title=scan_title,
    )


def get_first_scan_title(file_path: str) -> Optional[str]:
    return _get_reader(file_path).get_first_scan_title(file_path)


def get_all_scan_titles(file_path: str) -> List[str]:
    return _get_reader(file_path).get_all_scan_titles(file_path)


def get_scan_column_names(file_path: str, scan_title: str) -> List[str]:
    return _get_reader(file_path).get_scan_column_names(file_path, scan_title)


def build_ascii_data_url(
    file_path: str,
    col_name: str,
    scan_title: Optional[str] = None,
    data_slice: Optional[slice] = None,
):
    if scan_title is None:
        scan_title = get_first_scan_title(file_path)
    if scan_title is None:
        scan_title = ""

    if "/" in scan_title:
        raise ValueError("scan_title cannot contain '/'")
    data_path = f"{scan_title}/{col_name}"

    _, ext = os.path.splitext(file_path)
    if ext == ".xmu":
        scheme = "larch"
    elif ext == ".spec" or _is_spec(file_path):
        scheme = "spec"
    else:
        scheme = "ascii"

    return DataUrl(
        file_path=file_path,
        data_path=data_path,
        data_slice=data_slice,
        scheme=scheme,
    )


def split_ascii_url(url: DataUrl) -> Dict[str, Any]:
    """
    convert an url to (file_path, scan_title, col_name, data_slice)
    """
    if not isinstance(url, DataUrl):
        raise TypeError
    scan_title = None
    col_name = None
    data_path = url.data_path()
    if data_path:
        parts = data_path.split("/")
        if parts:
            scan_title = parts[0]
            if len(parts) > 1:
                col_name = "/".join(parts[1:])
    return {
        "file_path": url.file_path(),
        "scan_title": scan_title,
        "col_name": col_name,
        "data_slice": url.data_slice(),
    }
