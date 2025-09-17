"""Tool to display Spectra maps and estimate E0"""

import functools

import numpy
from silx.gui import qt
from silx.gui.plot.items.roi import RectangleROI
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.utils.enum import Enum

from est.core.types import XASObject
from est.gui.XasObjectViewer import MapViewer


class E0ComputationMethod(Enum):
    """Methods to compute E0"""

    MEAN = "mean"
    MEDIAN = "median"


class _ComputationScale(Enum):
    ALL = "all"
    CURRENT = "current"


class E0CalculatorDialog(qt.QDialog):
    """Dialog to compute E0 mean or median in a ROI"""

    def __init__(self, parent=None, xas_obj=None):
        qt.QDialog.__init__(self, parent=parent)
        if xas_obj is None:
            raise ValueError("xas_obj should not be None")

        self._methodToUse = None
        # set when the user quit the dialog and define to use mean or median

        # add the E0Calculator
        self._mainWidget = E0Calculator(parent=self, xas_obj=xas_obj)
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self._mainWidget)

        # add the buttons
        style = qt.QApplication.instance().style()
        icon = style.standardIcon(qt.QStyle.SP_DialogApplyButton)

        _buttons = qt.QDialogButtonBox(parent=self)
        self._useMedian = qt.QPushButton(icon, "use median", self)
        _buttons.addButton(self._useMedian, qt.QDialogButtonBox.ActionRole)
        self._useMean = qt.QPushButton(icon, "use mean", self)
        _buttons.addButton(self._useMean, qt.QDialogButtonBox.ActionRole)
        _buttons.addButton(qt.QDialogButtonBox.Cancel)
        self.layout().addWidget(_buttons)

        # connect signal / slot
        _buttons.rejected.connect(self.reject)
        self._useMean.released.connect(
            functools.partial(self.validateMethodToUse, E0ComputationMethod.MEAN)
        )
        self._useMedian.released.connect(
            functools.partial(self.validateMethodToUse, E0ComputationMethod.MEDIAN)
        )

    def validateMethodToUse(self, method):
        """Define the method to use and close the dialog"""
        method = E0ComputationMethod.from_value(method)
        assert method in (None, E0ComputationMethod.MEDIAN, E0ComputationMethod.MEAN)
        self._methodToUse = method
        self.accept()

    def getE0(self):
        if self._methodToUse is None:
            return None
        else:
            return self._mainWidget.getE0(method=self._methodToUse)


class E0Calculator(qt.QMainWindow):
    """Interface to compute E0 mean and median values from a ROI"""

    sigE0Changed = qt.Signal(float)
    """Signal emitted when E0 is changing"""

    def __init__(self, parent=None, xas_obj=None):
        assert isinstance(xas_obj, (XASObject, type(None)))
        self._xas_obj = None

        qt.QMainWindow.__init__(self, parent=parent)
        # map view
        self._muView = MapViewer(parent=self, keys=("mu",))
        self._muView.menuBar().hide()
        self._muView.keySelectionDocker.hide()
        # for now we don't wan't to manage the roi depending on the dimension.
        self._muView.setPerspectiveVisible(False)
        self.setCentralWidget(self._muView)
        self.setWindowFlags(qt.Qt.Widget)

        # add a ROI
        self._roiManager = RegionOfInterestManager(self._muView.getPlot())
        self._roiManager.setColor("red")  # Set the color of ROI

        self._roi = RectangleROI()
        self._updateRoi(xas_obj=xas_obj)
        self._roi.setName("ROI")
        self._roi.setEditable(True)
        self._roiManager.addRoi(self._roi)

        # dock widget to compute E0
        self._dockWidget = qt.QDockWidget(parent=self)
        self._e0CalculationWidget = _E0CalculationWidget(parent=self._dockWidget)
        self._dockWidget.setWidget(self._e0CalculationWidget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._dockWidget)
        self._dockWidget.setAllowedAreas(
            qt.Qt.RightDockWidgetArea | qt.Qt.LeftDockWidgetArea
        )
        self._dockWidget.setFeatures(qt.QDockWidget.NoDockWidgetFeatures)

        # expose scale
        self.getComputationScale = self._e0CalculationWidget.getComputationScale
        self.getE0 = self._e0CalculationWidget.getE0

        # connect Signal / Slot
        self._roi.sigRegionChanged.connect(functools.partial(self._updateE0, "ROI"))
        self._muView.sigFrameChanged.connect(functools.partial(self._updateE0, "frame"))
        self._e0CalculationWidget.sigComputationScaleChanged.connect(
            functools.partial(self._updateE0, "scale")
        )

        # set up
        if xas_obj is not None:
            self.setXasObject(xas_obj=xas_obj)

    def setXasObject(self, xas_obj: XASObject, update_roi: bool = True):
        self._xas_obj = xas_obj
        self._muView.setXasObject(xas_obj=self._xas_obj)
        if update_roi:
            self._updateRoi(self._xas_obj)
        # compute E0 for the current roi
        self._updateE0(origin="init")

    def getXasObject(self):
        return self._xas_obj

    def _updateRoi(self, xas_obj):
        if xas_obj is not None:
            dim_1, dim_2 = xas_obj.dim1, xas_obj.dim2
        else:
            dim_1, dim_2 = 100, 100
        self._roi.setGeometry(origin=(0, 0), size=(dim_2, dim_1))

    def _updateE0(self, origin: str):
        """
        :param origin: what is the reason of updating E0:
                       * `init`: construction of the widget, we want to run the
                         the first computation
                       * `frame`: the current frame change
                       * `scale`: the scale to compute E0 changed
                       * `ROI`: the region of interest changed
        """
        assert origin in ("ROI", "frame", "scale", "init")
        if origin == "frame" and self.getComputationScale() == _ComputationScale.ALL:
            return
        if self._xas_obj is None:
            return

        if self.getComputationScale() == _ComputationScale.ALL:
            data = self._xas_obj.spectra.as_ndarray("mu")
        else:
            data = self._muView.getActiveImage(just_legend=False).getData()

        e0 = self._compute0(roi=self._roi, data=data)
        self._e0CalculationWidget.setE0(e0)

    def _compute0(self, roi, data):
        if self._xas_obj is None:
            return
        roi_origin = roi.getOrigin()
        roi_size = roi.getSize()
        ymin, ymax = int(roi_origin[1]), int(roi_origin[1] + roi_size[1])
        xmin, xmax = int(roi_origin[0]), int(roi_origin[0] + roi_size[0])
        # clip roi
        ymin = max(ymin, 0)
        ymax = min(ymax, self._xas_obj.dim1)
        xmin = max(xmin, 0)
        xmax = min(xmax, self._xas_obj.dim2)

        if data.ndim == 3:
            # TODO: take into account the dimension displayed
            roi_data = data[:, ymin:ymax, xmin:xmax]
        elif data.ndim:
            roi_data = data[ymin:ymax, xmin:xmax]
        else:
            raise ValueError("given data dim %s is not managed" % data.ndim)

        return {
            E0ComputationMethod.MEAN: numpy.mean(roi_data),
            E0ComputationMethod.MEDIAN: numpy.median(roi_data),
        }


