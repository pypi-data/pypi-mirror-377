from typing import Iterable
from typing import Union

import numpy
import pint
from silx.io.url import DataUrl

from est.units import ur

from .spectrum import Spectrum

try:
    from larch import symboltable
except ImportError:
    symboltable = None

import logging

_logger = logging.getLogger(__name__)


class Spectra:
    """
    A map of spectrum.

    - data: numpy array of Spectrum. Expected to be 2D.
    - energy: set of energy for each position (x,y)
    """

    def __init__(self, energy, spectra: Union[Iterable, None] = None):
        self.__data = numpy.array([])
        self.energy = energy
        if spectra is None:
            spectra = []
        if not isinstance(spectra, (list, tuple, numpy.ndarray)):
            raise TypeError("spectra type is invalid: {}".format(type(spectra)))

        spectrum_list = []
        shape = (1, -1)
        if isinstance(spectra, numpy.ndarray):
            if spectra.ndim == 2:
                for spectrum in spectra.flat:
                    if not isinstance(spectrum, Spectrum):
                        raise TypeError(
                            f"If spectra is provided as a 2D array we expect it to contain Spectrum already. Found one element of type {type(spectrum)}"
                        )
                self.__data = spectra
                return
            elif not spectra.ndim == 3:
                raise ValueError("Provided spectra is expected to be 3d")
            else:
                for y_i_spectrum in range(spectra.shape[1]):
                    for x_i_spectrum in range(spectra.shape[2]):
                        spectrum_list.append(
                            Spectrum(
                                energy=self.energy,
                                mu=spectra[:, y_i_spectrum, x_i_spectrum],
                            )
                        )
                # spectra dimensions should be channel, y, x
                shape = spectra.shape[-2:]
        else:
            for spectrum in spectra:
                if not isinstance(spectrum, Spectrum):
                    raise TypeError(
                        f"spectra is expected to contain {Spectrum} only and not",
                        type(spectrum),
                    )
                spectrum_list.append(spectrum)
        self.__data = numpy.array(spectrum_list)
        for spec in self.__data.flat:
            assert isinstance(spec, Spectrum)
        self.reshape(shape)

    def check_validity(self):
        for spectrum in self.data.flat:
            if not isinstance(spectrum, Spectrum):
                raise TypeError(
                    f"spectra is expected to contain {Spectrum} only and not",
                    type(spectrum),
                )
            if not isinstance(spectrum.energy, (numpy.ndarray, pint.Quantity)):
                raise ValueError(
                    f"spectrum energy is {type(spectrum.energy)}. When numpy array or pint.Quantity expected"
                )
            if not isinstance(spectrum.mu, numpy.ndarray):
                raise ValueError(
                    f"spectrum mu is {type(spectrum.mu)}. When numpy array"
                )

    @property
    def data(self):
        return self.__data

    def __getitem__(self, item):
        return self.__data[item]

    @property
    def shape(self):
        return self.__data.shape

    def reshape(self, shape):
        assert len(shape) == 2
        assert isinstance(shape, Iterable)
        if None in shape:
            raise ValueError("None not handled")
        self.__data = self.__data.reshape(shape)
        for spec in self.__data.flat:
            assert isinstance(spec, Spectrum)
        return self.__data

    @property
    def energy(self) -> numpy.ndarray:
        """Energy in eV"""
        return self.__energy

    @energy.setter
    @ur.wraps(None, (None, ur.eV), strict=False)
    def energy(self, energy):
        self.__energy = energy
        if len(self.data) > 0:
            if len(self.data.flat[0].energy) != len(energy):
                _logger.warning("spectra and energy have incoherent dimension")

    def as_ndarray(self, key: str) -> numpy.ndarray:
        """
        Convert the spectra to a numpy ndarray.
        The shape of the array will be adapted according to the 'relative_to' parameter.

        :param key: spectra field to be converted to a numpy ndarray (of dimension two). Key must be in ('mu', 'normalized_mu')
        """
        valid_keys = ("mu", "normalized_mu")
        if key not in valid_keys:
            raise ValueError(f"key should be in {valid_keys}. Got {key}")

        def get_param(object, name):
            if hasattr(object, name):
                return getattr(object, name)
            else:
                return object[name]

        if len(self.data.flat) == 0:
            return None

        array = None
        for i_spectrum, spectrum in enumerate(self.data.flat):
            try:
                if "." in key:
                    subkeys = key.split(".")
                    key_ = subkeys[-1]
                    subkeys = subkeys[:-1]
                    value = get_param(spectrum, subkeys[0])
                    for subkey in subkeys[1:]:
                        value = get_param(value, subkey)
                    value = get_param(value, key_)
                else:
                    value = get_param(spectrum, key)
            except Exception:
                _logger.info("fail to access to {}".format(key))
                break

            if isinstance(value, pint.Quantity):
                value = value.m_as(ur.eV)
            if symboltable is not None and isinstance(value, symboltable.Group):
                _logger.info("pass larch details, not managed for now")
                continue

            if array is None:
                if value is not None:
                    array = numpy.zeros((len(value), len(self.data.flat)))
                else:
                    array = numpy.zeros((len(self.data.flat)))

            array[:, i_spectrum] = value

        if array is None:
            return array

        shape = list(self.data.shape)
        shape.insert(0, -1)
        return array.reshape(shape)

    def __eq__(self, other):
        if not isinstance(other, Spectra):
            return False
        if len(self.data) != len(other.data):
            return False
        else:
            return numpy.array_equal(self.data.flat, other.data.flat)

    def __iter__(self):
        return iter(self.data.flat)

    @staticmethod
    def from_dict(ddict, dimensions):
        """
        :param dict ddict: dict containing the data to be loaded
        :param tuple dimensions: information regarding spectra dimensions
        """
        from est.io import load_data  # avoid cyclic import

        # if spectra is given from an url
        if isinstance(ddict, str):
            return load_data(
                data_url=DataUrl(path=ddict),
                name="spectra",
                dimensions=dimensions,
            )
        # if come from a list of spectrum
        elif not isinstance(ddict, (numpy.ndarray, pint.Quantity)):
            new_spectra = []
            for spectrum in ddict:
                assert isinstance(spectrum, dict)
                new_spectra.append(Spectrum.from_dict(spectrum))
            return Spectra(energy=new_spectra[0].energy, spectra=new_spectra)
        else:
            raise TypeError("Unhandled input type ({})".format(type(ddict)))
