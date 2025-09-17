import numpy as np
import xarray as xr

from pygridsio.IO.AscZmapIO import Grid


def validate_grid_type(grid, raise_error=True):
    if not isinstance(grid, xr.DataArray):
        if raise_error:
            raise TypeError(
                "This method only accepts a xarray DataArray with dimensions x and y"
            )
        return False

    if "x" not in grid.dims or "y" not in grid.dims:
        if raise_error:
            raise TypeError(
                "This method only accepts a xarray DataArray with dimensions x and y"
            )

        return False

    return True


def custom_grid_to_xarray(grid: Grid):
    grid_dataarray = xr.DataArray(
        grid.z,
        coords=[("y", grid.gridy), ("x", grid.gridx)],
        dims=["y", "x"]
    )
    grid_dataarray.attrs["coord system"] = grid.coord_sys
    return grid_dataarray

def xarray_to_custom_grid(grid: xr.DataArray):
    custom_grid = Grid(read=False)
    custom_grid.gridx = grid.x.data
    custom_grid.gridy = grid.y.data
    custom_grid.orx = custom_grid.gridx[0]
    custom_grid.ory = custom_grid.gridy[0]
    custom_grid.coord_sys = "RD New"
    custom_grid.dx = custom_grid.gridx[1] - custom_grid.gridx[0]
    custom_grid.dy = custom_grid.gridy[1] - custom_grid.gridy[0]
    custom_grid.cellsize = custom_grid.dx
    custom_grid.nodata_val = np.nan
    custom_grid.z = grid.data
    return custom_grid

