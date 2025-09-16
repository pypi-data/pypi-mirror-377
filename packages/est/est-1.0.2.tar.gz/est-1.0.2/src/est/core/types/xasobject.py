from __future__ import annotations

import copy
import logging
from typing import Any
from typing import Sequence

import numpy
import pint
from silx.io.url import DataUrl

from est.core.types.dimensions import STANDARD_DIMENSIONS
from est.io.utils import get_data_from_url
from est.settings import DEFAULT_READ_TIMEOUT
from est.units import ur

from .spectra import Spectra
from .spectrum import Spectrum

_logger = logging.getLogger(__name__)


class XASObject:
    """Base class of XAS

    :param spectra: absorbed beam as a list of :class:`.Spectrum` or a
                    numpy.ndarray. If is a numpy array, the axes should
                    have the `STANDARD_DIMENSIONS` order.
    :param energy: beam energy
    :param configuration: configuration of the different process
    :param dim1: first dimension of the spectra
    :param dim2: second dimension of the spectra
    :param name: name of the object. Will be used for the hdf5 entry
    :param spectra_url: path to the spectra data if any. Used when serializing
                        the XASObject. Won't read it from it.
    :param energy_url: path to the energy / channel  data if any. Used when
                       serializing the XASObject. Won't read it from it.
    """

    def __init__(
        self,
        spectra: numpy.ndarray | Sequence[Any] | None = None,
        energy: numpy.ndarray | None = None,
        configuration: dict | None = None,
        dim1: int | None = None,
        dim2: int | None = None,
        name: str = "scan1",
        spectra_url: DataUrl | None = None,
        energy_url: DataUrl | None = None,
    ):
        if isinstance(energy, numpy.ndarray) and not isinstance(energy, pint.Quantity):
            # automatic energy unit guess. convert energy provided in keV to eV
            # works because EXAFS data are never longer than 2 keV and a low
            # energy XANES is never shorter than 3 eV.
            # See https://gitlab.esrf.fr/workflow/ewoksapps/est/-/issues/30
            if (energy.max() - energy.min()) < 3.0:
                energy = energy * ur.keV
            else:
                energy = energy * ur.eV

        if energy is not None:
            energy = energy.m_as(ur.eV)

        self.__entry_name = name
        self.__spectra_url = spectra_url
        self.__energy_url = energy_url
        self.spectra = (energy, spectra, dim1, dim2)
        self.configuration = configuration

    def attach_3d_array(self, attr_name: str, attr_value: DataUrl | numpy.ndarray):
        """
        Attach to each attribute the provided value
        """
        if isinstance(attr_value, DataUrl):
            data = get_data_from_url(attr_value)
        else:
            data = attr_value
        if data.shape[0] > self.energy.shape[0]:
            _logger.warning(
                "energy has less value than dataset. Clip {}.".format(attr_name)
            )
            data = data[: self.energy.shape[0]]
        if not isinstance(data, numpy.ndarray):
            raise TypeError(
                "`attr_value` should be an instance of DataUrl "
                "referencing a numpy array or a numpy array not "
                "{}".format(type(data))
            )
        if data.ndim > 2:
            for spectrum, d in zip(self.spectra.data.flat, data):
                setattr(spectrum, attr_name, d)
        else:
            for spectrum in self.spectra.data.flat:
                setattr(spectrum, attr_name, data)

    @property
    def entry(self) -> str:
        return self.__entry_name

    @property
    def spectra(self) -> Spectra:
        return self.__spectra

    @property
    def spectra_url(self) -> DataUrl | None:
        """Url from where the spectra is available.
        Used for object serialization"""
        return self.__spectra_url

    @spectra_url.setter
    def spectra_url(self, url: DataUrl):
        self.__spectra_url = url

    @property
    def energy_url(self) -> DataUrl | None:
        """Url from where the energy is available.
        Used for object serialization"""
        return self.__energy_url

    @energy_url.setter
    def energy_url(self, url: DataUrl):
        self.__energy_url = url

    @property
    def normalized_energy(self):
        if self.spectra is not None:
            return self.spectra.data.flat[0].normalized_energy

    # TODO: should no take such a tuple in parameter but the different parameters
    # energy, spectra, dim1, dim2
    @spectra.setter
    def spectra(self, energy_spectra: Spectra | tuple | None):
        if isinstance(energy_spectra, Spectra):
            self.__spectra = energy_spectra
            return

        if energy_spectra is None:
            return

        if len(energy_spectra) != 4:
            raise ValueError(
                f"4 elements expected: energy, spectra, dim1 and dim2. get {len(energy_spectra)} instead"
            )
        energy, spectra, dim1, dim2 = energy_spectra
        self.__spectra = Spectra(energy=energy, spectra=spectra)
        if dim1 is not None and dim2 is not None:
            self.__spectra.reshape((dim1, dim2))

    def get_spectrum(self, dim1_idx: int, dim2_idx: int) -> Spectrum:
        """Util function to access the spectrum at dim1_idx, dim2_idx"""
        return self.spectra[dim1_idx, dim2_idx]

    @property
    def energy(self) -> numpy.ndarray:
        """energy as a numpy array in eV.
        :note: cannot be with unit because use directly by xraylarch and pymca
        """
        return self.spectra.energy

    @property
    def configuration(self) -> dict:
        return self.__configuration

    @configuration.setter
    def configuration(self, configuration: dict | None):
        assert configuration is None or isinstance(configuration, dict)
        self.__configuration = configuration or {}

    def to_dict(self) -> dict:
        """convert the XAS object to a dict

        By default made to simply import raw data.
        """

        res = {
            "configuration": self.configuration,
            "dim1": self.spectra.shape[0],
            "dim2": self.spectra.shape[1],
            "energy": self.spectra.energy,
            "spectra": [spectrum.to_dict() for spectrum in self.spectra],
            "dimensions": STANDARD_DIMENSIONS,  # spectra dimensions are always changed to STANDARD on load
        }
        return res

    def absorbed_beam(self) -> numpy.ndarray:
        return self.spectra.as_ndarray("mu")

    def load_from_dict(self, ddict: dict) -> XASObject:
        """load XAS values from a dict"""
        if not isinstance(ddict, dict):
            raise TypeError(f"ddict is expected to be a dict. Not {type(ddict)}")
        dimensions = ddict.get("dimensions", STANDARD_DIMENSIONS)
        # default way of storing data
        from est.io import load_data  # avoid cyclic import

        """The dict can be on the scheme of the to_dict function, containing
        the spectra and the configuration. Otherwise we consider it is simply
        the spectra"""
        if "configuration" in ddict:
            self.configuration = ddict["configuration"]
        if "spectra" in ddict:
            self.spectra = Spectra.from_dict(ddict["spectra"], dimensions=dimensions)
        else:
            self.spectra = None
        if "energy" in ddict:
            energy = ddict["energy"]
            if isinstance(energy, str):
                energy_url = DataUrl(path=energy)
                energy = load_data(
                    data_url=energy_url, name="energy", dimensions=dimensions
                )
        else:
            energy = None
        if "dim1" in ddict:
            dim1 = ddict["dim1"]
        else:
            dim1 = None
        if "dim2" in ddict:
            dim2 = ddict["dim2"]
        else:
            dim2 = None

        self.spectra.reshape((dim1, dim2))
        return self

    @staticmethod
    def from_dict(ddict: dict) -> XASObject:
        return XASObject().load_from_dict(ddict=ddict)

    @staticmethod
    def from_file(
        h5_file,
        entry="scan1",
        spectra_path="data/absorbed_beam",
        energy_path="data/energy",
        configuration_path="configuration",
        dimensions=None,
        timeout=DEFAULT_READ_TIMEOUT,
    ) -> XASObject:
        from est.core.io import read_from_url  # avoid cyclic import

        # load only mu and energy from the file
        spectra_url = DataUrl(
            file_path=h5_file, data_path="/".join((entry, spectra_path)), scheme="silx"
        )
        energy_url = DataUrl(
            file_path=h5_file, data_path="/".join((entry, energy_path)), scheme="silx"
        )
        if configuration_path is None:
            config_url = None
        else:
            config_url = DataUrl(
                file_path=h5_file,
                data_path="/".join((entry, configuration_path)),
                scheme="silx",
            )
        return read_from_url(
            spectra_url=spectra_url,
            channel_url=energy_url,
            config_url=config_url,
            dimensions=dimensions,
            timeout=timeout,
        )

    def dump(self, h5_file: str):
        """dump the XAS object to a file_path within the Nexus format"""
        from est.core.io import dump_xas  # avoid cyclic import

        dump_xas(h5_file, self)

    def deepcopy(self) -> XASObject:
        return self.from_dict(self.to_dict())

    def copy(self) -> XASObject:
        """ """
        # To have dedicated h5 file we have to create one new h5 file for
        # for each process. For now there is no way to do it differently
        res = copy.copy(self)
        return res

    def __eq__(self, other: Any):
        if other is None:
            return False
        return (
            isinstance(other, XASObject)
            and (
                (self.energy is None and other.energy is None)
                or numpy.array_equal(self.energy, other.energy)
            )
            and self.configuration == other.configuration
            and self.spectra,
            other.spectra,
        )

    @property
    def n_spectrum(self) -> int:
        """return the number of spectra"""
        return len(self.spectra.data.flat)
