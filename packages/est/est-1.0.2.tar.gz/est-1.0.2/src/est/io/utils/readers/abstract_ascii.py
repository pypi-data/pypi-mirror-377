import abc
from typing import List
from typing import Tuple

import numpy

from est.units import ur


class AbstractAsciiReader(abc.ABC):
    @staticmethod
    def get_first_scan_title(file_path: str):
        return None

    @staticmethod
    def get_all_scan_titles(file_path: str) -> List[str]:
        return list()

    @staticmethod
    @abc.abstractmethod
    def get_scan_column_names(file_path: str, scan_title: str) -> List[str]:
        pass

    @staticmethod
    @abc.abstractmethod
    def read_spectrum(
        ascii_file,
        energy_col_name=None,
        absorption_col_name=None,
        monitor_col_name=None,
        energy_unit=ur.eV,
        scan_title=None,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        pass
