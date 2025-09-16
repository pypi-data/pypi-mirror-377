from typing import Dict
from typing import Optional
from typing import Sequence

from ewokscore import Task

_Y_TO_X_NAME = {
    "mu": "energy",
    "normalized_mu": "energy",
    "flatten_mu": "energy",
    "chi": "k",
    "chi_weighted_k": "k",
    "ft_mag": "R",
    "noise_savgol": "energy",
}
_Y_TO_INFO_ATTRS = {
    "normalized_mu": ["e0", "edge_step"],
    "flatten_mu": ["e0", "edge_step"],
    "noise_savgol": ["raw_noise_savgol", "norm_noise_savgol", "edge_step", "e0"],
}
_Y_TO_HLINE_ATTRS = {"noise_savgol": ["raw_noise_savgol"]}
_Y_TO_VLINE_ATTRS = {"noise_savgol": ["noise_e_min", "noise_e_max"]}
_LARCH_ATTRS = ("noise_e_min", "noise_e_max")
_INFO_ATTRS_TO_NAMES = {
    "raw_noise_savgol": "raw_noise",
    "norm_noise_savgol": "norm_noise",
    "edge_step": "edge_step",
}
_LABELS = {
    "energy": "Energy (eV)",
    "mu": "μ(E)",
    "normalized_mu": "Norm(μ(E))",
    "flatten_mu": "Flat(μ(E))",
    "chi": "χ(k)",
    "chi_weighted_k": "k^{kweight} χ(k) (Å^-{kweight})",
    "ft_mag": "|FT(R)| (Å^-{kweightp1})",
    "k": "Wavenumber (Å^-1)",
    "R": "Radius (Å)",
    "noise_savgol": "Noise(μ)",
}


def process_plotspectrumdata(
    spectrum, plot_names: Optional[Sequence] = None
) -> Dict[str, dict]:
    kweight = spectrum.larch_dict["xftf_k_weight"]
    params = {"kweight": kweight, "kweightp1": kweight + 1}
    plot_data = dict()
    if not plot_names:
        plot_names = ("flatten_mu", "chi_weighted_k", "ft_mag", "noise_savgol")
    for yname in plot_names:
        plot_data[yname] = get_plotspectrumdata(spectrum, yname, params)
    return plot_data


def get_plotspectrumdata(spectrum, yname, params):
    xname = _Y_TO_X_NAME[yname]
    if yname == "ft_mag":
        x = spectrum.ft.radius
        y = spectrum.ft.intensity
    else:
        x = getattr(spectrum, xname)
        y = getattr(spectrum, yname)

    xlabel = _LABELS[xname]
    ylabel = _LABELS[yname]
    xlabel = xlabel.format(**params)
    ylabel = ylabel.format(**params)

    info = dict()
    for attr in _Y_TO_INFO_ATTRS.get(yname, list()):
        value = get_spectrum_value(spectrum, attr)
        key = _INFO_ATTRS_TO_NAMES.get(attr, attr)
        info[key] = value

    hlines = [
        get_spectrum_value(spectrum, attr)
        for attr in _Y_TO_HLINE_ATTRS.get(yname, list())
    ]
    vlines = [
        get_spectrum_value(spectrum, attr)
        for attr in _Y_TO_VLINE_ATTRS.get(yname, list())
    ]

    return {
        "name": yname,
        "x": x,
        "y": y,
        "xlabel": xlabel,
        "ylabel": ylabel,
        "info": info,
        "hlines": hlines,
        "vlines": vlines,
    }


def get_spectrum_value(spectrum, attr):
    if attr in _LARCH_ATTRS:
        return spectrum.larch_dict[attr]
    else:
        return getattr(spectrum, attr)


class PlotSpectrumData(
    Task,
    input_names=["xas_obj"],
    optional_input_names=["plot_names"],
    output_names=["plot_data"],
):
    def run(self):
        self.outputs.plot_data = [
            process_plotspectrumdata(spectrum, plot_names=self.inputs.plot_names)
            for spectrum in self.inputs.xas_obj.spectra.data.flat
        ]
