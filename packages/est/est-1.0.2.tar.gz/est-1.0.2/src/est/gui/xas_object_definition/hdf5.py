from silx.gui import qt
from silx.gui.dialog.DataFileDialog import DataFileDialog
from silx.io.url import DataUrl

from est.core.types import dimensions
from est.core.utils.symbol import MU_CHAR
from est.gui.unit.energy import EnergyUnitSelector


class XASObjectFromH5(qt.QTabWidget):
    """
    Interface used to define a XAS object from h5 files and data path
    """

    editingFinished = qt.Signal()
    """signal emitted when edition is finished"""

    def __init__(self, parent=None):
        qt.QTabWidget.__init__(self, parent)
        # Mandatory information
        self._basicInformation = _MandatoryXASObjectInfo(self)
        self.addTab(self._basicInformation, "basic information")
        # Optional information
        self._advanceInformation = _OptionalXASObjectInfo(self)
        self.addTab(self._advanceInformation, "advanced information")

        # connect signal / slot
        self._basicInformation.editingFinished.connect(self._editingIsFinished)
        self._advanceInformation.editingFinished.connect(self._editingIsFinished)

    @property
    def advanceInfo(self):
        return self._advanceInformation

    def _editingIsFinished(self, *args, **kwargs):
        self.editingFinished.emit()

    def getEnergyUnit(self):
        return self._basicInformation.getEnergyUnit()

    def setEnergyUnit(self, unit):
        self._basicInformation.setEnergyUnit(unit=unit)

    def getDimensions(self):
        return self._basicInformation.getDimensions()

    def setDimensions(self, dims):
        self._basicInformation.setDimensions(dims=dims)

    def getConfigurationUrl(self):
        return self._basicInformation.getConfigurationUrl()

    def setConfigurationUrl(self, url):
        self._basicInformation.setConfigurationUrl(url=url)

    def getEnergyUrl(self):
        return self._basicInformation.getEnergyUrl()

    def setEnergyUrl(self, url):
        self._basicInformation.setEnergyUrl(url=url)

    def getSpectraUrl(self):
        return self._basicInformation.getSpectraUrl()

    def setSpectraUrl(self, url):
        return self._basicInformation.setSpectraUrl(url=url)

    def isSpectraConcatenated(self):
        return self._basicInformation._concatenatedCheckbox.isChecked()

    def setConcatenatedSpectra(self, value: bool):
        self._basicInformation._concatenatedCheckbox.setChecked(value)

    def getSkipConcatenatedNPoints(self):
        return self._basicInformation._skipConcatenatedNPoints.value()

    def setSkipConcatenatedNPoints(self, value: int):
        self._basicInformation._skipConcatenatedNPoints.setValue(value)

    def getSkipConcatenatedNSpectra(self):
        return self._basicInformation._skipConcatenatedNSpectra.value()

    def setSkipConcatenatedNSpectra(self, value: int):
        self._basicInformation._skipConcatenatedNSpectra.setValue(value)

    def getConcatenatedSpectraSectionSize(self):
        return self._basicInformation._concatenatedSpectraSectionSize.value()

    def setConcatenatedSpectraSectionSize(self, value: int):
        self._basicInformation._concatenatedSpectraSectionSize.setValue(value)


