from __future__ import annotations

from typing import Optional

from silx.io.url import DataUrl

from est.core.types import dimensions as dimensions_mod
from est.units import as_energy_unit
from est.units import ur


class InputInformation:
    """
    Utility class to store information to generate XASObject
    """

    def __init__(
        self,
        spectra_url: DataUrl | None = None,
        channel_url: DataUrl | None = None,
        config_url: DataUrl | None = None,
        dimensions: Optional[dimensions_mod.DimensionsType] = None,
        energy_unit=ur.eV,
        I0_url: DataUrl | None = None,
        I1_url: DataUrl | None = None,
        I2_url: DataUrl | None = None,
        mu_ref_url: DataUrl | None = None,
        is_concatenated: bool = False,
        trim_concatenated_n_points: int = 0,
        skip_concatenated_n_spectra: int = 0,
        concatenated_spectra_section_size: int = 0,
    ):
        # main information
        self.spectra_url = spectra_url
        self.channel_url = channel_url
        self.config_url = config_url
        self.dimensions = dimensions_mod.parse_dimensions(dimensions)
        self.energy_unit = energy_unit
        self.is_concatenated = is_concatenated
        self.trim_concatenated_n_points = trim_concatenated_n_points
        self.skip_concatenated_n_spectra = skip_concatenated_n_spectra
        self.concatenated_spectra_section_size = concatenated_spectra_section_size

        # "fancy information"
        self.I0_url = I0_url
        self.I1_url = I1_url
        self.I2_url = I2_url
        self.mu_ref_url = mu_ref_url

    def to_dict(self) -> dict:
        def dump_url(url):
            if url in (None, ""):
                return None
            else:
                return url.path()

        return {
            "spectra_url": dump_url(self.spectra_url),
            "channel_url": dump_url(self.channel_url),
            "config_url": dump_url(self.config_url),
            "dimensions": self.dimensions,
            "energy_unit": str(self.energy_unit),
            "I0_url": dump_url(self.I0_url),
            "I1_url": dump_url(self.I1_url),
            "I2_url": dump_url(self.I2_url),
            "mu_ref_url": dump_url(self.mu_ref_url),
            "is_concatenated": self.is_concatenated,
            "trim_concatenated_n_points": self.trim_concatenated_n_points,
            "skip_concatenated_n_spectra": self.skip_concatenated_n_spectra,
            "concatenated_spectra_section_size": self.concatenated_spectra_section_size,
        }

    @staticmethod
    def from_dict(ddict: dict):
        def load_url(url_name: str):
            url = ddict.get(url_name, None)

            if url in (None, ""):
                return None
            else:
                return DataUrl(path=url)

        return InputInformation(
            spectra_url=load_url("spectra_url"),
            channel_url=load_url("channel_url"),
            dimensions=ddict.get("dimensions", None),
            config_url=load_url("config_url"),
            energy_unit=as_energy_unit(ddict.get("energy_unit", None)),
            I0_url=load_url("I0_url"),
            I1_url=load_url("I1_url"),
            I2_url=load_url("I2_url"),
            mu_ref_url=load_url("mu_ref_url"),
            is_concatenated=ddict.get("is_concatenated", False),
            trim_concatenated_n_points=ddict.get("trim_concatenated_n_points", 0),
            skip_concatenated_n_spectra=ddict.get("skip_concatenated_n_spectra", 0),
            concatenated_spectra_section_size=ddict.get(
                "concatenated_spectra_section_size", 0
            ),
        )
