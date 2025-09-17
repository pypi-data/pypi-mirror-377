import logging

from ewoksorange.gui.orange_imports import gui
from PyMca5.PyMcaGui.physics.xas.XASNormalizationParameters import (
    XASNormalizationParameters,
)
from silx.gui import qt
from silx.gui.plot import LegendSelector

from est.core.process.pymca.normalization import PyMca_normalization
from est.gui.e0calculator import E0CalculatorDialog
from est.gui.XasObjectViewer import ViewType
from est.gui.XasObjectViewer import XasObjectViewer
from est.gui.XasObjectViewer import _plot_edge
from est.gui.XasObjectViewer import _plot_norm
from est.gui.XasObjectViewer import _plot_post_edge
from est.gui.XasObjectViewer import _plot_pre_edge
from orangecontrib.est.process import EstProcessWidget
from orangecontrib.est.widgets.container import _ParameterWindowContainer

_logger = logging.getLogger(__file__)


class _XASNormalizationParametersPatched(XASNormalizationParameters):
    """This class will try to patch the XASNormalizationParameters with the
    E0Calculation widget"""

    sigE0CalculationRequested = qt.Signal()
    """Signal emitted when E0 computation is required"""

    def __init__(self, *args, **kwargs):
        XASNormalizationParameters.__init__(self, *args, **kwargs)
        # add E0CalculationWidget if can
        try:
            self.__addE0CalculationDialog()
        except Exception as e:
            _logger.warning("Fail to add the E0CalculationDialog. Reason is", str(e))
        else:
            self._e0CalcPB.pressed.connect(self._launchE0Calculator)

    def setE0(self, e0):
        e0_min = self.e0SpinBox.minimum()
        e0_max = self.e0SpinBox.maximum()
        if not (e0_min <= e0 <= e0_max):
            _logger.warning(
                "given e0 value (%s) is invalid, value should be "
                "between %s and %s" % (e0, e0_min, e0_max)
            )

        params = self.getParameters()
        params["E0Value"] = e0
        params["E0Method"] = "Manual"
        self.setParameters(ddict=params, signal=False)

    def __addE0CalculationDialog(self):
        # check we know where to set the button
        for attr in ("e0SpinBox", "jumpLine", "e0CheckBox"):
            if not hasattr(self, attr):
                raise NameError(
                    "%s not defined - pymca version not " "recognized" % attr
                )
        for widget, widget_index in zip((self.e0SpinBox, self.jumpLine), (3, 5)):
            if self.layout().indexOf(widget) != widget_index:
                raise ValueError("XASNormalizationParameters layout is not recognized.")

        style = qt.QApplication.instance().style()
        icon = style.standardIcon(qt.QStyle.SP_FileDialogContentsView)
        self._e0CalcPB = qt.QPushButton(icon, "", self)
        self.layout().addWidget(self._e0CalcPB, 1, 2)

    def _launchE0Calculator(self, *args, **kwargs):
        self.sigE0CalculationRequested.emit()


class NormalizationWindow(qt.QMainWindow):
    """Widget embedding the pymca parameter window and the display of the
    data currently process"""

    sigE0CalculationRequested = qt.Signal()
    """Signal emitted when E0 computation is required"""

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        # xas object viewer
        mapKeys = ["mu", "NormalizedMu", "NormalizedSignal", "NormalizedBackground"]
        self.xasObjViewer = XasObjectViewer(mapKeys=mapKeys)
        self.xasObjViewer._spectrumViews[0]._plotWidget.getXAxis().setLabel(
            "Energy (eV)"
        )
        self.xasObjViewer._spectrumViews[0]._plotWidget.getYAxis().setLabel(
            "Absorption (a.u.)"
        )
        self.setCentralWidget(self.xasObjViewer)
        self._pymcaWindow = _ParameterWindowContainer(
            parent=self, parametersWindow=_XASNormalizationParametersPatched
        )
        dockWidget = qt.QDockWidget(parent=self)

        # pymca window
        dockWidget.setWidget(self._pymcaWindow)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, dockWidget)
        dockWidget.setAllowedAreas(qt.Qt.RightDockWidgetArea | qt.Qt.LeftDockWidgetArea)
        dockWidget.setFeatures(qt.QDockWidget.NoDockWidgetFeatures)

        # legend selector
        self.legendDockWidget = LegendSelector.LegendsDockWidget(
            parent=self, plot=self.xasObjViewer._spectrumViews[0]._plotWidget
        )
        self.legendDockWidget.setAllowedAreas(
            qt.Qt.RightDockWidgetArea | qt.Qt.LeftDockWidgetArea
        )
        self.legendDockWidget.setFeatures(qt.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self.legendDockWidget)

        # volume key selection
        self.addDockWidget(
            qt.Qt.RightDockWidgetArea, self.xasObjViewer._mapView.keySelectionDocker
        )

        # plot settings
        for ope in (_plot_edge, _plot_norm, _plot_post_edge, _plot_pre_edge):
            self.xasObjViewer._spectrumViews[0].addCurveOperation(ope)

        self.setWindowFlags(qt.Qt.Widget)

        # expose API
        self.setE0 = self._pymcaWindow._mainwidget.setE0

        # connect signal / slot
        self.xasObjViewer.viewTypeChanged.connect(self._updateLegendView)

        # set up
        self._updateLegendView()

    def getNCurves(self):
        return len(self.xasObjViewer._spectrumViews._plot.getAllCurves())

    def _updateLegendView(self):
        index, viewType = self.xasObjViewer.getViewType()
        self.legendDockWidget.setVisible(viewType is ViewType.spectrum)
        self.xasObjViewer._mapView.keySelectionDocker.setVisible(
            viewType is ViewType.map
        )


class NormalizationOW(EstProcessWidget, ewokstaskclass=PyMca_normalization):
    """
    Widget used for signal extraction
    """

    name = "normalization"
    description = "Progress spectra normalization"
    icon = "icons/normalization.png"
    priority = 1
    keywords = ["spectroscopy", "normalization"]

    want_main_area = True
    resizing_enabled = True

    def __init__(self):
        super().__init__()
        self._window = NormalizationWindow(parent=self)
        layout = gui.vBox(self.mainArea, "normalization").layout()
        layout.addWidget(self._window)
        self._window.xasObjViewer.setWindowTitle("spectra")

        norm_params = self.get_task_input_value("normalization", default=None)
        if norm_params is not None:
            self._window._pymcaWindow.setParameters(norm_params)

        # expose API
        self.setE0 = self._window.setE0

        # connect signals / slots
        pymcaWindowContainer = self._window._pymcaWindow
        pymcaWindowContainer.sigChanged.connect(self._updateProcess)
        if hasattr(pymcaWindowContainer._mainwidget, "sigE0CalculationRequested"):
            pymcaWindowContainer._mainwidget.sigE0CalculationRequested.connect(
                self._getE0FromDialog
            )

    def _updateProcess(self):
        self.update_default_inputs(
            normalization=self._window._pymcaWindow.getParameters()
        )
        self.handleNewSignals()

    def task_input_changed(self):
        xas_obj = self.get_task_input_value("xas_obj", default=None)
        if xas_obj is None:
            _logger.warning("no xas_obj. Unable to update the GUI")
            return
        if "e0" in xas_obj.configuration:
            self.setE0(xas_obj.configuration["e0"])

    def _getE0FromDialog(self):
        """Pop up an instance of E0CalculationDialog and get E0 from it"""
        if self._latest_xas_obj is None:
            return
        dialog = E0CalculatorDialog(xas_obj=self._latest_xas_obj, parent=None)
        if dialog.exec_():
            self.setE0(dialog.getE0())