class _MandatoryXASObjectInfo(qt.QWidget):
    """Widget containing mandatory information"""

    editingFinished = qt.Signal()
    """signal emitted when edition is finished"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        # spectra url
        self._spectraSelector = _URLSelector(
            parent=self, name="spectra url", layout=self.layout(), position=(0, 0)
        )

        self._bufWidget = qt.QWidget(parent=self)
        self._bufWidget.setLayout(qt.QHBoxLayout())

        # Spacer to push elements
        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self._bufWidget.layout().addWidget(spacer)

        # Dimension selection widget
        self._dimensionSelection = _SpectraDimensions(parent=self._bufWidget)
        self._bufWidget.layout().addWidget(self._dimensionSelection)

        # Concatenated checkbox
        self._concatenatedCheckbox = qt.QCheckBox(
            "Concatenated spectra", parent=self._bufWidget
        )
        self._bufWidget.layout().addWidget(self._concatenatedCheckbox)

        # Labels and spin boxes
        self._concatenatedWidget = qt.QWidget(parent=self)
        self._concatenatedWidget.setLayout(qt.QVBoxLayout())

        label1 = qt.QLabel("Skip first N concatenated spectra", parent=self._bufWidget)
        self._skipConcatenatedNSpectra = qt.QSpinBox(parent=self._bufWidget)
        self._concatenatedWidget.layout().addWidget(label1)
        self._concatenatedWidget.layout().addWidget(self._skipConcatenatedNSpectra)

        label2 = qt.QLabel(
            "Trim N points of concatenated spectra",
            parent=self._bufWidget,
        )
        self._skipConcatenatedNPoints = qt.QSpinBox(parent=self._bufWidget)
        self._concatenatedWidget.layout().addWidget(label2)
        self._concatenatedWidget.layout().addWidget(self._skipConcatenatedNPoints)

        label3 = qt.QLabel(
            "Section size of concatenated spectra",
            parent=self._bufWidget,
        )
        self._concatenatedSpectraSectionSize = qt.QSpinBox(parent=self._bufWidget)
        self._concatenatedWidget.layout().addWidget(label3)
        self._concatenatedWidget.layout().addWidget(
            self._concatenatedSpectraSectionSize
        )

        self._bufWidget.layout().addWidget(self._concatenatedWidget)

        # Add buffer widget to main layout
        self.layout().addWidget(self._bufWidget, 1, 1)

        # channel/energy url
        self._energySelector = _URLSelector(
            parent=self,
            name="channel/energy url",
            layout=self.layout(),
            position=(2, 0),
        )
        self._energyUnit = EnergyUnitSelector(parent=self)
        self.layout().addWidget(self._energyUnit, 2, 3, 1, 1)
        # configuration url
        self._configSelector = _URLSelector(
            parent=self, name="configuration url", layout=self.layout(), position=(3, 0)
        )

        # connect signal / slot
        self._spectraSelector._qLineEdit.editingFinished.connect(
            self._editingIsFinished
        )
        self._energySelector._qLineEdit.editingFinished.connect(self._editingIsFinished)
        self._configSelector._qLineEdit.editingFinished.connect(self._editingIsFinished)
        self._dimensionSelection.sigDimensionChanged.connect(self._editingIsFinished)
        self._energyUnit.currentIndexChanged.connect(self._editingIsFinished)
        self._concatenatedCheckbox.stateChanged.connect(
            self._onConcatenatedCheckboxChange
        )
        self._skipConcatenatedNPoints.valueChanged.connect(self._editingIsFinished)
        self._skipConcatenatedNSpectra.valueChanged.connect(self._editingIsFinished)
        self._concatenatedSpectraSectionSize.valueChanged.connect(
            self._editingIsFinished
        )

        # expose API
        self.setDimensions = self._dimensionSelection.setDimensions
        self.getDimensions = self._dimensionSelection.getDimensions

        self._syncConcatenatedCheckbox()

    def _syncConcatenatedCheckbox(self):
        concatenated = self._concatenatedCheckbox.isChecked()
        self._concatenatedWidget.setEnabled(concatenated)
        self._dimensionSelection.setDisabled(concatenated)

    def _onConcatenatedCheckboxChange(self):
        self._syncConcatenatedCheckbox()
        self._editingIsFinished()

    def getSpectraUrl(self):
        """
        :return: the DataUrl of the spectra
        :rtype: DataUrl
        """
        return self._spectraSelector.getUrlPath()

    def getEnergyUrl(self):
        """
        :return: the DataUrl of energy / channel
        :rtype: DataUrl
        """
        return self._energySelector.getUrlPath()

    def getConfigurationUrl(self):
        """

        :return: the DataUrl of the configuration
        :rtype: DataUrl
        """
        return self._configSelector.getUrlPath()

    def setSpectraUrl(self, url):
        self._spectraSelector.setUrlPath(url)

    def setEnergyUrl(self, url):
        self._energySelector.setUrlPath(url)

    def setConfigurationUrl(self, url):
        self._configSelector.setUrlPath(url)

    def _editingIsFinished(self, *args, **kwargs):
        self.editingFinished.emit()

    def getDimensionsInfo(self) -> dimensions.DimensionsType:
        return self._dimensionSelection.getDimensions()

    def getEnergyUnit(self):
        return self._energyUnit.getUnit()

    def setEnergyUnit(self, unit):
        self._energyUnit.setUnit(unit=unit)


class _OptionalXASObjectInfo(qt.QWidget):
    """Widget containing optional information that we can associate to
    spectrum.
    """

    editingFinished = qt.Signal()
    """signal emitted when edition is finished"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        # I0
        self._I0Selector = _URLSelector(
            parent=self, name="I0 url", layout=self.layout(), position=(0, 0)
        )
        # I1
        self._I1Selector = _URLSelector(
            parent=self, name="I1 url", layout=self.layout(), position=(1, 0)
        )
        # I2
        self._I2Selector = _URLSelector(
            parent=self, name="I2 url", layout=self.layout(), position=(2, 0)
        )
        # mu ref
        self._muRefSelector = _URLSelector(
            parent=self,
            name="{} ref".format(MU_CHAR),
            layout=self.layout(),
            position=(3, 0),
        )

        # connect signal / slot
        self._I0Selector._qLineEdit.textChanged.connect(self._editingIsFinished)
        self._I1Selector._qLineEdit.textChanged.connect(self._editingIsFinished)
        self._I2Selector._qLineEdit.textChanged.connect(self._editingIsFinished)
        self._muRefSelector._qLineEdit.textChanged.connect(self._editingIsFinished)

    def _editingIsFinished(self, *args, **kwargs):
        self.editingFinished.emit()

    def getI0Url(self):
        return self._I0Selector.getUrlPath()

    def setI0Url(self, url):
        self._I0Selector.setUrlPath(url)

    def getI1Url(self):
        return self._I1Selector.getUrlPath()

    def setI1Url(self, url):
        self._I1Selector.setUrlPath(url)

    def getI2Url(self):
        return self._I2Selector.getUrlPath()

    def setI2Url(self, url):
        self._I2Selector.setUrlPath(url)

    def getMuRefUrl(self):
        return self._muRefSelector.getUrlPath()

    def setMuRefUrl(self, url):
        self._muRefSelector.setUrlPath(url)


