import functools
import logging
from typing import Dict
from typing import List
from typing import Tuple

import numpy

try:
    from larch.io import columnfile
except ImportError:
    columnfile = None

from est.units import ur

from .abstract_ascii import AbstractAsciiReader
from .parse import parse_energy_mu

_logger = logging.getLogger(__name__)


def _read_columnfile(
    column_file,
) -> Dict[str, numpy.ndarray]:
    if columnfile is None:
        raise ImportError("Larch not imported")
    larch_group = columnfile.read_ascii(column_file)
    return dict(zip(larch_group.array_labels, larch_group.data))


class LarchReader(AbstractAsciiReader):
    @staticmethod
    def get_scan_column_names(file_path: str, scan_title: str) -> List[str]:
        return list(_read_columnfile(file_path))

    @staticmethod
    @functools.lru_cache(maxsize=2)  # called twice for energy and absorption
    def read_spectrum(
        column_file,
        energy_col_name=None,
        absorption_col_name=None,
        monitor_col_name=None,
        energy_unit=ur.eV,
        scan_title=None,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        data = _read_columnfile(column_file)

        if energy_col_name is None:
            _logger.warning("Larch energy column name not provided. Try 'energy'")
            energy_col_name = "energy"
        if absorption_col_name is None:
            _logger.warning("Larch absorption column name not provided. Try 'mu'")
            absorption_col_name = "mu"
        if monitor_col_name is None:
            _logger.warning("Larch monitor column name not provided. Try 'i0'")
            monitor_col_name = "i0"

        energy = data.get(energy_col_name)
        mu = data.get(absorption_col_name)
        monitor = data.get(monitor_col_name)

        return parse_energy_mu(energy, mu, monitor, energy_unit)
