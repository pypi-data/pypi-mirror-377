import logging
from typing import Iterable

from silx.gui import qt

from est.gui.unit.energy import EnergyUnitSelector
from est.io.utils import ascii

_logger = logging.getLogger(__name__)


class XASObjectFromAscii(qt.QWidget):
    """
    Interface used to define a XAS object from a single ASCII file
    """

    editingFinished = qt.Signal()
    """signal emitted when edition is finished"""

    class FileQLineEdit(qt.QLineEdit):
        """QLineEdit to handle a file path"""

        def dropEvent(self, event):
            if event.mimeData().hasFormat("text/uri-list"):
                for url in event.mimeData().urls():
                    self.setText(str(url.path()))

        def supportedDropActions(self):
            """Inherited method to redefine supported drop actions."""
            return qt.Qt.CopyAction | qt.Qt.MoveAction

        def dragEnterEvent(self, event):
            if event.mimeData().hasFormat("text/uri-list"):
                event.accept()
                event.setDropAction(qt.Qt.CopyAction)
            else:
                qt.QWidget.dragEnterEvent(self, event)

        def dragMoveEvent(self, event):
            if event.mimeData().hasFormat("text/uri-list"):
                event.setDropAction(qt.Qt.CopyAction)
                event.accept()
            else:
                qt.QWidget.dragMoveEvent(self, event)

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        # select file
        self.layout().addWidget(qt.QLabel("file", self), 0, 0, 1, 1)
        self._inputLe = self.FileQLineEdit("", self)
        self.layout().addWidget(self._inputLe, 0, 1, 1, 1)
        self._selectPB = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectPB, 0, 2, 1, 1)

        # select energy
        self.layout().addWidget(qt.QLabel("energy unit", self), 1, 0, 1, 1)
        self._energyUnitSelector = EnergyUnitSelector(parent=self)
        self.layout().addWidget(self._energyUnitSelector, 1, 1, 1, 1)

        # select scan from multi-spectrum file
        self.layout().addWidget(qt.QLabel("scan title"), 2, 0, 1, 1)
        self._scanTitleName = qt.QComboBox(self)
        self.layout().addWidget(self._scanTitleName, 2, 1, 1, 1)

        # select columns
        self._dimensionWidget = _ColNameSelection(parent=self)
        self.layout().addWidget(self._dimensionWidget, 3, 0, 1, 2)

        # spacer
        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 999, 0, 1, 1)

        # signal / slot connection
        self._selectPB.pressed.connect(self._selectFile)
        self._inputLe.editingFinished.connect(self._newFileSelected)
        self._scanTitleName.currentIndexChanged.connect(self._newScanSelected)

        self._dimensionWidget.sigInputChanged.connect(self._editingIsFinished)
        self._scanTitleName.currentIndexChanged.connect(self._editingIsFinished)
        self._energyUnitSelector.currentIndexChanged.connect(self._editingIsFinished)

    def _editingIsFinished(self, *args, **kwargs):
        self.editingFinished.emit()

    def getFileSelected(self):
        return self._inputLe.text()

    def _getNameFilters(self):
        return [
            "Ascii (*.dat *.spec *.csv *.xmu)",
            "All Files (*)",
        ]

    def _selectFile(self, *args, **kwargs):
        old = self.blockSignals(True)
        try:
            dialog = qt.QFileDialog(self)
            dialog.setFileMode(qt.QFileDialog.ExistingFile)
            dialog.setNameFilters(self._getNameFilters())

            if not dialog.exec_():
                dialog.close()
                return

            fileSelected = dialog.selectedFiles()
            if len(fileSelected) == 0:
                return
            assert len(fileSelected) == 1
            self.setFileSelected(fileSelected[0])
        finally:
            self.blockSignals(old)

    def setFileSelected(self, file_path):
        self._inputLe.setText(file_path)
        self._inputLe.editingFinished.emit()

    def _newFileSelected(self):
        old = self.blockSignals(True)
        try:
            scan_title = self.getScanTitle()
            self._scanTitleName.clear()
            titles = ascii.get_all_scan_titles(self.getFileSelected())
            for title in sorted(titles):
                self._scanTitleName.addItem(title)
            if titles and scan_title not in titles:
                scan_title = titles[0]
            self.setScanTitle(scan_title)
            self._scanTitleName.currentIndexChanged.emit(
                self._scanTitleName.currentIndex()
            )
        except Exception as e:
            _logger.warning(e)
        finally:
            self.blockSignals(old)

    def _newScanSelected(self, index):
        old = self.blockSignals(True)
        try:
            self._dimensionWidget.setScan(self.getFileSelected(), self.getScanTitle())
        except Exception as e:
            _logger.warning(e)
        finally:
            self.blockSignals(old)

    def getEnergyUnit(self):
        return self._energyUnitSelector.getUnit()

    def setEnergyUnit(self, unit):
        return self._energyUnitSelector.setUnit(unit=unit)

    def setEnergyColName(self, name):
        self._dimensionWidget.setEnergyColName(name)

    def getEnergyColName(self):
        return self._dimensionWidget.getEnergyColName()

    def setAbsColName(self, name):
        self._dimensionWidget.setAbsColName(name)

    def getAbsColName(self):
        return self._dimensionWidget.getAbsColName()

    def setMonitorColName(self, name):
        self._dimensionWidget.setMonitorColName(name)

    def getMonitorColName(self):
        return self._dimensionWidget.getMonitorColName()

    def getColumnSelected(self):
        return self._dimensionWidget.getColumnSelected()

    def setScanTitle(self, scan_title):
        index = self._scanTitleName.findText(scan_title)
        if index >= 0:
            self._scanTitleName.setCurrentIndex(index)

    def getScanTitle(self):
        return self._scanTitleName.currentText()


