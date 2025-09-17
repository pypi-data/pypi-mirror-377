import copy
from os import path
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from pygridsio import remove_padding_from_grid, resample_grid
from pygridsio.grid_functions.grid_plotting import (
    make_interactive_plot,
    plot_grid,
    plot_grid_comparison,
    plot_netherlands_shapefile,
)
from pygridsio.IO.main_IO_functions import read_grid, read_grid_to_custom_grid

test_files_path = Path(path.dirname(__file__), "resources")

def test_grid_plot_custom_grid(tmp_path):
    # Arrange
    grid_file_name = Path(test_files_path, "SLDNA_top.zmap")
    grid = read_grid_to_custom_grid(grid_file_name)

    # Act
    with pytest.raises(TypeError):
        plot_grid(
            grid,
            outfile=Path(tmp_path, "temp.png"),
            zoom=True
        )

def test_grid_plot(tmp_path):
    # Arrange
    grid = read_grid(test_files_path / "SLDNA_top.zmap")
    fig, ax = plt.subplots(figsize=(10, 10))

    # Act
    plot_grid(
        grid,
        axes=ax,
        outfile=Path(tmp_path, "temp2.png"),
        zoom=True
    )

def test_grid_plot_no_colorbar(tmp_path):
    # Arrange
    grid = read_grid(test_files_path / "SLDNA_top.zmap")
    fig, ax = plt.subplots(figsize=(10, 10))

    # Act
    plot_grid(
        grid,
        axes=ax,
        outfile=Path(tmp_path, "temp3.png"),
        zoom=True,
        add_colorbar=False,
    )

def test_grid_plot_custom_norm(tmp_path):
    # Arrange
    grid = read_grid(test_files_path / "SLDNA_top.zmap")
    fig, ax = plt.subplots(figsize=(10, 10))

    # Act
    plot_grid(
        grid,
        axes=ax,
        outfile=Path(tmp_path, "temp3.png"),
        norm=None,
        zoom=True
    )

def test_plot_grid_comparison(tmp_path):
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = copy.deepcopy(grid1)
    grid2.data *= 0.75
    plot_grid_comparison(
        grid1,
        grid2,
        outfile=Path(tmp_path, "gridcomparison.png")
    )


def test_plot_grid_comparison_with_different_resolutions(tmp_path):
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = copy.deepcopy(grid1)
    grid2.data *= 0.75
    grid1 = resample_grid(grid1, new_cellsize=1000)

    plot_grid_comparison(
        grid1,
        grid2,
        outfile=Path(tmp_path, "gridcomparison.png")
    )


def test_plot_grid_comparison_with_filenames(tmp_path):
    grid1filename = Path(test_files_path, "SLDNA_top.zmap")
    grid2filename = str(Path(test_files_path, "SLDNA_top.zmap"))
    plot_grid_comparison(
        grid1filename,
        grid2filename,
        outfile=Path(tmp_path, "gridcomparison.png")
    )


def test_plot_grid_comparison_with_all_nan_grid(tmp_path):
    grid1 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2 = read_grid(test_files_path / "SLDNA_top.zmap")
    grid2.data[:] = np.nan
    plot_grid_comparison(
        grid1,
        grid2,
        outfile=Path(tmp_path, "gridcomparison.png")
    )


def test_plot_shapefile():
    fig, ax = plt.subplots(figsize=(10, 10))

    plot_netherlands_shapefile(ax)

def test_plot_grid_comparison_single_value_grids(tmp_path):
    grid1 = read_grid(test_files_path / "KNNSF_ntg_new.nc")
    grid2 = read_grid(test_files_path / "KNNSF_ntg_old.nc")
    plot_grid_comparison(
        grid1,
        grid2,
        outfile=tmp_path / "gridcomparison_single_value.png",
        add_netherlands_shapefile=True
    )

def test_plot_grid_comparison_identical_grids(tmp_path):
    grid1 = read_grid(test_files_path / "KNNSF_ntg_new.nc")
    plot_grid_comparison(
        grid1,
        grid1,
        outfile=tmp_path / "gridcomparison_identical_grids.png",
        add_netherlands_shapefile=True
    )

def test_grid_interactive_plot(tmp_path):
    # Arrange
    grid = read_grid(test_files_path / "SLDNA_top.zmap")
    grid = remove_padding_from_grid(grid)

    grid2 = read_grid(test_files_path / "SLDNA_ntg.zmap")
    grid2 = resample_grid(grid2, grid_to_use=grid)

    grid3 = copy.deepcopy(grid2)
    grid3.data[:, :] = np.nan

    well_data = pd.read_excel(test_files_path / "SLDNA_well_data_perm.xlsx")

    # Act
    make_interactive_plot(
        [grid, grid2, grid3],
        ["top", "ntg", "dummy1234658607-"],
        units=["[m]", "[0-1]", "Cats"],
        outfile=tmp_path / "interactive_plot.html",
        add_netherlands_shapefile=True,
        title="Aquifer: SLDNA, Scenario: BaseCase",
        scatter_df=well_data,
        scatter_z="perm_preferred")