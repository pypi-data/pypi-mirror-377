import numpy as np
import pytest

try:
    import anu_ctlab_io.netcdf

    _HAS_NETCDF = True
except ImportError:
    _HAS_NETCDF = False

import anu_ctlab_io


@pytest.mark.skipif(not _HAS_NETCDF, reason="Requires 'netcdf' extra")
def test_read_netcdf_single():
    dataset = anu_ctlab_io.Dataset.from_path("tests/data/tomoLoRes_SS.nc")

    # check the type is right
    assert str(dataset._datatype) == "tomo"

    array = dataset.data
    assert array.dtype == np.uint16
    assert array.shape[0] == 10
    assert array.shape[1] == 20
    assert array.shape[2] == 30

    assert (array[:] == np.arange(np.prod(array.shape)).reshape(array.shape)).all()
    assert dataset.history and isinstance(dataset.history, dict)
    print(dataset.history)


@pytest.mark.skipif(not _HAS_NETCDF, reason="Requires 'netcdf' extra")
def test_read_netcdf_multi():
    dataset = anu_ctlab_io.Dataset.from_path(
        "tests/data/tomoHiRes_SS_nc",
    )
    array = dataset.data

    assert array.dtype == np.uint16
    assert array.shape[0] == 100
    assert array.shape[1] == 200
    assert array.shape[2] == 300

    # See generate_test_data_zarr.py
    #   Each chunk of z shape 30 is just filled with a constant value of the chunk index
    #   The chunk z shape is independent of the netcdf block z shape.
    print(array.compute()[range(0, 100, 5), 0, 0])
    shape_z = array.shape[0]
    chunk_z = 30
    num_chunks_z = (shape_z + chunk_z - 1) // chunk_z
    for i in range(num_chunks_z):
        chunk = array[i * chunk_z : min((i + 1) * chunk_z, shape_z), ...]
        assert (chunk == i).all()
