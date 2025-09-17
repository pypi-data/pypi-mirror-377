import copy

import numpy as np
import xarray as xr
from xarray import DataArray

from pygridsio.IO.AscZmapIO import Grid
from pygridsio.IO.grid_to_xarray import validate_grid_type


def assert_grid_geometry_is_equal(grid1: xr.DataArray, grid2: xr.DataArray):
    if not np.array_equal(grid1.x, grid2.x, equal_nan=True):
        return False
    return np.array_equal(grid1.y, grid2.y, equal_nan=True)


def assert_grids_are_equal(grid1: xr.DataArray, grid2: xr.DataArray):
    if not np.array_equal(grid1.x, grid2.x, equal_nan=True):
        return False
    if not np.array_equal(grid1.y, grid2.y, equal_nan=True):
        return False
    return np.array_equal(grid1.data, grid2.data, equal_nan=True)


def remove_padding_from_grid(
    grids: Grid | xr.DataArray | xr.Dataset
) -> None | Grid | DataArray:
    if isinstance(grids, Grid):
        return remove_padding_from_custom_grid(grids)
    elif isinstance(grids, xr.DataArray):
        return remove_padding_from_xarray(grids)
    elif isinstance(grids, xr.Dataset):
        print("Not yet implemented for xr.Datasets")
    else:
        raise TypeError("Type of grid not recognised, "
                        "accepted grids are: Grid, xr.DataArray")


def remove_padding_from_custom_grid(grid: Grid) -> Grid:
    first_col, last_col, first_row, last_row = return_non_nan_extent(grid.z)

    newNx = last_col - first_col + 1
    newNy = last_row - first_row + 1
    newGridx = grid.gridx[first_col:last_col + 1]
    newGridy = grid.gridy[first_row:last_row + 1]
    newValues = grid.z[first_row:last_row + 1, first_col:last_col + 1]

    # create a new grid object:
    new_grid = copy.deepcopy(grid)
    new_grid.gridx = newGridx
    new_grid.gridy = newGridy
    new_grid.nx = newNx
    new_grid.ny = newNy
    new_grid.z = newValues

    return new_grid


def remove_padding_from_xarray(grid: xr.DataArray) -> xr.DataArray:
    validate_grid_type(grid)

    first_col, last_col, first_row, last_row = return_non_nan_extent(grid.data)
    new_gridx = grid.x.data[first_col:last_col + 1]
    new_gridy = grid.y.data[first_row:last_row + 1]
    new_values = grid.data[first_row:last_row + 1, first_col:last_col + 1]
    new_grid = xr.DataArray(new_values,
                            coords=[("y", new_gridy), ("x", new_gridx)],
                            dims=["y", "x"])
    return new_grid


def resample_grid(
    grid: xr.DataArray,
    grid_to_use: xr.DataArray = None,
    new_cellsize: float = None,
    set_to_RDNew=False,
    interp_method="nearest"
) -> xr.DataArray:
    """
    Resample an xarray grid to a new geometry/resolution.
    Either a new cellsize can be provided or another grid can be provided to resample
    the provided grid to.

    Parameters
    ----------
    grid
        A grid to resample
    grid_to_use
        If provided, then grid will be resampled to have the same geometry as this grid
    new_cellsize
        A new cell size to resample the input grid to, the original minimum and maximum
        extent of the input grid will be used to resample to the new cell size
    set_to_RDNew
        If set to True and combined with new_cellsize then the grid will be resampled
        starting from Lower left corner: [0.0,300e3] and going to
        top right corner: [293e3,635e3] in the RD new coordinate system
    interp_method
        Either linear or nearest; nearest simply provides the value of the cell that
        contains the new coordinates while linear takes an average of the 4 cells
        nearest to the new cell
    Returns
    -------
        An xarray Grid
    """

    validate_grid_type(grid)

    if grid_to_use is None and new_cellsize is None:
        raise ValueError(
            "grid_to_use and new_cellsize cannot both be None, specify"
            "either a grid to resample the input grid to, or a new"
            "cellsize"
        )

    if grid_to_use is not None:
        return resample_grid_to_grid(grid, grid_to_use, interp_method=interp_method)

    # Create new coordinate arrays
    if set_to_RDNew:
        x_min = 0.0
        y_min = 300000
        x_max = 293000
        y_max = 635000
    else:
        x_min, x_max = grid.x.min(), grid.x.max()
        y_min, y_max = grid.y.min(), grid.y.max()

    new_x = np.arange(x_min, x_max, new_cellsize)
    new_y = np.arange(y_min, y_max, new_cellsize)

    if np.array_equal(new_x, grid.x.data) and np.array_equal(new_y, grid.y.data):
        return grid # grid is already at desired resolution. No resampling is performed

    # Interpolating the data to the new grid
    return grid.interp(x=new_x, y=new_y, method=interp_method)


def resample_grid_to_grid(
    grid_to_resample: xr.DataArray = None,
    grid_to_use: xr.DataArray = None,
    interp_method="nearest"
) -> xr.DataArray:

    validate_grid_type(grid_to_resample)
    validate_grid_type(grid_to_use)

    return grid_to_resample.interp(x=grid_to_use.x,
                                   y=grid_to_use.y,
                                   method=interp_method)


def calculate_grid_misfit(grid1: xr.DataArray, grid2: xr.DataArray):
    """
    This returns a value describing how different two grids are on their non-nan values.
    It is equal to:

    sqrt((grid1 - grid2)^2 ) / sqrt(grid1^2)
    Where grid1 and grid2 in the above equation is equal to the element wise comparison
    of their grid values.

    This means:
    - a value of 0 means the grids are identical
    - a value of 0.1 means that grid1 and grid2 differ by 10% of the magnitude of grid1
    - a value of 1.0 means that grid1 and grid2 differ by 100% of the magnitude of grid1
    - a value of 2.0 means that grid1 and grid2 differ by 200% of the magnitude of grid1
    Parameters
    ----------
    grid1
    grid2

    Returns
    -------

    """

    validate_grid_type(grid1)
    validate_grid_type(grid2)
    if (not np.array_equal(grid1.x.data, grid2.x.data) or
        not np.array_equal(grid1.y.data, grid2.y.data)):
        raise ValueError("grid1 and grid2 must have the "
                         "same resolution before measuring similarity")

    grid1_data = grid1.data
    grid1_data.flatten()
    grid1_data = grid1_data[~np.isnan(grid1_data)]

    diff = grid1.data - grid2.data
    diff1d = diff.flatten()
    diff1d = diff1d[~np.isnan(diff1d)]

    grid1_norm = np.linalg.norm(grid1_data)
    if grid1_norm == 0:
        return np.inf
    else:
        return np.linalg.norm(diff1d) / grid1_norm


def return_non_nan_extent(grid_values: np.array):
    nx = grid_values.shape[1]
    ny = grid_values.shape[0]

    first_col = 0
    for i in range(nx):
        if np.any(~np.isnan(grid_values[:, i])):
            first_col = i
            break

    last_col = nx - 1
    for i in range(nx - 1, 0, -1):
        if np.any(~np.isnan(grid_values[:, i])):
            last_col = i
            break

    first_row = 0
    for j in range(ny):
        if np.any(~np.isnan(grid_values[j, :])):
            first_row = j
            break

    last_row = ny - 1
    for j in range(ny - 1, 0, -1):
        if np.any(~np.isnan(grid_values[j, :])):
            last_row = j
            break

    return first_col, last_col, first_row, last_row