import logging
from typing import Union

import numpy
import pint

from est.units import ur

_logger = logging.getLogger(__name__)


class Spectrum:
    """
    Core object to be used to store larch and pymca results.

    Larch is using 'Group' to store the results and adds members to this group
    according to the different treatment. Pymca is using a dictionary to store
    the results.

    This class has to adpat to both behaviors and the different naming
    convention as well.

    :param numpy.ndarray (1D) energy: beam energy
    :param numpy.ndarray (1D) mu: beam absorption
    :param int x: x index on the spectra
    :param int y: y index on the spectra
    """

    _MU_KEY = "Mu"

    _ENERGY_KEY = "Energy"

    _NORMALIZED_MU_KEY = "NormalizedMu"

    _NORMALIZED_ENERGY_KEY = "NormalizedEnergy"

    _POST_EDGE_KEY = "post_edge"

    _EDGE_STEP_KEY = "edge_step"

    _CHI_KEY = "Chi"

    _K_KEY = "K"

    _FT_KEY = "FT"

    _EDGE_KEY = "Edge"

    _NORMALIZED_BACKGROUND_KEY = "NormalizedBackground"

    _X_POS_KEY = "XPos"

    _Y_POS_KEY = "YPos"

    _PYMCA_DICT_KEY = "pymca_dict"

    _LARCH_DICT_KEY = "larch_dict"

    def __init__(
        self,
        energy: Union[None, numpy.ndarray] = None,
        mu: Union[None, numpy.ndarray] = None,
        x: Union[None, int] = None,
        y: Union[None, int] = None,
    ):
        super().__init__()
        if energy is not None:
            assert isinstance(energy, (numpy.ndarray, pint.Quantity)), energy
            if isinstance(energy, numpy.ndarray):
                energy = energy * ur.eV

        self.__x = x
        self.__y = y

        # properties
        self.__energy = None
        self.__mu = None
        self.__chi = None
        self.__k_values = None
        self.__normalized_mu = None
        self.__flatten_mu = None
        self.__normalized_energy = None
        self.__pre_edge = None
        self.__post_edge = None
        self.__edge_step = None
        self.__e0 = None
        self.__noise_savgol = None
        self.__norm_noise_savgol = None
        self.__raw_noise_savgol = None
        self.ft = _FT()
        self.__pymca_dict = {}
        # pymca dict use to store some processing information specific to pymca
        self.__larch_dict = {}

        # TODO: this should be removed as the item setting as a dict has been removed
        self.__key_mapper = {
            self._MU_KEY: self.__class__.mu,
            self._ENERGY_KEY: self.__class__.energy,
            self._NORMALIZED_MU_KEY: self.__class__.normalized_mu,
            self._NORMALIZED_ENERGY_KEY: self.__class__.normalized_energy,
            self._POST_EDGE_KEY: self.__class__.post_edge,
            self._NORMALIZED_BACKGROUND_KEY: self.__class__.pre_edge,
            self._FT_KEY: self.__class__.ft,
            self._EDGE_KEY: self.__class__.e0,
            self._EDGE_STEP_KEY: self.__class__.edge_step,
            self._CHI_KEY: self.__class__.chi,
            self._K_KEY: self.__class__.k,
            self._PYMCA_DICT_KEY: self.__class__.pymca_dict,
            self._LARCH_DICT_KEY: self.__class__.larch_dict,
        }

        self.energy = energy
        self.mu = mu

    @property
    def energy(self) -> Union[None, numpy.ndarray]:
        """Energy in eV.

        :note: cannot be a Quantity because uses directly by xraylarch and pymca
        """
        return self.__energy

    @energy.setter
    @ur.wraps(None, (None, ur.eV), strict=False)
    def energy(self, energy):
        self.__energy = energy

    @property
    def mu(self) -> Union[None, numpy.ndarray]:
        return self.__mu

    @mu.setter
    def mu(self, mu: numpy.ndarray):
        assert isinstance(mu, numpy.ndarray) or mu is None
        self.__mu = mu

    @property
    def x(self) -> Union[None, int]:
        return self.__x

    @property
    def y(self) -> Union[None, int]:
        return self.__y

    @property
    def chi(self) -> Union[None, numpy.ndarray]:
        return self.__chi

    @chi.setter
    def chi(self, chi: numpy.ndarray):
        self.__chi = chi

    @property
    def k(self) -> Union[None, numpy.ndarray]:
        return self.__k_values

    @k.setter
    def k(self, k: numpy.ndarray):
        self.__k_values = k

    @property
    def normalized_mu(self) -> Union[None, numpy.ndarray]:
        return self.__normalized_mu

    @normalized_mu.setter
    def normalized_mu(self, mu: numpy.ndarray):
        assert isinstance(mu, numpy.ndarray) or mu is None
        self.__normalized_mu = mu

    @property
    def flatten_mu(self) -> Union[None, numpy.ndarray]:
        return self.__flatten_mu

    @flatten_mu.setter
    def flatten_mu(self, mu: numpy.ndarray):
        assert isinstance(mu, numpy.ndarray) or mu is None
        self.__flatten_mu = mu

    @property
    def normalized_energy(self) -> Union[None, numpy.ndarray]:
        return self.__normalized_energy

    @normalized_energy.setter
    def normalized_energy(self, energy: Union[numpy.ndarray, pint.Quantity]):
        if not (isinstance(energy, (numpy.ndarray, pint.Quantity)) or energy is None):
            raise TypeError(
                f"energy is expected to be None or a numpy array or a Quantity. Not {type(energy)}."
            )
        self.__normalized_energy = energy

    @property
    def pre_edge(self) -> Union[None, numpy.ndarray]:
        return self.__pre_edge

    @pre_edge.setter
    def pre_edge(self, value: numpy.ndarray):
        self.__pre_edge = value

    @property
    def post_edge(self) -> Union[None, numpy.ndarray]:
        return self.__post_edge

    @post_edge.setter
    def post_edge(self, value: numpy.ndarray):
        self.__post_edge = value

    @property
    def edge_step(self):
        return self.__edge_step

    @edge_step.setter
    def edge_step(self, value):
        self.__edge_step = value

    @property
    def e0(self) -> Union[None, numpy.ndarray]:
        return self.__e0

    @e0.setter
    def e0(self, e0: numpy.ndarray):
        self.__e0 = e0

    @property
    def noise_savgol(self):
        return self.__noise_savgol

    @noise_savgol.setter
    def noise_savgol(self, values):
        self.__noise_savgol = values

    @property
    def raw_noise_savgol(self):
        return self.__raw_noise_savgol

    @raw_noise_savgol.setter
    def raw_noise_savgol(self, noise):
        self.__raw_noise_savgol = noise

    @property
    def norm_noise_savgol(self):
        return self.__norm_noise_savgol

    @norm_noise_savgol.setter
    def norm_noise_savgol(self, values):
        self.__norm_noise_savgol = values

    @property
    def ft(self):
        return self.__ft

    @ft.setter
    def ft(self, ft):
        if isinstance(ft, _FT):
            self.__ft = ft
        elif isinstance(ft, dict):
            self.__ft = _FT.from_dict(ft)
        else:
            raise TypeError

    @property
    def r(self) -> Union[None, numpy.ndarray]:
        # this alias is needed for larch
        return self.__ft.radius

    @r.setter
    def r(self, value: numpy.ndarray):
        # this alias is needed for larch
        self.__ft.radius = value

    @property
    def chir_mag(self) -> Union[None, numpy.ndarray]:
        # this alias is needed for larch
        return self.__ft.intensity

    @chir_mag.setter
    def chir_mag(self, value: numpy.ndarray):
        # this alias is needed for larch
        self.__ft.intensity = value

    @property
    def pymca_dict(self):
        return self.__pymca_dict

    @pymca_dict.setter
    def pymca_dict(self, ddict: dict):
        assert isinstance(ddict, dict)
        self.__pymca_dict = ddict

    @property
    def larch_dict(self):
        return self.__larch_dict

    @larch_dict.setter
    def larch_dict(self, ddict: dict):
        assert isinstance(ddict, dict)
        self.__larch_dict = ddict

    @property
    def shape(self) -> tuple:
        _energy_len = 0
        if self.__energy is not None:
            _energy_len = len(self.__energy)
        _mu_len = 0
        if self.__mu is not None:
            _mu_len = len(self.__mu)

        return (_energy_len, _mu_len)

    def load_from_dict(self, ddict: dict):
        assert isinstance(ddict, dict)

        def value_is_none(value):
            if hasattr(value, "decode"):
                value = value.decode("UTF-8")

            if isinstance(value, str):
                return value == "None"
            else:
                return value is None

        for key, value in ddict.items():
            if key in self.__key_mapper:
                prop = self.__key_mapper[key]
                if value_is_none(value=value):
                    prop.fset(self, None)
                else:
                    prop.fset(self, value)
            else:
                _logger.warning(f"Unable to set value for key {key}. Will be ignored")
        return self

    @staticmethod
    def from_dict(ddict: dict):
        x_pos = None
        y_pos = None
        if Spectrum._X_POS_KEY in ddict:
            x_pos = ddict.pop(Spectrum._X_POS_KEY)
        if Spectrum._Y_POS_KEY in ddict:
            y_pos = ddict.pop(Spectrum._Y_POS_KEY)
        spectrum = Spectrum(x=x_pos, y=y_pos)
        return spectrum.load_from_dict(ddict=ddict)

    def to_dict(self) -> dict:
        res = {
            self._X_POS_KEY: self.x,
            self._Y_POS_KEY: self.y,
            self._MU_KEY: self.mu,
            self._ENERGY_KEY: self.energy,
            self._FT_KEY: self.ft.to_dict(),
            self._NORMALIZED_MU_KEY: self.normalized_mu,
            self._NORMALIZED_ENERGY_KEY: self.normalized_energy,
            self._POST_EDGE_KEY: self.post_edge,
            self._NORMALIZED_BACKGROUND_KEY: self.pre_edge,
            self._EDGE_KEY: self.e0,
            self._CHI_KEY: self.chi,
            self._K_KEY: self.k,
            self._PYMCA_DICT_KEY: self.pymca_dict,
            self._LARCH_DICT_KEY: self.larch_dict,
        }
        return res

    def __str__(self):
        def add_info(str_, attr):
            assert hasattr(self, attr)
            sub_str = "- " + attr + ": " + str(getattr(self, attr)) + "\n"
            return str_ + sub_str

        main_info = ""
        for info in (
            "energy",
            "mu",
            "normalized_mu",
            "normalized_signal",
            "normalized_energy",
        ):
            main_info = add_info(str_=main_info, attr=info)
        return main_info

    def copy(self):
        return Spectrum.from_dict(self.to_dict())

    def _force_indexes(self, x, y):
        """This is protected because it might change display and
        the indexes should be defined during Spectra or Spectrum construction
        once for all"""
        self.__x = x
        self.__y = y


