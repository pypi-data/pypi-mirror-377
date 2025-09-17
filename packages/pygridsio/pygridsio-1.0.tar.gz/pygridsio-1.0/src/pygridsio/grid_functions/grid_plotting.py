import copy
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import xarray as xr
from plotly.subplots import make_subplots

from pygridsio import combine_grids_in_dataset, read_grid
from pygridsio.grid_functions.grid_operations import (
    calculate_grid_misfit,
    resample_grid,
)
from pygridsio.IO.grid_to_xarray import validate_grid_type
from pygridsio.resources.netherlands_shapefile.shapefile_plot_util import (
    get_netherlands_shapefile,
)


def zoom_on_grid(ax, z, x, y, zoom_buffer=10000):
    # if all values are nan simply return
    if np.isnan(z).all():
        return

    not_nan_locs = np.argwhere(~np.isnan(z))
    x_all = []
    y_all = []
    for coords in not_nan_locs:
        x_all.append(coords[1])
        y_all.append(coords[0])

    minx = x[np.min(x_all)]
    maxx = x[np.max(x_all)]
    miny = y[np.min(y_all)]
    maxy = y[np.max(y_all)]
    ax.set_xlim([minx - zoom_buffer, maxx + zoom_buffer])
    ax.set_ylim([miny - zoom_buffer, maxy + zoom_buffer])
    ax.set_xlim([minx - zoom_buffer, maxx + zoom_buffer])
    ax.set_ylim([miny - zoom_buffer, maxy + zoom_buffer])


def get_vmin_vmax(data):
    if np.all(np.isnan(data)):
        vmin = 0.0
        vmax = 1.0
    else:
        vmin = np.nanmin(data)
        vmax = np.nanmax(data)
        if vmin == vmax:
            vmin -= 0.1
            vmax += 0.1
    return vmax, vmin


def plot_grid(
    grid: xr.DataArray,
    axes=None,
    outfile=None,
    show=False,
    cmap="viridis",
    norm=None,
    vmin=None,
    vmax=None,
    add_colorbar=True,
    zoom=True,
    zoom_buffer=10000,
    custom_shapefile=None,
    add_netherlands_shapefile=False,
    shapefile_alpha=1.0
):
    """
    Plot a custom grid class

    Parameters
    ----------
    grid
        The grid object; either custom or a xarray.DataArray
    axes (optional)
        An axes object to plot the grid onto; if not provided a figure and axes object
        will be created
    outfile (optional)
        The file to save the figure to; if not provided then will show instead of save
        the figure
    cmap (optional)
        The colour map to use; if not provided matplotlib default will be used
    norm (optional)
        The colour map norm to use, if not provided the norm is derived from the data by
        matplotlib
    vmin (optional)
        The minimum value for the colourmap
    vmax (optional)
        The maximum value for the colourmap
    zoom (optional)
        Zoom onto the non-nan part of the grid.
    zoom_buffer (optional)
        A space around the non-nan part of the grid to be added if zoom is applied
    add_netherlands_shapefile (optional)
        Adds a shapefile of the netherlands to the background of the plot
    shapefile_alpha (optional)
        Controls the transparency of the shapefile

    Returns
    -------

    """
    validate_grid_type(grid)

    if axes is None:
        fig, axes = plt.subplots(1, 1, figsize=(6, 5))

    grid.plot(
        ax=axes,
        x="x",
        y="y",
        cmap=cmap,
        norm=norm,
        vmin=vmin,
        vmax=vmax,
        add_colorbar=add_colorbar
    )

    if zoom:
        zoom_on_grid(axes, grid.data, grid.x, grid.y, zoom_buffer=zoom_buffer)
    axes.tick_params(axis='both', which='major', labelsize=8)

    if add_netherlands_shapefile:
        shapefile = get_netherlands_shapefile()
        shapefile.boundary.plot(ax=axes, alpha=shapefile_alpha, edgecolor="k")

    if custom_shapefile is not None:
        custom_shapefile.boundary.plot(ax=axes, alpha=shapefile_alpha, edgecolor="k")

    if outfile is not None:
        plt.savefig(outfile)

    if show:
        plt.show()


