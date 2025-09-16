"""Tools to visualize spectra"""

import logging
from typing import Iterable

import numpy
import silx
from silx.gui import icons as silx_icons
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot1D
from silx.gui.plot.StackView import StackViewMainWindow
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser
from silx.utils.enum import Enum

from est.core.types import Spectrum
from est.core.types import XASObject
from est.core.utils.symbol import MU_CHAR
from est.gui import icons

_logger = logging.getLogger(__name__)

# median spectrum view
silx_version = silx.version.split(".")
if not (int(silx_version[0]) == 0 and int(silx_version[1]) <= 11):
    silx_plot_has_baseline_feature = True
else:
    silx_plot_has_baseline_feature = False
    _logger.warning(
        "a more recent of silx is required to display " "mean spectrum (0.12)"
    )


class ViewType(Enum):
    map = (0,)
    spectrum = (1,)


class _SpectrumViewAction(qt.QAction):
    def __init__(self, parent=None, iView=0):
        qt.QAction.__init__(self, "spectrum view", parent=parent)
        assert iView in (0, 1)  # for now we can only deal with two plot at max
        # otherwise no more icon color to display
        self._iView = iView
        if iView == 0:
            icon = "item-1dim"
        elif iView == 1:
            icon = "item-1dim-black"
        else:
            # if necessary: add more icons, this is the only limitation
            raise NotImplementedError("Only two spectrum views are maanged")
        spectrum_icon = icons.getQIcon(icon)
        self.setIcon(spectrum_icon)
        self.setCheckable(True)


class _MapViewAction(qt.QAction):
    def __init__(self, parent=None):
        qt.QAction.__init__(self, "map view", parent=parent)
        map_icon = silx_icons.getQIcon("image")
        self.setIcon(map_icon)
        self.setCheckable(True)


class XasObjectViewer(qt.QMainWindow):
    """Viewer dedicated to view a XAS object

    :param QObject parent: Qt parent
    :param list mapKeys: list of str keys to propose for the map display
    :param list spectrumsPlots: list of keys if several spectrum plot should be
                                proposed.
    """

    viewTypeChanged = qt.Signal()
    """emitted when the view type change"""

    def __init__(self, parent=None, mapKeys=None, spectrumPlots=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)

        # main stack widget
        self._mainWidget = qt.QWidget(parent=self)
        self._mainWidget.setLayout(qt.QVBoxLayout())
        self.setCentralWidget(self._mainWidget)
        # map view
        self._mapView = MapViewer(parent=self, keys=mapKeys)
        self._mainWidget.layout().addWidget(self._mapView)

        # spectrum view
        self._spectrumViews = []
        if spectrumPlots is not None:
            spectrum_views_ = spectrumPlots
        else:
            spectrum_views_ = ("",)
        for _ in range(len(spectrum_views_)):
            spectrumView = SpectrumViewer(parent=self)
            self._mainWidget.layout().addWidget(spectrumView)
            self._spectrumViews.append(spectrumView)
        # add toolbar
        toolbar = qt.QToolBar("")
        toolbar.setIconSize(qt.QSize(32, 32))
        self._spectrumViewActions = []
        self.view_actions = qt.QActionGroup(self)
        for iSpectrumView, tooltip in enumerate(spectrum_views_):
            spectrumViewAction = _SpectrumViewAction(parent=None, iView=iSpectrumView)
            self.view_actions.addAction(spectrumViewAction)
            self._spectrumViewActions.append(spectrumViewAction)
            spectrumViewAction.setToolTip(tooltip)
            toolbar.addAction(spectrumViewAction)
        self._mapViewAction = _MapViewAction()
        toolbar.addAction(self._mapViewAction)
        self.view_actions.addAction(self._mapViewAction)

        self.addToolBar(qt.Qt.LeftToolBarArea, toolbar)
        toolbar.setMovable(False)

        # connect signal / Slot
        self._mapViewAction.triggered.connect(self._updateView)
        for spectrumAction in self._spectrumViewActions:
            spectrumAction.triggered.connect(self._updateView)

        # initialize
        self._spectrumViewActions[0].setChecked(True)
        self._updateView()

    def _updateView(self, *arg, **kwargs):
        index, view_type = self.getViewType()
        self._mapView.setVisible(view_type is ViewType.map)
        for iView, spectrumView in enumerate(self._spectrumViews):
            spectrumView.setVisible(view_type is ViewType.spectrum and iView == index)
        self.viewTypeChanged.emit()

    def getViewType(self):
        if self._mapViewAction.isChecked():
            return None, ViewType.map
        else:
            for spectrumViewAction in self._spectrumViewActions:
                if spectrumViewAction.isChecked():
                    return spectrumViewAction._iView, ViewType.spectrum
        return None, None

    def setXASObj(self, xas_obj):
        self._mapView.clear()

        self._mapView.setXasObject(xas_obj)
        for spectrumView in self._spectrumViews:
            spectrumView.clear()
            spectrumView.setXasObject(xas_obj)


