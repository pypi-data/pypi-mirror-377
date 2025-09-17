from os import path
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from pygridsio import combine_grids_in_dataset, read_grid, resample_grid, write_grid
from pygridsio.IO.geotiffIO import read_geotiff_to_grid, write_grid_to_geotiff
from pygridsio.IO.main_IO_functions import read_grid_to_custom_grid
from pygridsio.IO.netcdfIO import write_dataset_to_netcdf_raster, write_to_netcdf_raster

test_files_path = Path(path.dirname(__file__), "resources")

def test_grid_read_troublesome_zmap_to_custom_grid():
    """
    A weird one; I got a .zmap grid which has some combiination of ystart, yend and
    ny which causes the gridy array to have a length that is not equal to ny;
    This is to do with a rounding error of the function np.arange() which is used to
    instantiate gridy and gridx, ensure this doesn't happen.
    """

    # Arrange
    grid = read_grid_to_custom_grid(test_files_path / "troublesome.zmap")

    # Assert
    assert len(grid.gridy) == 33


def test_grid_read_to_custom_grid():
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    _ = read_grid_to_custom_grid(grid_file_name)

def test_grid_read_fname_without_suffix():
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_ntg")
    _ = read_grid_to_custom_grid(grid_file_name, grid_format="ZMAP")


def test_grid_read_to_xarray():
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    _ = read_grid(grid_file_name)


def test_combine_grids_in_dataset():
    # Arrange
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = read_grid(test_files_path / "SLDNA_ntg.zmap")

    _ = combine_grids_in_dataset(
        [grid1, grid2],
        labels=["top", "ntg"],
        grid_template=grid1)

def test_combine_grids_in_dataset_different_resolutions():
    # Arrange
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = read_grid(test_files_path / "SLDNA_ntg.zmap")
    grid2_resampled = resample_grid(grid2, new_cellsize=1000, set_to_RDNew=True)

    with pytest.raises(ValueError):
        _ = combine_grids_in_dataset(
            [grid1, grid2_resampled],
            labels=["top", "ntg"])

def test_write(tmp_path):
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    grid = read_grid(grid_file_name)
    write_grid(grid, Path(tmp_path, "test.nc"))
    write_grid(grid, Path(tmp_path, "test.zmap"))
    write_grid(grid, Path(tmp_path, "test.asc"))
    write_grid(grid, Path(tmp_path, "test.tif"))

def test_write_dataset(tmp_path):
    # Arrange
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = read_grid(test_files_path / "SLDNA_ntg.zmap")
    grids_dataset = combine_grids_in_dataset(
        [grid1, grid2],
        labels=["top", "ntg"],
        grid_template=grid1)
    write_dataset_to_netcdf_raster(
        grids_dataset,
        Path(tmp_path, "test_dataset.nc"))

def test_write_to_netcdf_raster(tmp_path):
    # Arrange
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = read_grid(test_files_path / "SLDNA_ntg.zmap")
    grid3 = read_grid_to_custom_grid(test_files_path / "SLDNA_top.zmap")
    grids_dataset = combine_grids_in_dataset(
        [grid1, grid2],
        labels=["top", "ntg"],
        grid_template=grid1
    )

    # Act
    write_to_netcdf_raster(grid1, tmp_path / "dataarray_write.nc")
    write_to_netcdf_raster(
        grids_dataset,
        tmp_path / "dataset_write.nc"
    )
    write_to_netcdf_raster(grid3, tmp_path / "grid_write.nc")

    # Assert
    _ = xr.load_dataset(
        tmp_path / "dataarray_write.nc"
    )

    _ = xr.load_dataset(
        tmp_path / "dataset_write.nc"
    )

    _ = xr.load_dataset(
        tmp_path / "grid_write.nc"
    )

def test_read_netcdf_to_custom_grid(tmp_path):
    # Arrange
    grid_original = read_grid_to_custom_grid(
        test_files_path / "SLDNA_top.zmap"
    )

    write_to_netcdf_raster(
        grid_original,
        tmp_path / "SLDNA_top.nc"
    )

    # Act
    grid_written = read_grid_to_custom_grid(
        tmp_path / "SLDNA_top.nc"
    )

    # Assert
    assert np.array_equal(grid_original.z, grid_written.z, equal_nan=True)


def test_geotiff_IO(tmp_path):
    # Arrange
    grid_original = read_grid(test_files_path / "ROSLL__ntg.nc")

    # Act
    write_grid_to_geotiff(
        grid_original,
        tmp_path / "ROSLL__ntg.tif",
        epsg="RDnew"
    )

    grid_read = read_geotiff_to_grid(tmp_path / "ROSLL__ntg.tif")

    # Assert
    xr.testing.assert_allclose(grid_read, grid_original)

def test_geotiff_IO_read_write_grid():

    grid_original = read_grid(test_files_path / "ROSLL__ntg.nc")
    write_grid(grid_original, test_files_path / "ROSLL__ntg.tif")
    grid_from_geotiff = read_grid(test_files_path / "ROSLL__ntg.tif")

    # Assert
    xr.testing.assert_allclose(grid_original, grid_from_geotiff)