def plot_netherlands_shapefile(ax: plt.Axes, shapefile_alpha=1.0, edgecolor="k"):
    """
    Plots a shapefile of the boundaries of the Netherlands on a provided axis
    Parameters
    ----------
    ax: matplotlib Axes
    shapefile_alpha (optional) transparency of the shapefile
    edgecolor (optional) colour of the edges of the shapefile

    Returns
    -------

    """
    shapefile = get_netherlands_shapefile()
    shapefile.boundary.plot(ax=ax, alpha=shapefile_alpha, edgecolor=edgecolor)

def plot_grid_comparison(
    grid1: xr.DataArray | str | Path,
    grid2: xr.DataArray | str | Path,
    outfile: str | Path,
    custom_shapefile=None,
    add_netherlands_shapefile=False,
    title1=None,
    title2=None,
    suptitle=None
):
    """
    Compare two grids to eachother, making a plot with 6 panels; two plots of the grids
    as maps, one of the difference of grid1 - grid2, and on the bottom row their
    respective histograms of the non-nan values

    Parameters
    ----------
    grid1
    grid2
    outfile
    custom_shapefile - a shapefile to plot behind the grids
    add_netherlands_shapefile - if true, plot a shapefile of the Netherlands
    title1 - the title of the top left panel
    title2 - the title of the top middle panel
    suptitle - the overall title

    Returns
    -------

    """
    if isinstance(grid1, Path | str):
        grid1 = read_grid(grid1)
    if isinstance(grid2, Path | str):
        grid2 = read_grid(grid2)
    validate_grid_type(grid1)
    validate_grid_type(grid2)

    # setup figure
    fig, axes = plt.subplots(ncols=3, nrows=2, figsize=(20, 8), height_ratios=[1, 0.5])
    grid_axes = [axes[0][0], axes[0][1], axes[0][2]]
    hist_axes = [axes[1][0], axes[1][1], axes[1][2]]
    fig.tight_layout(pad=5)

    # resample grid2 to have the same resolution as grid1 for calculating the
    # difference grid
    grid2_resampled = copy.deepcopy(grid2)
    grid2_resampled = resample_grid(grid2_resampled, grid_to_use=grid1)
    diff_grid = grid1 - grid2_resampled
    grid_list = [grid1, grid2_resampled, diff_grid]

    # plotting the individual grids with the same values on the colour bars
    cmaps = ["viridis", "viridis", "coolwarm"]
    max1, min1 = get_vmin_vmax(grid1.data)
    max2, min2 = get_vmin_vmax(grid2.data)
    vmin, vmax = np.min([min1, min2]), np.max([max1, max2])

    if not np.isnan(diff_grid.data).all():
        max_abs_val = np.nanmax(np.abs(diff_grid.data))
    else:
        max_abs_val = 1.0

    plot_grid(
        grid1,
        axes=grid_axes[0],
        cmap=cmaps[0],
        vmin=vmin,
        vmax=vmax,
        zoom=True,
        custom_shapefile=custom_shapefile,
        add_netherlands_shapefile=add_netherlands_shapefile
    )

    plot_grid(
        grid2,
        axes=grid_axes[1],
        cmap=cmaps[1],
        vmin=vmin,
        vmax=vmax,
        zoom=True,
        custom_shapefile=custom_shapefile,
        add_netherlands_shapefile=add_netherlands_shapefile
    )

    plot_grid(
        diff_grid,
        axes=grid_axes[2],
        cmap=cmaps[2],
        vmin=-max_abs_val,
        vmax=max_abs_val,
        zoom=True,
        custom_shapefile=custom_shapefile,
        add_netherlands_shapefile=add_netherlands_shapefile
    )

    # make histograms
    vmins = [vmin, vmin, -max_abs_val]
    vmaxs = [vmax, vmax, max_abs_val]
    for i in range(3):
        data = grid_list[i].data
        data = data[~np.isnan(data)]
        data = data.flatten()
        n, bins, patches = hist_axes[i].hist(data, bins=20)
        # Create a gradient color effect
        for j, p in enumerate(patches):
            cm = plt.get_cmap(cmaps[i])
            norm = mpl.colors.Normalize(vmin=vmins[i], vmax=vmaxs[i])
            plt.setp(p, 'facecolor', cm(norm(bins[j])))

    # add in the histogram from the other grid in the background:
    def add_background_hist(ax, data):
        data = data[~np.isnan(data)]
        data = data.flatten()
        ax.hist(data, bins=20, zorder=-1, color="lightgrey")

    hist_axes[0].set_title(f"Grid 1 dx: {grid1.x.data[1] - grid1.x.data[0]}m,"
                           f" dy: {grid1.y.data[1] - grid1.y.data[0]}m")
    add_background_hist(hist_axes[0], grid2_resampled.data)

    hist_axes[1].set_title(f"Grid 2 dx: {grid2.x.data[1] - grid2.x.data[0]}m,"
                           f" dy: {grid2.y.data[1] - grid2.y.data[0]}m")
    add_background_hist(hist_axes[1], grid1.data)

    hist_axes[2].set_title(f"Grid misfit: "
                           f"{calculate_grid_misfit(grid1, grid2_resampled)*100:.1f}%")

    # make titles
    if not np.isnan(grid1.data).all():
        minmax_string1 = (f"min: {np.nanmin(grid1.data):.3f}"
                          f"max: {np.nanmax(grid1.data):.3f}")
    else:
        minmax_string1 = "all NaNs"
    if title1 is None:
        grid_axes[0].set_title(f"grid 1\n{minmax_string1}")
    else:
        grid_axes[0].set_title(f"{title1}\n{minmax_string1}")

    if not np.isnan(grid2.data).all():
        minmax_string2 = (f"min: {np.nanmin(grid2.data):.3f}"
                          f"max: {np.nanmax(grid2.data):.3f}")
    else:
        minmax_string2 = "all NaNs"
    if title2 is None:
        grid_axes[1].set_title(f"grid 2\n{minmax_string2}")
    else:
        grid_axes[1].set_title(f"{title2}\n{minmax_string2}")

    if suptitle is not None:
        plt.suptitle(suptitle)
    addon = ""
    if not np.isnan(diff_grid.data).all():
        addon = (f"\nmin: {np.nanmin(diff_grid.data):.3f}"
                 f"max: {np.nanmax(diff_grid.data):.3f}")
    grid_axes[2].set_title("difference (grid1 - grid2)" + addon)

    plt.savefig(outfile)
    plt.close()