class MapViewer(qt.QWidget):
    """
    Widget to display different map of the spectra
    """

    sigFrameChanged = qt.Signal(int)
    """Signal emitter when the frame number has changed."""

    def __init__(self, parent=None, keys=None):
        """

        :param parent:
        :param keys: volume keys to display for the xasObject (Mu,
        NormalizedMu...)
        """
        assert keys is not None
        self._xasObj = None
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QVBoxLayout())
        self._mainWindow = StackViewMainWindow(parent=parent)
        self.layout().addWidget(self._mainWindow)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self._mainWindow.setKeepDataAspectRatio(True)
        self._mainWindow.setColormap(Colormap(name="temperature"))

        # define the keys combobox
        self._keyWidget = qt.QWidget(parent=self)
        self._keyWidget.setLayout(qt.QHBoxLayout())
        self._keyComboBox = qt.QComboBox(parent=self._keyWidget)
        for key in keys:
            self._keyComboBox.addItem(key)
        self._keyWidget.layout().addWidget(qt.QLabel("view: "))
        self._keyWidget.layout().addWidget(self._keyComboBox)
        self.keySelectionDocker = qt.QDockWidget(parent=self)
        self.keySelectionDocker.setContentsMargins(0, 0, 0, 0)
        self._keyWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._keyWidget.layout().setSpacing(0)
        self.keySelectionDocker.setWidget(self._keyWidget)
        # self._mainWindow.addDockWidget(qt.Qt.TopDockWidgetArea, dockWidget)
        self.keySelectionDocker.setAllowedAreas(qt.Qt.TopDockWidgetArea)
        self.keySelectionDocker.setFeatures(qt.QDockWidget.NoDockWidgetFeatures)

        # expose API
        self.getActiveImage = self._mainWindow.getActiveImage
        self.menuBar = self._mainWindow.menuBar

        # connect signal / slot
        self._keyComboBox.currentTextChanged.connect(self._updateView)
        self._mainWindow.sigFrameChanged.connect(self._shareFrameChangedSignal)

    def clear(self):
        self._mainWindow.clear()

    def getActiveKey(self):
        return self._keyComboBox.currentText()

    def setXasObject(self, xas_obj):
        self._xasObj = xas_obj
        self._updateView()

    def _updateView(self, *args, **kwargs):
        if self._xasObj is None:
            return
        # set the map view
        spectra_volume = self._xasObj.spectra.as_ndarray(self.getActiveKey())
        if spectra_volume.size:
            self._mainWindow.setStack(spectra_volume)
        else:
            self._mainWindow.clear()

    def getPlot(self):
        return self._mainWindow.getPlotWidget()

    def _shareFrameChangedSignal(self, frame):
        self.sigFrameChanged.emit(frame)

    def setPerspectiveVisible(self, b):
        """hide the dimension selection"""
        self._mainWindow.setOptionVisible(b)
        self._mainWindow._browser.setVisible(True)


class _ExtendedSliderWithBrowser(HorizontalSliderWithBrowser):
    def __init__(self, parent=None, name=None):
        HorizontalSliderWithBrowser.__init__(self, parent)
        self.layout().insertWidget(0, qt.QLabel(str(name + ":")))


class _CurveOperation:
    def __init__(
        self,
        x,
        y,
        legend,
        yaxis=None,
        linestyle=None,
        symbol=None,
        color=None,
        ylabel=None,
        baseline=None,
        alpha=1.0,
    ):
        self.x = x
        self.y = y
        self.legend = legend
        self.yaxis = yaxis
        self.linestyle = linestyle
        self.symbol = symbol
        self.color = color
        self.ylabel = ylabel
        self.baseline = baseline
        self.alpha = alpha


