"""Plotting defaults for quickstart notebooks.

Keeping plot style consistent across datasets helps readers recognise the repo's
output and compare datasets side by side.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import matplotlib.pyplot as plt


# Default colourmap for temperature-like variables (diverging)
TEMP_CMAP = "RdBu_r"

# Default colourmap for precipitation-like variables (sequential)
PRECIP_CMAP = "YlGnBu"

# Default colourmap for generic sequential data
SEQUENTIAL_CMAP = "viridis"

# Default figure size for single maps
MAP_FIGSIZE = (10, 6)

# Default figure size for time series
TIMESERIES_FIGSIZE = (10, 4)


def standard_map_axes(ax: "plt.Axes") -> None:
    """Apply standard formatting to a cartopy map axis.

    Adds coastlines, country borders, gridlines with labels. Call after creating
    a cartopy GeoAxes.

    Args:
        ax: A matplotlib axis with a cartopy projection.
    """
    import cartopy.feature as cfeature

    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4, edgecolor="gray")
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
