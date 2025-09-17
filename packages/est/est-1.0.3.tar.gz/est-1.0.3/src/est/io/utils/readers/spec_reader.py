import functools
import logging
from typing import List
from typing import Optional
from typing import Tuple

import numpy
from silx.io.specfile import SfErrFileOpen
from silx.io.spech5 import SpecFile

from est.units import ur

from .abstract_ascii import AbstractAsciiReader
from .parse import parse_energy_mu

_logger = logging.getLogger(__name__)


class SpecReader(AbstractAsciiReader):
    @staticmethod
    def get_first_scan_title(file_path: str) -> Optional[str]:
        spec_file = SpecFile(file_path)
        try:
            scan = spec_file[0]
        except IndexError:
            return None
        return scan.scan_header_dict["S"]

    @staticmethod
    def get_all_scan_titles(file_path: str) -> List[str]:
        return [scan.scan_header_dict["S"] for scan in SpecFile(file_path)]

    @staticmethod
    def get_scan_column_names(file_path: str, scan_title: str) -> List[str]:
        for scan in SpecFile(file_path):
            if not scan_title or scan_title == scan.scan_header_dict["S"]:
                return scan.labels
        return list()

    @staticmethod
    @functools.lru_cache(maxsize=2)  # called twice for energy and absorption
    def read_spectrum(
        filename,
        energy_col_name=None,
        absorption_col_name=None,
        monitor_col_name=None,
        energy_unit=ur.eV,
        scan_title=None,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        try:
            spec_file = SpecFile(filename)
        except SfErrFileOpen:
            if _is_empty(filename):
                return numpy.array([]), numpy.array([])
            raise

        for scan in spec_file:
            is_scan = scan_title == scan.scan_header_dict["S"]
            if not is_scan:
                if scan_title is None:
                    continue
                return numpy.array([]), numpy.array([])

            columns = scan.labels
            if energy_col_name is None:
                _logger.warning(
                    "Spec energy column name not provided. Select the first column."
                )
                energy_col_name = columns[0]
            if absorption_col_name is None:
                _logger.warning(
                    "Spec absorption column name not provided. Select the second column."
                )
                absorption_col_name = columns[1]

            has_energy = energy_col_name in columns
            has_absorption = absorption_col_name in columns
            if not has_energy and not has_absorption:
                return numpy.array([]), numpy.array([])

            has_monitor = monitor_col_name in columns
            energy = None
            mu = None
            monitor = None
            if has_energy:
                energy = scan.data_column_by_name(label=energy_col_name)
            if has_absorption:
                mu = scan.data_column_by_name(label=absorption_col_name)
            if has_monitor:
                monitor = scan.data_column_by_name(label=monitor_col_name)

            return parse_energy_mu(energy, mu, monitor, energy_unit)

        return numpy.array([]), numpy.array([])


def _is_empty(filename) -> bool:
    try:
        with open(filename, "r") as f:
            for line in f:
                if line:
                    return False
    except FileNotFoundError:
        return False
    return True