class _ColNameSelection(qt.QWidget):
    sigInputChanged = qt.Signal()
    """Signal emitted when dimension change"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QFormLayout())
        self._energyColNamCB = _QColumnComboBox(parent=self)
        self.layout().addRow("energy col name", self._energyColNamCB)
        self._absColNamCB = _QColumnComboBox(parent=self)
        self.layout().addRow("absorption col name", self._absColNamCB)
        self._monitorColNamCB = _QColumnComboBox(parent=self)
        self._monitorColNamCB.setEnabled(False)
        self._useMonitorCB = qt.QCheckBox("monitor col name")
        self.layout().addRow(self._useMonitorCB, self._monitorColNamCB)

        # connect Signal / Slot
        self._energyColNamCB.currentIndexChanged.connect(self._propagateSigChanged)
        self._absColNamCB.currentIndexChanged.connect(self._propagateSigChanged)
        self._monitorColNamCB.currentIndexChanged.connect(self._propagateSigChanged)
        self._useMonitorCB.toggled.connect(self._propagateSigChanged)
        self._useMonitorCB.toggled.connect(self._monitorColNamCB.setEnabled)

    def _propagateSigChanged(self):
        self.sigInputChanged.emit()

    def getColumnSelected(self) -> dict:
        """

        :return: return the information regarding each energy and mu
        :rtype: dict
        """
        return {
            "energy": self.getEnergyColName(),
            "mu": self.getAbsColName(),
            "monitor": self.getMonitorColName(),
        }

    def getMonitorColName(self):
        if self.useMonitor():
            return self._monitorColNamCB.currentText()
        else:
            return None

    def setMonitorColName(self, name):
        self._monitorColNamCB.setColumnName(name)

    def useMonitor(self):
        return self._useMonitorCB.isChecked()

    def setEnergyColName(self, name):
        self._energyColNamCB.setColumnName(name)

    def getEnergyColName(self):
        return self._energyColNamCB.getColumnName()

    def setAbsColName(self, name):
        self._absColNamCB.setColumnName(name)

    def getAbsColName(self):
        return self._absColNamCB.getColumnName()

    def setScan(self, file_path, scan_title):
        old = self.blockSignals(True)
        try:
            prev_energy = self._energyColNamCB.getColumnName()
            prev_absorption = self._absColNamCB.getColumnName()
            prev_monitor = self._monitorColNamCB.currentText()

            self._energyColNamCB.clear()
            self._absColNamCB.clear()
            self._monitorColNamCB.clear()

            col_names = ascii.get_scan_column_names(file_path, scan_title)
            self._energyColNamCB.setColumnsNames(col_names)
            self._absColNamCB.setColumnsNames(col_names)
            self._monitorColNamCB.setColumnsNames(col_names)

            if col_names:
                ncols = len(col_names)
                if prev_energy not in col_names and ncols >= 1:
                    prev_energy = col_names[0]
                if prev_absorption not in col_names and ncols >= 2:
                    prev_absorption = col_names[1]
                if prev_monitor not in col_names and ncols >= 3:
                    prev_monitor = col_names[2]

            self._energyColNamCB.setColumnName(prev_energy)
            self._absColNamCB.setColumnName(prev_absorption)
            self._monitorColNamCB.setColumnName(prev_monitor)
        finally:
            self.blockSignals(old)


class _QColumnComboBox(qt.QComboBox):
    def __init__(self, parent):
        qt.QComboBox.__init__(self, parent)

    def setColumnsNames(self, columns_names: Iterable):
        for column_name in columns_names:
            self.addItem(column_name)

    def setColumnName(self, name):
        index = self.findText(name)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            _logger.info("Unable to find name: {}".format(name))

    def getColumnName(self):
        return self.currentText()