class _XMarkerOperation:
    def __init__(self, x, legend, color="blue", text=None):
        self.x = x
        self.legend = legend
        self.color = color
        self.text = text


class _YMarkerOperation:
    def __init__(self, y, legend, color="blue", text=None):
        self.y = y
        self.legend = legend
        self.color = color
        self.text = text


class _RawDataList(qt.QTableWidget):
    def __init__(self, parent):
        qt.QTableWidget.__init__(self, parent)
        self.clear()

    def setData(self, x: Iterable, y: Iterable):
        if len(x) != len(y):
            raise ValueError("x and y should have the same number of element")
        self.setRowCount(len(x))
        self.setHorizontalHeaderLabels(
            ["X (energy converted to eV)", "Y ({})".format(MU_CHAR)]
        )

        for i_row, (x_value, y_value) in enumerate(zip(x, y)):
            x_item = qt.QTableWidgetItem()
            x_item.setText(str(x_value))
            self.setItem(i_row, 0, x_item)
            y_item = qt.QTableWidgetItem()
            y_item.setText(str(y_value))
            self.setItem(i_row, 1, y_item)
        self.resizeColumnsToContents()

    def clear(self):
        super().clear()
        self.setHorizontalHeaderLabels(
            ["X (energy converted to eV)", "Y ({})".format(MU_CHAR)]
        )
        self.setRowCount(0)
        self.setColumnCount(2)
        self.setSortingEnabled(True)
        self.verticalHeader().hide()