def add_shapefile_boundary_to_interactive_plot(shapefile_df, subsample=1):
    # get points from boundary
    boundaries = shapefile_df.boundary.explode(index_parts=True)
    traces = []
    for i in range(len(boundaries)):
        xvals, yvals = boundaries.values[i].xy
        xvals_subsample = np.array(xvals)[::subsample]
        yvals_subsample = np.array(yvals)[::subsample]
        traces.append(go.Scatter(x=xvals_subsample,
                                 y=yvals_subsample,
                                 mode='lines',
                                 hoverinfo='skip',
                                 showlegend=False,
                                 line=dict(color="black")))
    return traces


def make_interactive_plot(
    grids_xarray: list[xr.DataArray],
        gridnames: list[str],
        units=None,
        outfile=None,
        scatter_df=None,
        scatter_hovertext=None,
        scatter_z=None,
        add_netherlands_shapefile=False,
        title="",
):
    """
    Make plotly interactive plots; providing a list of grids, a list of grid names
    Parameters
    ----------
    grids_xarray
    gridnames
    units
    outfile
    scatter_df
    scatter_hovertext
    scatter_z
    netherlands_shapefile

    Returns
    -------

    """

    grids_dataset = combine_grids_in_dataset(grids_xarray, labels=gridnames)
    NGrids = len(gridnames)
    vmax, vmin = get_vmin_vmax(grids_dataset[gridnames[0]].data)
    variable0 = gridnames[0]

    # Add heatmap and well scatter trace
    if units is None:
        units = ["" for i in range(NGrids)]

    traces_map = []
    traces_map.append(
        go.Heatmap(z=grids_dataset[variable0].data, x=grids_dataset.x.values,
                   y=grids_dataset.y.values, colorbar_x=1.05, zmin=vmin, zmax=vmax,
                   colorscale="Viridis", name="heatmap"))

    # Histogram
    nbins = 40
    histogram_color = "darkgrey"
    traces_histogram = []
    flatten_data = grids_dataset[variable0].data.flatten()
    histogram_data = flatten_data[~np.isnan(flatten_data)]
    traces_histogram.append(
        go.Histogram(x=histogram_data, name="histogram",
                     nbinsx=nbins, marker=dict(color=histogram_color)))

    if scatter_df is not None:
        traces_map.append(
            go.Scatter(
                x=scatter_df.x, y=scatter_df.y, mode="markers",
                hovertext=scatter_hovertext, name="well data", showlegend=True,
                marker={"color": scatter_df[scatter_z], "colorscale": "viridis",
                        "cmin": vmin, "cmax": vmax,
                        "line": dict(width=2, color='DarkSlateGrey')}
            )
        )

    # instantiate figure
    fig = make_subplots(rows=2, cols=1, row_heights=[1, 0.25])
    if add_netherlands_shapefile:
        traces_map.extend(add_shapefile_boundary_to_interactive_plot(
            get_netherlands_shapefile()))
    for trace in traces_map:
        fig.add_trace(trace, row=1, col=1)
    fig.add_trace(traces_histogram[0], row=2, col=1)

    # collect grids for grid buttons for the heatmap
    grid_buttons = []
    for i in range(NGrids):
        gridname = gridnames[i]
        data = grids_dataset[gridname].data
        vmax, vmin = get_vmin_vmax(data)
        if scatter_df is not None:
            marker_argument = {"color": scatter_df[scatter_z],
                               "colorscale": "Viridis",
                               'cmin': vmin,
                               'cmax': vmax,
                               "line": dict(width=2, color='DarkSlateGrey')}

            grid_button_argument = {'z': [data], 'zmin': [vmin], 'zmax': [vmax],
                                            'marker': marker_argument}

            grid_buttons.append(dict(method="restyle",
                                     args=[grid_button_argument, [0, 1]],
                                     label=gridname))
        else:
            marker_argument = {"colorscale": "Viridis", 'cmin': vmin, 'cmax': vmax,
                               "line": dict(width=2, color='DarkSlateGrey')}
            grid_buttons.append(dict(method="restyle",
                                     args=[{'z': [data], 'zmin': [vmin], 'zmax': [vmax],
                                            'marker': marker_argument}, [0]],
                                     label=gridname))

    # collect grids for grid buttons for the histograms
    histogram_grid_buttons = []
    for i in range(NGrids):
        gridname = gridnames[i]
        flatten_data = grids_dataset[gridname].data.flatten()
        histogram_data = flatten_data[~np.isnan(flatten_data)]
        if len(histogram_data) == 0:
            histogram_data = [np.nan]
        histogram_grid_buttons.append(
            dict(method="restyle",
                 args=[{"x": histogram_data,
                        "nbinsx": nbins,
                        "marker": dict(color=histogram_color)},
                       [len(traces_map)]],
                 label=gridname))

    # Update plot sizing, and x and y labels
    fig.update_layout(
        width=800,
        height=1000,
        autosize=True,
        xaxis={"scaleanchor": "y"},
        dragmode='pan',
        showlegend=False
    )

    # Axis labels
    fig.update_xaxes(title_text="X RD new [m]", row=1, col=1)
    fig.update_yaxes(title_text="Y RD new [m]", row=1, col=1)
    fig.update_xaxes(title_text="Grid values", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)

    # Add dropdown menus
    button_layer_1_height = 1.06
    button_layer_1_width = 0.2
    button_layer_2_height = 0.23
    button_layer_2_width = 0.2
    fig.update_layout(
        title=title,
        updatemenus=[
            # list of grids
            dict(
                buttons=list(grid_buttons),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=button_layer_1_width,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top"
            ),

            # list of grids for histogram
            dict(
                buttons=list(histogram_grid_buttons),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=button_layer_2_width,
                xanchor="left",
                y=button_layer_2_height,
                yanchor="top"
            )
        ]
    )

    # add the text defining the grid of the histogram
    fig.update_layout(
        annotations=[
            dict(text="Grid for map:", x=button_layer_1_width - 0.17, xref="paper",
                 y=button_layer_1_height - 0.015, yref="paper",
                 showarrow=False),
            dict(text="(You have to change the<br>histogram data separately)",
                 x=button_layer_1_width + 0.75, xref="paper",
                 y=button_layer_1_height - 0.02, yref="paper",
                 showarrow=False, font={'size': 10, 'color': "IndianRed"}),
            dict(text="Grid for histogram:", x=button_layer_2_width - 0.21,
                 xref="paper", y=button_layer_2_height - 0.04, yref="paper",
                 showarrow=False),
            dict(text="(You have to change the<br>map data separately)",
                 x=button_layer_1_width + 0.75, xref="paper",
                 y=button_layer_2_height - 0.05, yref="paper",
                 showarrow=False, font={'size': 10, 'color': "IndianRed"}),
        ])

    if outfile:
        fig.write_html(outfile, config={'scrollZoom': True})
    else:
        fig.show()
