import logging
from typing import Optional
from typing import Tuple

import numpy

from est.units import ur

_logger = logging.getLogger(__name__)


def parse_energy_mu(
    energy: Optional[numpy.ndarray],
    mu: Optional[numpy.ndarray],
    monitor: Optional[numpy.ndarray],
    energy_unit,
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    if energy is None:
        energy = numpy.array([])
    if mu is None:
        mu = numpy.array([])
    has_monitor = monitor is not None

    if has_monitor:
        n = {len(energy), len(mu), len(monitor)}
        if len(n) != 1:
            _logger.warning("Trim unequal size of energy, mu and monitor")
            n = min(n)
            energy = energy[:n]
            mu = mu[:n]
            monitor = monitor[:n]
    else:
        n = {len(energy), len(mu)}
        if len(n) != 1:
            _logger.warning("Trim unequal size of energy and mu")
            n = min(n)
            energy = energy[:n]
            mu = mu[:n]

    energy = (energy * energy_unit).m_as(ur.eV)

    if has_monitor:
        with numpy.errstate(divide="ignore"):
            mu = mu / monitor
        not_finite = ~numpy.isfinite(mu)
        if not_finite.any():
            _logger.warning(
                "found non-finite values after mu division by the monitor. Replace them by 0"
            )
            mu[not_finite] = 0

    return energy, mu
