"""Tools to select energy roi"""

from typing import Optional
from typing import Union

from silx.gui import qt

from est.core.types.xasobject import XASObject
from est.gui.SpectrumPlot import SpectrumPlot


class _RoiSettings(qt.QWidget):
    sigValueChanged = qt.Signal()
    """signal emitted when roi value is changed"""

    MAX_VALUE = 999999999

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QFormLayout())
        self._minE = qt.QDoubleSpinBox(self)
        self._minE.setRange(0, _RoiSettings.MAX_VALUE)
        self._minE.setValue(0)
        self.layout().addRow("min E", self._minE)
        self._maxE = qt.QDoubleSpinBox(self)
        self._maxE.setRange(0, _RoiSettings.MAX_VALUE)
        self._maxE.setValue(_RoiSettings.MAX_VALUE)
        self.layout().addRow("max E", self._maxE)

        # connect signal / slot
        self._minE.editingFinished.connect(self._changed)
        self._maxE.editingFinished.connect(self._changed)

    def _changed(self):
        self.sigValueChanged.emit()

    def setRangeE(self, min_E, max_E):
        old = self.blockSignals(True)
        try:
            self._minE.setValue(min_E)
            self._maxE.setValue(max_E)
        finally:
            self.blockSignals(old)
        self.sigValueChanged.emit()

    def getMinE(self):
        return self._minE.value()

    def setMinE(self, value):
        self._minE.setValue(value)

    def getMaxE(self):
        return self._maxE.value()

    def setMaxE(self, value):
        self._maxE.setValue(value)

    def getROI(self):
        return self.getMinE(), self.getMaxE()

    def setROI(self, roi):
        min, max = roi
        self.setMinE(min)
        self.setMaxE(max)

    def hasntBeenModified(self):
        return (self._minE.value() == 0) and (
            self._maxE.value() == _RoiSettings.MAX_VALUE
        )


class EnergyRoiWidget(qt.QMainWindow):
    sigROIChanged = qt.Signal()
    """signal emit when the ROI is updated"""

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)

        # plot
        self._plot = SpectrumPlot(self)
        self.setCentralWidget(self._plot)

        # roi settings
        self._widget = _RoiSettings(self)
        dockWidget = qt.QDockWidget(parent=self)
        dockWidget.setWidget(self._widget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, dockWidget)
        dockWidget.setAllowedAreas(qt.Qt.RightDockWidgetArea | qt.Qt.LeftDockWidgetArea)
        dockWidget.setFeatures(qt.QDockWidget.NoDockWidgetFeatures)

        # add Markers
        self._minEMarker = self._plot.addXMarker(
            self._widget.getMinE(),
            legend="from",
            color="red",
            draggable=True,
            text="min E",
        )

        self._maxEMarker = self._plot.addXMarker(
            self._widget.getMaxE(),
            legend="to",
            color="red",
            draggable=True,
            text="max E",
        )

        # expose API
        self.setROI = self._widget.setROI
        self.getROI = self._widget.getROI

        # connect signal / slot
        self._widget.sigValueChanged.connect(self._updateROIAnchors)
        self._getMinMarker().sigDragFinished.connect(self._updateMinValuefromMarker)
        self._getMaxMarker().sigDragFinished.connect(self._updateMaxValuefromMarker)

    def setXasObject(self, xas_obj: Union[XASObject, dict, None]):
        if xas_obj is None:
            self._plot.clear()
        else:
            if isinstance(xas_obj, dict):
                xas_obj = XASObject.from_dict(xas_obj)
            if not isinstance(xas_obj, XASObject):
                raise TypeError(str(type(xas_obj)))
            self._plot.setXasObject(xas_obj)
            if self._widget.hasntBeenModified() and xas_obj.energy is not None:
                if xas_obj.energy.size:
                    self._widget.setRangeE(xas_obj.energy.min(), xas_obj.energy.max())

    def getXasObject(self) -> Optional[XASObject]:
        return self._plot._plot.xas_obj

    def _getMinMarker(self):
        return self._plot._plot._plotWidget._getMarker(self._minEMarker)

    def _getMaxMarker(self):
        return self._plot._plot._plotWidget._getMarker(self._maxEMarker)

    def _updateROIAnchors(self):
        oldMinMarker = self._getMinMarker().blockSignals(True)
        oldMaxMarker = self._getMaxMarker().blockSignals(True)

        self._getMinMarker().setPosition(self._widget.getMinE(), 0)
        self._getMaxMarker().setPosition(self._widget.getMaxE(), 0)

        self._getMinMarker().blockSignals(oldMinMarker)
        self._getMaxMarker().blockSignals(oldMaxMarker)
        self.sigROIChanged.emit()

    def _updateMinValuefromMarker(self):
        old = self._widget.blockSignals(True)
        self._widget.setMinE(self._getMinMarker().getPosition()[0])
        self._widget.blockSignals(old)
        self.sigROIChanged.emit()

    def _updateMaxValuefromMarker(self):
        old = self._widget.blockSignals(True)
        self._widget.setMaxE(self._getMaxMarker().getPosition()[0])
        self._widget.blockSignals(old)
        self.sigROIChanged.emit()