class SpectrumViewer(qt.QMainWindow):
    sigSpectrumChanged = qt.Signal()
    """Signal emitted when the spectrum change"""

    def __init__(self, parent=None):
        self._curveOperations = []
        """List of callaback to produce plot regarding the XASObject.
        Callback function should return a _curve_operation"""
        qt.QMainWindow.__init__(self, parent)

        self.xas_obj = None

        self._plotWidget = Plot1D(parent=self)
        self._rawDataWidget = _RawDataList(parent=self)

        self._tabWidget = qt.QTabWidget(self)
        self._tabWidget.addTab(self._plotWidget, "plot")
        self._tabWidget.addTab(self._rawDataWidget, "data as text")

        self.setCentralWidget(self._tabWidget)

        # frame browsers
        dockWidget = qt.QDockWidget(self)

        frameBrowsers = qt.QWidget(parent=self)
        frameBrowsers.setLayout(qt.QVBoxLayout())
        frameBrowsers.layout().setContentsMargins(0, 0, 0, 0)

        self._dim1FrameBrowser = _ExtendedSliderWithBrowser(parent=self, name="dim 1")
        frameBrowsers.layout().addWidget(self._dim1FrameBrowser)
        self._dim2FrameBrowser = _ExtendedSliderWithBrowser(parent=self, name="dim 2")
        frameBrowsers.layout().addWidget(self._dim2FrameBrowser)
        dockWidget.setWidget(frameBrowsers)

        self.addDockWidget(qt.Qt.BottomDockWidgetArea, dockWidget)
        dockWidget.setAllowedAreas(qt.Qt.BottomDockWidgetArea)
        dockWidget.setFeatures(qt.QDockWidget.NoDockWidgetFeatures)

        # connect signal / slot
        self._dim1FrameBrowser.valueChanged.connect(self._updateSpectrumDisplayed)
        self._dim2FrameBrowser.valueChanged.connect(self._updateSpectrumDisplayed)

    def addCurveOperation(self, callbacks):
        """register an curve to display from Xasobject keys, and a legend

        :param callbacks: callback to call when displaying a specific curve
        :type: Union[list,tuple,function]
        """
        if isinstance(callbacks, (list, tuple)):
            for callback in callbacks:
                self.addCurveOperation(callback)
        else:
            self._curveOperations.append(callbacks)

    def clearCurveOperations(self):
        """Remove all defined curve operation"""
        self._curveOperations.clear()

    def setXasObject(self, xas_obj):
        self.xas_obj = xas_obj
        if self.xas_obj is None:
            self.clear()
        else:
            assert self.xas_obj.spectra.shape[0] >= 0
            assert self.xas_obj.spectra.shape[1] >= 0
            self._dim1FrameBrowser.setRange(0, self.xas_obj.spectra.shape[0] - 1)
            self._dim2FrameBrowser.setRange(0, self.xas_obj.spectra.shape[1] - 1)
            self._updateSpectrumDisplayed()

    def getCurrentSpectrum(self):
        """
        Return the spectrum currently selected
        """
        if self.xas_obj is None:
            return None
        dim1_index = self._dim1FrameBrowser.value()
        dim2_index = self._dim2FrameBrowser.value()
        if dim1_index < 0 or dim2_index < 0:
            return None

        assert dim1_index >= 0
        assert dim2_index >= 0

        return self.xas_obj.get_spectrum(dim1_index, dim2_index)

    def _updateSpectrumDisplayed(self, *args, **kwargs):
        dim1_index = self._dim1FrameBrowser.value()
        spectrum = self.getCurrentSpectrum()
        if spectrum is None:
            return
        # update raw data tab
        self._rawDataWidget.setData(x=spectrum.energy, y=spectrum.mu)
        # update plot tab
        for operation in self._curveOperations:
            curves = operation(spectrum)
            if curves is None:
                continue
            else:
                curves = list(curves)
            if silx_plot_has_baseline_feature is True:
                new_curves_op = operation(self.xas_obj, index=dim1_index)
                if new_curves_op is not None:
                    curves.extend(new_curves_op)
            for res in curves:
                # result can be None or nan if the processing fails. So in this
                # case we won't display anything
                if res is not None:
                    if isinstance(res, _CurveOperation):
                        if res.x is None or res.x is numpy.nan:
                            continue

                        kwargs = {
                            "x": res.x,
                            "y": res.y,
                            "legend": res.legend,
                            "yaxis": res.yaxis,
                            "linestyle": res.linestyle,
                            "symbol": res.symbol,
                            "color": res.color,
                            "ylabel": res.ylabel,
                        }
                        if silx_plot_has_baseline_feature:
                            kwargs["baseline"] = (res.baseline,)

                        curve = self._plotWidget.addCurve(**kwargs)
                        if isinstance(curve, str):
                            # silx < 2.0
                            curve = self._plotWidget.getCurve(curve)
                        curve.setAlpha(res.alpha)
                    elif isinstance(res, _XMarkerOperation):
                        if res.x is None or res.x is numpy.nan:
                            continue

                        self._plotWidget.addXMarker(
                            x=res.x,
                            color=res.color,
                            legend=res.legend,
                            text=res.text,
                        )
                    elif isinstance(res, _YMarkerOperation):
                        if res.y is None or res.y is numpy.nan:
                            continue

                        self._plotWidget.addYMarker(
                            y=res.y,
                            color=res.color,
                            legend=res.legend,
                            text=res.text,
                        )
                    else:
                        raise TypeError(
                            "this type of operation {} is not recognized. Details {}".format(
                                type(res), res
                            )
                        )
        self.sigSpectrumChanged.emit()

    def clear(self):
        self._plotWidget.clear()
        self._dim1FrameBrowser.setMaximum(-1)
        self._dim2FrameBrowser.setMaximum(-1)
        self._rawDataWidget.clear()

    def setYAxisLogarithmic(self, val):
        self._plotWidget.setYAxisLogarithmic(val)


COLOR_MEAN = "black"
COLOR_STD = "grey"


def _get_energy_for(obj, values):
    """Depending on if this is pymca or larch we might need to get
    the normalized energy instead of the energy"""
    if values is None:
        return None
    elif len(values) == len(obj.energy):
        return obj.energy
    else:
        return obj.normalized_energy


