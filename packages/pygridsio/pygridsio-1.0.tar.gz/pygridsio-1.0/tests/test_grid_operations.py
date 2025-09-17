from os import path
from pathlib import Path

import numpy as np

from pygridsio.grid_functions.grid_operations import (
    assert_grids_are_equal,
    calculate_grid_misfit,
    remove_padding_from_custom_grid,
    remove_padding_from_grid,
    resample_grid,
)
from pygridsio.IO.main_IO_functions import read_grid, read_grid_to_custom_grid

test_files_path = Path(path.dirname(__file__), "resources")

def test_grid_remove_padding():
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    grid = read_grid_to_custom_grid(grid_file_name)
    grid_no_padding = remove_padding_from_custom_grid(grid)

    non_nan_original = np.count_nonzero(~np.isnan(grid.z))
    ncells_original = np.size(grid.z)

    non_nan_new = np.count_nonzero(~np.isnan(grid_no_padding.z))
    ncells_new = np.size(grid_no_padding.z)

    # Assert
    assert non_nan_original == non_nan_new
    assert ncells_new < ncells_original

def test_xarray_remove_padding(tmp_path):
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    grid = read_grid(grid_file_name)
    grid_no_padding = remove_padding_from_grid(grid)

    non_nan_original = np.count_nonzero(~np.isnan(grid.data))
    ncells_original = np.size(grid.data)

    non_nan_new = np.count_nonzero(~np.isnan(grid_no_padding.data))
    ncells_new = np.size(grid_no_padding.data)

    # Assert
    assert non_nan_original == non_nan_new
    assert ncells_new < ncells_original

def test_xarray_grid_resample_to_RDnew():
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    grid = read_grid(grid_file_name)

    # Act
    resampled_grid = resample_grid(grid,
                                   new_cellsize=1000,
                                   set_to_RDNew=True,
                                   interp_method="nearest"
                                   )

    # Assert
    assert len(resampled_grid.x) == 293
    assert len(resampled_grid.y) == 335

def test_xarray_grid_resample_to_RDnew_multiple_times():
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    grid = read_grid(grid_file_name)

    # Act
    resampled_grid1 = resample_grid(grid,
                                    new_cellsize=1000,
                                    set_to_RDNew=True,
                                    interp_method="nearest",
                                    )


    resampled_grid2 = resample_grid(resampled_grid1,
                                    new_cellsize=1000,
                                    set_to_RDNew=True,
                                    interp_method="nearest",
                                    )

    resampled_grid3 = resample_grid(resampled_grid2,
                                    new_cellsize=1000,
                                    set_to_RDNew=True,
                                    interp_method="nearest",
                                    )

    resampled_grid4 = resample_grid(resampled_grid3,
                                    new_cellsize=1000,
                                    set_to_RDNew=True,
                                    interp_method="nearest",
                                    )

    # Assert
    assert assert_grids_are_equal(resampled_grid1, resampled_grid4)


def test_xarray_grid_resample_to_other_grid_resolution():
    # Arrange
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = read_grid(test_files_path / "ROSL_ROSLU__temperature.nc")

    # Act
    grid1 = resample_grid(grid1, grid_to_use=grid2)

    # Assert
    assert np.array_equal(grid1.x.data, grid2.x.data)
    assert np.array_equal(grid1.y.data, grid2.y.data)

def test_grid_similarity():
    # Arrange
    grid1 = read_grid(test_files_path / "KNNSF_ntg_new.nc")
    grid2 = read_grid(test_files_path / "KNNSF_ntg_old.nc")
    grid2_resampled = resample_grid(grid2, grid_to_use=grid1)

    # Act
    _ = calculate_grid_misfit(grid1, grid2_resampled)

def test_grid_similarity_all_zeros():
    # Arrange
    grid1 = read_grid(test_files_path / "KNNSF_ntg_new.nc")
    grid2 = read_grid(test_files_path / "KNNSF_ntg_old.nc")
    grid2_resampled = resample_grid(grid2, grid_to_use=grid1)
    grid1.data[:] = 0

    # Act
    _ = calculate_grid_misfit(grid1, grid2_resampled)

