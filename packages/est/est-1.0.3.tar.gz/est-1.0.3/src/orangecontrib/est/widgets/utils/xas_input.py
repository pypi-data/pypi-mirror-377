from typing import Optional
from typing import Union

import h5py
from ewoksorange.bindings.owwidgets import OWEwoksWidgetNoThread
from ewoksorange.gui.orange_imports import gui
from silx.gui import qt

import est.core.process.ignoreprocess
from est.core.process.io import ReadXasObject
from est.core.types.xasobject import XASObject
from est.gui.xas_object_definition.window import XASObjectWindow
from est.io.information import InputInformation
from est.io.utils.ascii import split_ascii_url


class XASInputOW(OWEwoksWidgetNoThread, ewokstaskclass=ReadXasObject):
    """
    Widget used for signal extraction
    """

    name = "xas input"
    description = "Read .dat file and convert it to spectra"
    icon = "icons/input.png"
    priority = 0
    keywords = ["spectroscopy", "signal", "input", "file"]

    want_main_area = True
    resizing_enabled = True
    want_control_area = False

    def __init__(self):
        super().__init__()
        self._inputWindow = qt.QWidget(parent=self)
        self._inputWindow.setLayout(qt.QGridLayout())

        self._inputDialog = XASObjectWindow(parent=self)
        self._inputWindow.layout().addWidget(self._inputDialog, 0, 0, 1, 2)

        # add the apply button
        types = qt.QDialogButtonBox.Ok
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self._inputWindow.layout().addWidget(spacer, 2, 0)

        layout = gui.vBox(self.mainArea, "input").layout()
        layout.addWidget(self._inputWindow)

        self.loadSettings(
            input_information=self.get_task_input_value(
                "input_information", default=None
            ),
        )

        # expose api
        self.apply = self.execute_ewoks_task

        # signal / slot connection
        self._buttons.accepted.connect(self.hide)
        self._buttons.accepted.connect(self.execute_ewoks_task)
        self._inputDialog.getMainWindow().editingFinished.connect(self._storeSettings)
        self.setFileSelected = self._inputDialog.setAsciiFile

    def loadSettings(self, input_information: Union[InputInformation, dict, None]):
        if input_information is None:
            return
        if isinstance(input_information, dict):
            input_information = InputInformation.from_dict(input_information)
        advanceHDF5Info = self._inputDialog.getAdvanceHdf5Information()

        if input_information.spectra_url.file_path() is None:
            input_type = None
        elif h5py.is_hdf5(input_information.spectra_url.file_path()):
            input_type = est.io.InputType.hdf5_spectra
            if input_information.spectra_url is not None:
                self._inputDialog.setSpectraUrl(input_information.spectra_url)
            if input_information.channel_url is not None:
                self._inputDialog.setEnergyUrl(input_information.channel_url)
            if input_information.mu_ref_url is not None:
                advanceHDF5Info.setMuRefUrl(input_information.mu_ref_url)
            self._inputDialog.getMainWindow().setSkipConcatenatedNPoints(
                input_information.trim_concatenated_n_points
            )
            self._inputDialog.getMainWindow().setSkipConcatenatedNSpectra(
                input_information.skip_concatenated_n_spectra
            )
            self._inputDialog.getMainWindow().setConcatenatedSpectraSectionSize(
                input_information.concatenated_spectra_section_size
            )
            self._inputDialog.getMainWindow().setConcatenatedSpectra(
                input_information.is_concatenated
            )
        else:
            input_type = est.io.InputType.ascii_spectrum
            self._inputDialog.setAsciiFile(input_information.spectra_url.file_path())
            # TODO: check if there is any scan title in here
            urls_with_col_names = {
                self._inputDialog.setEnergyColName: input_information.channel_url,
                self._inputDialog.setAbsColName: input_information.spectra_url,
                self._inputDialog.setMonitorColName: input_information.mu_ref_url,
            }
            for setter, value in urls_with_col_names.items():
                if value is not None:
                    setter(split_ascii_url(value)["col_name"])
            scan_title = split_ascii_url(input_information.spectra_url)["scan_title"]
            if scan_title is not None:
                self._inputDialog.setScanTitle(scan_title)

        if input_information.config_url is not None:
            self._inputDialog.setConfigurationUrl(input_information.config_url)

        if input_information.I0_url is None:
            advanceHDF5Info.setI0Url(input_information.I0_url)
        if input_information.I1_url is None:
            advanceHDF5Info.setI1Url(input_information.I1_url)
        if input_information.I2_url is None:
            advanceHDF5Info.setI2Url(input_information.I2_url)

        if len(input_information.dimensions) == 3:
            self._inputDialog.setDimensions(input_information.dimensions)
        elif not len(input_information.dimensions) == 0:
            raise ValueError("spectra dimensions are expected to be 3D")
        self._inputDialog.setEnergyUnit(input_information.energy_unit)

        # set up
        self._inputDialog.setCurrentType(input_type)

    def _storeSettings(self):
        self.update_default_inputs(
            input_information=self._inputDialog.getInputInformation().to_dict()
        )

    def sizeHint(self):
        return qt.QSize(400, 200)

    def buildXASObj(self) -> Optional[XASObject]:
        return self._inputDialog.buildXASObject()
