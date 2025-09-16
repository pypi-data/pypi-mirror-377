import silx.io.h5py_utils
from silx.io.url import DataUrl


def get_data(url: DataUrl):
    data_path = url.data_path()
    data_slice = url.data_slice()

    with silx.io.h5py_utils.File(url.file_path(), "r") as h5:
        dset = h5[data_path]

        if not silx.io.is_dataset(dset):
            raise ValueError("Data path from URL '%s' is not a dataset" % url.path())

        if data_slice is not None:
            return silx.io.utils.h5py_read_dataset(dset, index=data_slice)
        # works for scalar and array
        return silx.io.utils.h5py_read_dataset(dset)
