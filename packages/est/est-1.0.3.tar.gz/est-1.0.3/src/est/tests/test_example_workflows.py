"""Test the example workflows provided in the project resources"""

import pytest

try:
    import PyMca5
except ImportError:
    PyMca5 = None

try:
    import larch
except ImportError:
    larch = None


from ewoks import convert_graph
from ewoks import execute_graph


@pytest.mark.skipif(PyMca5 is None, reason="Pymca5 is not installed")
def test_example_pymca_exafs(example_pymca, filename_cu_from_pymca, tmpdir):
    assert_spec(
        example_pymca,
        example_pymca_inputs(example_pymca),
        filename_cu_from_pymca,
        tmpdir,
    )


@pytest.mark.skipif(PyMca5 is None, reason="Pymca5 is not installed")
def test_example_pymca_exafs_hdf5(example_pymca, hdf5_filename_cu_from_pymca, tmpdir):
    assert_hdf5(
        example_pymca,
        example_pymca_inputs(example_pymca),
        hdf5_filename_cu_from_pymca,
        1,
        tmpdir,
    )


@pytest.mark.skip("normalization fails")
@pytest.mark.skipif(PyMca5 is None, reason="Pymca5 is not installed")
def test_example_pymca_fullfield(example_pymca, hdf5_filename_cu_from_pymca, tmpdir):
    assert_hdf5(
        example_pymca,
        example_pymca_inputs(example_pymca),
        hdf5_filename_cu_from_pymca,
        2,
        tmpdir,
    )


@pytest.mark.skipif(larch is None, reason="xraylarch is not installed")
def test_example_larch_exafs(example_larch, filename_cu_from_pymca, tmpdir):
    assert_spec(
        example_larch,
        example_larch_inputs(example_larch),
        filename_cu_from_pymca,
        tmpdir,
    )


@pytest.mark.skipif(larch is None, reason="xraylarch is not installed")
def test_example_larch_exafs_hdf5(example_larch, hdf5_filename_cu_from_pymca, tmpdir):
    assert_hdf5(
        example_larch,
        example_larch_inputs(example_larch),
        hdf5_filename_cu_from_pymca,
        1,
        tmpdir,
    )


@pytest.mark.skip("pre-edge fails")
@pytest.mark.skipif(larch is None, reason="xraylarch is not installed")
def test_example_larch_fullfield(example_larch, hdf5_filename_cu_from_pymca, tmpdir):
    assert_hdf5(
        example_larch,
        example_larch_inputs(example_larch),
        hdf5_filename_cu_from_pymca,
        2,
        tmpdir,
    )


@pytest.mark.skipif(larch is None, reason="xraylarch is not installed")
def test_example_bm23_exafs(example_bm23, filename_cu_from_pymca, tmpdir):
    assert_spec(
        example_bm23,
        example_bm23_inputs(example_bm23),
        filename_cu_from_pymca,
        tmpdir,
    )


@pytest.mark.skipif(larch is None, reason="xraylarch is not installed")
def test_example_bm23_exafs_hdf5(example_bm23, hdf5_filename_cu_from_pymca, tmpdir):
    assert_hdf5(
        example_bm23,
        example_bm23_inputs(example_bm23),
        hdf5_filename_cu_from_pymca,
        1,
        tmpdir,
    )


@pytest.mark.skip("pre-edge fails")
@pytest.mark.skipif(larch is None, reason="xraylarch is not installed")
def test_example_bm23_fullfield(example_bm23, hdf5_filename_cu_from_pymca, tmpdir):
    assert_hdf5(
        example_bm23,
        example_bm23_inputs(example_bm23),
        hdf5_filename_cu_from_pymca,
        2,
        tmpdir,
    )


def example_pymca_inputs(workflow):
    return list()


def example_larch_inputs(workflow):
    return list()


def example_bm23_inputs(workflow):
    return list()


def assert_spec(workflow, inputs, filename_cu_from_pymca, tmpdir):
    input_information = {
        "channel_url": f"spec://{filename_cu_from_pymca}?1 cu.dat 1.1 Column 2/Column 1",
        "spectra_url": f"spec://{filename_cu_from_pymca}?1 cu.dat 1.1 Column 2/Column 2",
        "energy_unit": "electron_volt",
    }
    return assert_execution(workflow, inputs, input_information, tmpdir)


def assert_hdf5(workflow, inputs, filename, scan, tmpdir):
    input_information = {
        "channel_url": f"silx://{filename}?/{scan}.1/measurement/energy",
        "spectra_url": f"silx://{filename}?/{scan}.1/measurement/mu",
        "energy_unit": "electron_volt",
    }
    return assert_execution(workflow, inputs, input_information, tmpdir)


def assert_execution(workflow, inputs, input_information, tmpdir):
    output_file = tmpdir / "result.h5"
    inputs.append(
        {
            "id": find_node_id(workflow, "ReadXasObject"),
            "name": "input_information",
            "value": input_information,
        }
    )
    inputs.append(
        {
            "id": find_node_id(workflow, "DumpXasObject"),
            "name": "output_file",
            "value": str(output_file),
        }
    )
    outputs = [{"all": True}]
    result = execute_graph(workflow, inputs=inputs, outputs=outputs)
    output_file.exists()
    assert result["result"] == str(output_file)
    return result


def find_node_id(filename, clsname):
    adict = convert_graph(filename, None)
    for node_attrs in adict["nodes"]:
        if node_attrs["task_identifier"].endswith(clsname):
            return node_attrs["id"]
