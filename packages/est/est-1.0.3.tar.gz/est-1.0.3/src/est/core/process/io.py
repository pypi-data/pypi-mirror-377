from typing import Optional

from est.core.io import read_from_input_information
from est.io.information import InputInformation

from .process import Process


class DumpXasObject(
    Process,
    input_names=["xas_obj", "output_file"],
    output_names=["result"],
):
    @staticmethod
    def definition() -> str:
        return "write XAS object to a file"

    def run(self):
        xas_obj = self.getXasObject(xas_obj=self.inputs.xas_obj)
        xas_obj.dump(self.output_file)
        self.outputs.result = self.output_file

    @property
    def output_file(self) -> Optional[str]:
        if self.missing_inputs.output_file:
            return None
        return self.inputs.output_file


class ReadXasObject(
    Process,
    input_names=["input_information"],
    output_names=["xas_obj"],
):
    @staticmethod
    def definition() -> str:
        return "read XAS data from file"

    def run(self):
        self.setConfiguration(self.inputs.input_information)
        input_information = InputInformation.from_dict(self.inputs.input_information)
        xas_obj = read_from_input_information(input_information)
        self.outputs.xas_obj = xas_obj