def _plot_norm(obj, **kwargs):
    if isinstance(obj, XASObject):
        assert "index" in kwargs
        index_dim1 = kwargs["index"]
        spectra = obj.spectra.as_ndarray("normalized_mu")
        spectra = spectra[:, index_dim1, :]
        mean = numpy.mean(spectra, axis=1)
        std = numpy.std(spectra, axis=1)
        energy = _get_energy_for(obj, mean)
        c1 = _CurveOperation(
            x=energy, y=mean, color=COLOR_MEAN, legend="mean norm", alpha=0.5
        )
        c2 = _CurveOperation(
            x=obj.normalized_energy,
            y=mean + std,
            baseline=mean - std,
            color=COLOR_STD,
            legend="std norm",
            alpha=0.5,
        )
        return c1, c2
    elif isinstance(obj, Spectrum):
        if obj.normalized_mu is None:
            _logger.error("norm has not been computed yet")
            return
        energy = _get_energy_for(obj, obj.normalized_mu)
        c1 = _CurveOperation(
            x=energy, y=obj.normalized_mu, legend="norm", color="black"
        )
        operations = [
            c1,
        ]
        try:
            flat = obj.flat
            operations.append(
                _CurveOperation(
                    x=energy,
                    y=flat,
                    legend="flat normalized mu",
                    color="blue",
                )
            )
        except Exception:
            pass
        return tuple(operations)