class _FT:
    _RADIUS_KEY = "FTRadius"

    _INTENSITY_KEY = "FTIntensity"

    _IMAGINARY_KEY = "FTImaginary"

    _K_KEY = "K"

    _WINDOW_WEIGHT_KEY = "WindowWeight"

    def __init__(self):
        self.__radius = None
        self.__intensity = None
        self.__imaginary = None
        self.__k = None
        self.__window_weight = None

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, radius):
        self.__radius = radius

    @property
    def intensity(self):
        return self.__intensity

    @intensity.setter
    def intensity(self, intensity):
        self.__intensity = intensity

    @property
    def imaginary(self):
        return self.__imaginary

    @imaginary.setter
    def imaginary(self, imaginery):
        self.__imaginary = imaginery

    @property
    def k(self):
        return self.__k

    @k.setter
    def k(self, k):
        self.__k = k

    @property
    def window_weight(self):
        return self.__window_weight

    @window_weight.setter
    def window_weight(self, window_weight):
        self.__window_weight = window_weight

    def to_dict(self) -> dict:
        res = {
            self._RADIUS_KEY: self.radius,
            self._INTENSITY_KEY: self.intensity,
            self._IMAGINARY_KEY: self.imaginary,
            self._K_KEY: self.k,
            self._WINDOW_WEIGHT_KEY: self.window_weight,
        }
        return res

    def load_from_dict(self, ddict: dict):
        if self._RADIUS_KEY in ddict:
            self.radius = ddict[self._RADIUS_KEY]
        if self._INTENSITY_KEY in ddict:
            self.intensity = ddict[self._INTENSITY_KEY]
        if self._IMAGINARY_KEY in ddict:
            self.imaginary = ddict[self._IMAGINARY_KEY]
        if self._K_KEY in ddict:
            self.k = ddict[self._K_KEY]
        if self._WINDOW_WEIGHT_KEY in ddict:
            self.window_weight = ddict[self._WINDOW_WEIGHT_KEY]

    @staticmethod
    def from_dict(ddict: dict):
        res = _FT()
        res.load_from_dict(ddict=ddict)
        return res