class _E0CalculationWidget(qt.QGroupBox):
    """Contains all the options to compute E0 and display the mean and the
    median values"""

    sigComputationScaleChanged = qt.Signal(str)
    """Signal emitted when the computation scale change"""

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent=parent)
        self.setTitle("E0")
        self.setLayout(qt.QGridLayout())
        # median
        self.layout().addWidget(qt.QLabel("median", self), 0, 0)
        self._medianLE = qt.QLineEdit("0", parent=self)
        self._medianLE.setReadOnly(True)
        self.layout().addWidget(self._medianLE, 0, 1)
        # mean
        self.layout().addWidget(qt.QLabel("mean", self), 1, 0)
        self._meanLE = qt.QLineEdit("0", parent=self)
        self._meanLE.setReadOnly(True)
        self.layout().addWidget(self._meanLE, 1, 1)
        # calculation scale option
        self._computationScale = _E0CalculationScale(parent=self)
        self.layout().addWidget(self._computationScale, 2, 0, 1, 2)
        # spacer
        self._spacer = qt.QWidget(parent=self)
        self._spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(self._spacer, 3, 0)

        # expose API
        self.getComputationScale = self._computationScale.getComputationScale

        # connect signal / slot
        self._computationScale.sigComputationScaleChanged.connect(
            self._computationScaleChanged
        )

    def getE0(self, method):
        """
        Return the current E0 value from the requested computation method

        :param method: method of compuation to get E0
        :type: Union[str,ComputationMethod]
        :return: E0
        :rtype: float
        """
        method = E0ComputationMethod.from_value(method)
        if method is E0ComputationMethod.MEAN:
            return float(self._meanLE.text())
        elif method is E0ComputationMethod.MEDIAN:
            return float(self._medianLE.text())
        else:
            raise ValueError("Given method %s is not managed" % method)

    def setE0(self, values):
        """

        :param values: dictionary with the different ComputationMethod as keys
                       and the value computed as values
        :type: dict
        :return:
        """
        assert E0ComputationMethod.MEDIAN in values
        assert E0ComputationMethod.MEAN in values
        self._meanLE.setText("%.3f" % values[E0ComputationMethod.MEAN])
        self._medianLE.setText("%.3f" % values[E0ComputationMethod.MEDIAN])

    def _computationScaleChanged(self, scale):
        self.sigComputationScaleChanged.emit(scale)


class _E0CalculationScale(qt.QGroupBox):
    """Interface to allow the user to select a the scale (from one frame or all
    frames) to compute E0"""

    sigComputationScaleChanged = qt.Signal(str)
    """Signal emitted when the computation scale change"""

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent)
        self.__buttonGrp = qt.QButtonGroup(parent=self)
        self.setLayout(qt.QVBoxLayout())
        self.setTitle("compute E0 from:")
        self._fromCurrentFrameRB = qt.QRadioButton("from current frame", parent=self)
        self.layout().addWidget(self._fromCurrentFrameRB)
        self.__buttonGrp.addButton(self._fromCurrentFrameRB)
        self._fromAllMapsRB = qt.QRadioButton("from all frames", parent=self)
        self.layout().addWidget(self._fromAllMapsRB)
        self.__buttonGrp.addButton(self._fromAllMapsRB)

        # set up
        self.__buttonGrp.setExclusive(True)
        self._fromCurrentFrameRB.setChecked(True)

        # signal / slot connection
        self.__buttonGrp.buttonReleased.connect(self._statusChanged)

    def _statusChanged(self, *arg, **kwargs):
        self.sigComputationScaleChanged.emit(self.getComputationScale().value)

    def getComputationScale(self):
        if self._fromAllMapsRB.isChecked():
            return _ComputationScale.ALL
        elif self._fromCurrentFrameRB.isChecked():
            return _ComputationScale.CURRENT
        else:
            raise ValueError("At least all frame or current frame should be active")