class _QDimComboBox(qt.QComboBox):
    def __init__(self, parent):
        qt.QComboBox.__init__(self, parent)
        self.addItem("Dim 0", 0)
        self.addItem("Dim 1", 1)
        self.addItem("Dim 2", 2)
        self.setCurrentIndex(0)

    def setDim(self, dim: int):
        index = self.findData(dim)
        assert index >= 0
        self.setCurrentIndex(index)

    def getDim(self):
        return self.currentData()


class _SpectraDimensions(qt.QWidget):
    sigDimensionChanged = qt.Signal()
    """Signal emitted when dimension change"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QFormLayout())
        self._dim_x = _QDimComboBox(parent=self)
        self.layout().addRow("X", self._dim_x)
        self._dim_y = _QDimComboBox(parent=self)
        self.layout().addRow("Y", self._dim_y)
        self._dim_channel = _QDimComboBox(parent=self)
        self.layout().addRow("Channel/Energy", self._dim_channel)

        # set up
        self._dim_x.setDim(dimensions.STANDARD_DIMENSIONS[0])
        self._dim_y.setDim(dimensions.STANDARD_DIMENSIONS[1])
        self._dim_channel.setDim(dimensions.STANDARD_DIMENSIONS[2])

        # connect Signal / Slot
        self._dim_x.currentTextChanged.connect(self._insureDimUnicity)
        self._dim_y.currentTextChanged.connect(self._insureDimUnicity)
        self._dim_channel.currentTextChanged.connect(self._insureDimUnicity)

    def _insureDimUnicity(self):
        last_modified = self.sender()
        if last_modified is self._dim_x:
            get_second, get_third = self._dim_y, self._dim_channel
        elif last_modified is self._dim_y:
            get_second, get_third = self._dim_x, self._dim_channel
        elif last_modified is self._dim_channel:
            get_second, get_third = self._dim_x, self._dim_y
        else:
            raise RuntimeError("Sender should be in dim0, dim1, dim2")

        assert last_modified != get_second
        assert last_modified != get_third
        assert type(last_modified) is type(get_second) is type(get_third)
        value_set = {0, 1, 2}
        last_value_set = last_modified.getDim()
        value_set.remove(last_value_set)

        old_1 = last_modified.blockSignals(True)
        old_2 = get_second.blockSignals(True)
        old_3 = get_third.blockSignals(True)
        if get_second.getDim() in value_set:
            value_set.remove(get_second.getDim())
            get_third.setDim(value_set.pop())
        elif get_third.getDim() in value_set:
            value_set.remove(get_third.getDim())
            get_second.setDim(value_set.pop())
        else:
            get_second.setDim(value_set.pop())
            get_third.setDim(value_set.pop())

        last_modified.blockSignals(old_1)
        get_second.blockSignals(old_2)
        get_third.blockSignals(old_3)
        self.sigDimensionChanged.emit()

    def getDimensions(self) -> dimensions.DimensionsType:
        return (
            self._dim_x.getDim(),
            self._dim_y.getDim(),
            self._dim_channel.getDim(),
        )

    def setDimensions(self, dims: dimensions.DimensionsType) -> None:
        dims = dimensions.parse_dimensions(dims)
        self._dim_x.setDim(dims[0])
        self._dim_y.setDim(dims[1])
        self._dim_channel.setDim(dims[2])


class _URLSelector(qt.QWidget):
    def __init__(self, parent, name, layout=None, position=None):
        qt.QWidget.__init__(self, parent)
        self.name = name
        if layout is None:
            layout = self.setLayout(qt.QGridLayout())
            position = (0, 0)
        layout.addWidget(qt.QLabel(name + ":", parent=self), position[0], position[1])
        self._qLineEdit = qt.QLineEdit("", parent=self)
        layout.addWidget(self._qLineEdit, position[0], position[1] + 1)
        self._qPushButton = qt.QPushButton("select", parent=self)
        layout.addWidget(self._qPushButton, position[0], position[1] + 2)

        # connect signal / slot
        self._qPushButton.clicked.connect(self._selectFile)

    def _selectFile(self, *args, **kwargs):
        dialog = DataFileDialog(self)

        url = self._qLineEdit.text()
        if url:
            dialog.selectUrl(url)

        if not dialog.exec_():
            dialog.close()
            return None

        if dialog.selectedUrl() is not None:
            self.setUrlPath(dialog.selectedUrl())

    def getUrlPath(self):
        url = self._qLineEdit.text()
        if url == "":
            return None
        else:
            return DataUrl(path=url)

    def setUrlPath(self, url):
        if isinstance(url, DataUrl):
            url = url.path()
        self._qLineEdit.setText(url)
        self._qLineEdit.editingFinished.emit()