def _plot_flatten_mu(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if obj.flatten_mu is None:
        _logger.error("norm_area has not been computed yet")
        return None
    energy = _get_energy_for(obj, obj.flatten_mu)

    return (
        _CurveOperation(
            x=energy, y=obj.flatten_mu, legend="flatten_mu", color="orange"
        ),
    )


def _plot_mback_mu(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "mback_mu"):
        _logger.error("mback_mu has not been computed yet")
        return
    energy = _get_energy_for(obj, obj.mback_mu)

    return (
        _CurveOperation(x=energy, y=obj.mback_mu, legend="mback_mu", color="orange"),
    )


def _plot_pre_edge(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if obj.pre_edge is None:
        _logger.error("pre_edge has not been computed yet")
        return
    energy = _get_energy_for(obj, obj.pre_edge)
    return (
        _CurveOperation(x=energy, y=obj.pre_edge, legend="pre edge", color="green"),
    )


def _plot_post_edge(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if obj.post_edge is None:
        _logger.error("post_edge has not been computed yet")
        return
    energy = _get_energy_for(obj, obj.post_edge)
    return (
        _CurveOperation(x=energy, y=obj.post_edge, legend="post edge", color="blue"),
    )


def _plot_edge(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "e0"):
        _logger.error("e0 has not been computed yet")
        return
    return (_XMarkerOperation(x=obj.e0, legend="edge", color="yellow"),)


def _plot_raw(obj, **kwargs):
    if isinstance(obj, Spectrum):
        if obj.mu is None:
            _logger.error("mu not existing")
            return
        energy = _get_energy_for(obj, obj.mu)
        return (_CurveOperation(x=energy, y=obj.mu, legend="raw mu", color="red"),)
    elif isinstance(obj, XASObject):
        assert "index" in kwargs
        index_dim1 = kwargs["index"]
        spectra = obj.spectra.as_ndarray("normalized_mu")
        spectra = spectra[:, index_dim1, :]
        mean = numpy.mean(spectra, axis=1)
        std = numpy.std(spectra, axis=1)
        energy = _get_energy_for(obj, obj.normalized_energy)

        return (
            _CurveOperation(
                x=energy, y=mean, color=COLOR_MEAN, legend="mean mu", alpha=0.5
            ),
            _CurveOperation(
                x=energy,
                y=mean + std,
                baseline=mean - std,
                color=COLOR_STD,
                legend="mu std",
                alpha=0.5,
            ),
        )
    else:
        raise ValueError("input type is not manged")


def _plot_fpp(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "fpp"):
        _logger.error("fpp has not been computed yet")
        return
    energy = _get_energy_for(obj, obj.fpp)
    return (_CurveOperation(x=energy, y=obj.fpp, legend="fpp", color="blue"),)


def _plot_f2(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "f2"):
        _logger.error("f2 has not been computed yet")
        return
    energy = _get_energy_for(obj, obj.f2)
    return (_CurveOperation(x=energy, y=obj.f2, legend="f2", color="orange"),)


def _plot_chi(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "k"):
        _logger.error("k not computed, unable to display it")
        return
    if not hasattr(obj, "chi"):
        _logger.error("chi not computed, unable to display it")
        return
    return (_CurveOperation(x=obj.k, y=obj.chi, legend="chi(k)"),)


def _plot_chir_mag(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "r"):
        _logger.error("r not computed, unable to display it")
        return
    if not hasattr(obj, "chir_mag"):
        _logger.error("chir_mag not computed, unable to display it")
        return
    return (_CurveOperation(x=obj.r, y=obj.chir_mag, legend="|FT(R)|"),)


def _plot_chir_re(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "r"):
        _logger.error("r not computed, unable to display it")
        return
    if not hasattr(obj, "chir_re"):
        _logger.error("chir_re not computed, unable to display it")
        return
    return (_CurveOperation(x=obj.r, y=obj.chir_re, legend="Re(FT(R))"),)


def _plot_chir_imag(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "r"):
        _logger.error("r not computed, unable to display it")
        return
    if not hasattr(obj, "chir_im"):
        _logger.error("chir_im not computed, unable to display it")
        return
    return (_CurveOperation(x=obj.r, y=obj.chir_im, legend="Im(FT(R))"),)


def _plot_chi_weighted_k(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "k"):
        _logger.error("k not computed, unable to display it")
        return
    if not hasattr(obj, "chi_weighted_k"):
        _logger.error("chi_weighted_k not computed, unable to display it")
        return
    return (_CurveOperation(x=obj.k, y=obj.chi_weighted_k, legend="chi(k) * k_weight"),)


def plot_spectrum(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    energy = _get_energy_for(obj, obj.mu)
    return (
        _CurveOperation(
            x=energy, y=obj.mu, legend="spectrum", yaxis=None, color="blue"
        ),
    )


def _plot_bkg(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if "bkg" not in obj.larch_dict:
        _logger.error("missing bkg parameter, unable to compute bkg plot")
        return
    energy = _get_energy_for(obj, obj.larch_dict["bkg"])
    return (
        _CurveOperation(
            x=energy, y=obj.larch_dict["bkg"], legend="bkg", yaxis=None, color="red"
        ),
    )


# def _plot_knots(obj, **kwargs):
#     if not isinstance(obj, Spectrum):
#         return None
#     if not hasattr(obj, "autobk_details"):
#         _logger.error("missing bkg parameter, unable to compute bkg plot")
#         return
#     if not hasattr(obj.autobk_details, "knots_y"):
#         _logger.error("missing knots_y, unable to print output")
#         return
#     if not hasattr(obj.autobk_details, "knots_e"):
#         _logger.error("missing knots_e, unable to print output")
#         return

#     return (
#         _CurveOperation(
#             x=obj.autobk_details.knots_e,  # knots_e does not exists anymore. We would need to recompute it. Not trivial. Not sure we need this plot
#             y=obj.autobk_details.knots_y,
#             legend="knots",
#             yaxis=None,
#             color="green",
#             linestyle="",
#             symbol="o",
#         ),
#     )


def _exafs_signal_plot(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None

    if obj.k is None or "KMin" not in obj.pymca_dict or "KMax" not in obj.pymca_dict:
        _logger.error(
            "k or some keys are missing in pymca_dict (`KMin`, `KMax`). Is Exafs has been executed ?"
        )
        return None

    k = obj.k
    if "KMin" not in obj.pymca_dict:
        obj.pymca_dict["KMin"] = k.min()
    if "KMax" not in obj.pymca_dict:
        obj.pymca_dict["KMax"] = k.max()

    idx = (obj.k >= obj.pymca_dict["KMin"]) & (obj.k <= obj.pymca_dict["KMax"])
    x = k[idx]
    y = obj.chi[idx]
    return (_CurveOperation(x=x, y=y, legend="EXAFSSignal (chi)"),)


def _exafs_postedge_plot(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None

    if (
        obj.k is None
        or "PostEdgeB" not in obj.pymca_dict
        or "KMin" not in obj.pymca_dict
        or "KMax" not in obj.pymca_dict
    ):
        _logger.error(
            "k or some keys are missing in pymca_dict (`PostEdgeB`, `KMin`, `KMax`). Is Exafs has been executed ?"
        )
        return None

    k = obj.k
    if "KMin" not in obj.pymca_dict:
        obj.pymca_dict["KMin"] = k.min()
    if "KMax" not in obj.pymca_dict:
        obj.pymca_dict["KMax"] = k.max()

    idx = (obj.k >= obj.pymca_dict["KMin"]) & (obj.k <= obj.pymca_dict["KMax"])

    x = obj.k[idx]
    y = obj.pymca_dict["PostEdgeB"][idx]
    return (_CurveOperation(x=x, y=y, legend="PostEdge"),)


def _exafs_knots_plot(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None

    if "KnotsX" not in obj.pymca_dict or "KnotsY" not in obj.pymca_dict:
        _logger.error(
            "`KnotsX` or `KnotsY` is missing from spectrum pymca_dict. Unable to plot it"
        )
        return
    x = obj.pymca_dict["KnotsX"]
    y = obj.pymca_dict["KnotsY"]
    return (_CurveOperation(x=x, y=y, legend="Knots", linestyle="", symbol="o"),)


def _normalized_exafs(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    assert isinstance(obj, Spectrum)
    if obj.k is None or "EXAFSNormalized" not in obj.pymca_dict:
        _logger.error(
            "k not computed or `EXAFSNormalized` not in the pymca_dict. Unable to plot"
        )
        return None

    if "KWeight" in obj.pymca_dict:
        if obj.pymca_dict["KWeight"] == 1:
            ylabel = "EXAFS Signal * k"
        else:
            ylabel = "EXAFS Signal * k^%d" % obj.pymca_dict["KWeight"]
    else:
        ylabel = "EXAFS Signal"

    idx = (obj.k >= obj.pymca_dict["KMin"]) & (obj.k <= obj.pymca_dict["KMax"])

    return (
        _CurveOperation(
            x=obj.k[idx],
            y=obj.pymca_dict["EXAFSNormalized"][idx],
            legend="Normalized EXAFS",
            ylabel=ylabel,
        ),
    )


def _ft_window_plot(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if obj.ft.k is None:
        _logger.error("missing key 'K': unable to compute normalized EXAFS")
        return
    if obj.ft.window_weight is None:
        _logger.error("missing key 'WindowWeight': unable to compute normalized EXAFS")
        return
    return (
        _CurveOperation(
            x=obj.ft.k,
            y=obj.ft.window_weight,
            legend="FT Window",
            yaxis="right",
            color="red",
        ),
    )


def _ft_intensity_plot(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if obj.ft.radius is None:
        _logger.error("missing key 'FTRadius': unable to compute intensity plot")
        return
    if obj.ft.intensity is None:
        _logger.error("missing key 'FTIntensity': unable to compute intensity plot")
        return
    return (
        _CurveOperation(x=obj.ft.radius, y=obj.ft.intensity, legend="FT Intensity"),
    )


def _ft_imaginary_plot(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if obj.ft.radius is None:
        _logger.error("missing key 'FTRadius': unable to compute imaginary plot")
        return
    if obj.ft.intensity is None:
        _logger.error("missing key 'FTIntensity': unable to compute imaginary plot")
        return
    return (
        _CurveOperation(
            x=obj.ft.radius,
            y=obj.ft.imaginary,
            legend="FT Imaginary",
            color="red",
        ),
    )


def _plot_noise_savgol(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "noise_savgol"):
        _logger.error("noise has not been computed yet")
        return
    energy = obj.energy
    return (
        _CurveOperation(x=energy, y=obj.noise_savgol, legend="noise", color="blue"),
        _XMarkerOperation(
            x=obj.larch_dict["noise_e_min"],
            legend="e_min",
            color="gray",
            text="E start",
        ),
        _XMarkerOperation(
            x=obj.larch_dict["noise_e_max"],
            legend="e_max",
            color="brown",
            text="E end",
        ),
    )


def _plot_norm_noise_savgol(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "norm_noise_savgol"):
        _logger.error("noise has not been computed yet")
        return
    return (
        _YMarkerOperation(
            y=obj.norm_noise_savgol,
            legend="normalized noise",
            color="red",
            text="mean normalized noise",
        ),
    )


def _plot_raw_noise_savgol(obj, **kwargs):
    if not isinstance(obj, Spectrum):
        return None
    if not hasattr(obj, "raw_noise_savgol"):
        _logger.error("noise has not been computed yet")
        return
    return (
        _YMarkerOperation(
            y=obj.raw_noise_savgol,
            legend="raw noise",
            color="orange",
            text="mean raw noise",
        ),
    )
