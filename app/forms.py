"""Shared Streamlit form widgets used by every dataset page.

Each widget returns a Python value the caller can plug straight into a
download function. Widgets do not perform downloads themselves; they
only build config.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import streamlit as st


# Named bbox presets. Custom is handled separately.
BBOX_PRESETS: dict[str, list[float]] = {
    "UK (55, -8, 49, 2)": [55.0, -8.0, 49.0, 2.0],
    "Europe (72, -25, 34, 45)": [72.0, -25.0, 34.0, 45.0],
    "Global (90, -180, -90, 180)": [90.0, -180.0, -90.0, 180.0],
    "East Africa (15, 34, -5, 42)": [15.0, 34.0, -5.0, 42.0],
    "Sahel (18, -10, 10, 20)": [18.0, -10.0, 10.0, 20.0],
    "Central America (20, -95, 5, -75)": [20.0, -95.0, 5.0, -75.0],
    "Continental US (50, -125, 24, -66)": [50.0, -125.0, 24.0, -66.0],
    "Australia (-10, 112, -45, 155)": [-10.0, 112.0, -45.0, 155.0],
}


@dataclass
class BBox:
    """Bounding box in the CDS [north, west, south, east] order."""

    north: float
    west: float
    south: float
    east: float

    def as_list(self) -> list[float]:
        return [self.north, self.west, self.south, self.east]


def bbox_input(
    label: str = "Region",
    default_preset: str = "UK (55, -8, 49, 2)",
    key_prefix: str = "bbox",
) -> BBox:
    """Render a bbox selector: preset dropdown with optional custom override.

    Returns a BBox. The user can pick a named region or select "Custom"
    to type four numbers.
    """
    preset = st.selectbox(
        label,
        ["Custom", *BBOX_PRESETS.keys()],
        index=1 + list(BBOX_PRESETS).index(default_preset),
        key=f"{key_prefix}_preset",
    )

    if preset == "Custom":
        c1, c2, c3, c4 = st.columns(4)
        n = c1.number_input("North", -90.0, 90.0, 55.0, 0.5, key=f"{key_prefix}_n")
        w = c2.number_input("West", -180.0, 180.0, -8.0, 0.5, key=f"{key_prefix}_w")
        s = c3.number_input("South", -90.0, 90.0, 49.0, 0.5, key=f"{key_prefix}_s")
        e = c4.number_input("East", -180.0, 180.0, 2.0, 0.5, key=f"{key_prefix}_e")
        return BBox(n, w, s, e)

    values = BBOX_PRESETS[preset]
    return BBox(*values)


def year_range_input(
    label: str = "Years",
    default: tuple[int, int] = (2023, 2023),
    min_year: int = 1850,
    max_year: int = 2026,
    key_prefix: str = "years",
) -> list[str]:
    """Pick a year range, return a list of stringified years."""
    start, end = st.slider(
        label,
        min_year, max_year,
        default,
        key=f"{key_prefix}_range",
    )
    return [str(y) for y in range(start, end + 1)]


def month_multiselect(
    label: str = "Months",
    default: tuple[int, ...] = (7,),
    key_prefix: str = "months",
) -> list[str]:
    """Pick a set of months, return a list of zero-padded strings."""
    month_names = [
        "01 Jan", "02 Feb", "03 Mar", "04 Apr", "05 May", "06 Jun",
        "07 Jul", "08 Aug", "09 Sep", "10 Oct", "11 Nov", "12 Dec",
    ]
    selected = st.multiselect(
        label,
        month_names,
        default=[month_names[m - 1] for m in default],
        key=f"{key_prefix}_ms",
    )
    return [name.split()[0] for name in selected]


def day_multiselect(
    label: str = "Days of month",
    default_all: bool = False,
    key_prefix: str = "days",
) -> list[str]:
    """Pick days of month (1-31), zero-padded strings.

    If ``default_all`` is True the default selection is every day; useful
    when the user is likely to want a full month.
    """
    days = [f"{d:02d}" for d in range(1, 32)]
    default = days if default_all else ["01"]
    selected = st.multiselect(
        label,
        days,
        default=default,
        key=f"{key_prefix}_ms",
    )
    return selected


def hour_multiselect(
    label: str = "Hours (UTC)",
    default_all: bool = False,
    key_prefix: str = "hours",
) -> list[str]:
    """Pick hours-of-day, HH:00 strings."""
    hours = [f"{h:02d}:00" for h in range(24)]
    default = hours if default_all else ["12:00"]
    selected = st.multiselect(
        label,
        hours,
        default=default,
        key=f"{key_prefix}_ms",
    )
    return selected


def output_dir_input(
    slug: str,
    key_prefix: str = "output",
) -> tuple[str, str]:
    """Render output directory and filename inputs.

    Defaults to ``./data/{slug}/`` and a sensible filename.
    Returns ``(output_dir, output_filename)``.
    """
    default_dir = f"./data/{slug}"
    default_filename = f"{slug.replace('-', '_')}_download.nc"

    c1, c2 = st.columns([2, 3])
    output_dir = c1.text_input(
        "Output directory",
        value=default_dir,
        key=f"{key_prefix}_dir",
    )
    output_filename = c2.text_input(
        "Output filename",
        value=default_filename,
        key=f"{key_prefix}_name",
    )
    return output_dir, output_filename


def result_panel(output_path: Path) -> None:
    """Render the post-download result: size, xarray summary, open folder.

    Optional quick plot is a toggle inside an expander; renders lazily
    only when the user asks for it.
    """
    st.success(f"Saved to `{output_path}` ({output_path.stat().st_size / 1e6:.2f} MB)")

    try:
        import xarray as xr

        ds = xr.open_dataset(output_path)
        with st.expander("Dataset summary (xarray)", expanded=True):
            st.text(repr(ds))
        if st.toggle("Show quick plot", key="quick_plot"):
            _render_quick_plot(ds)
        ds.close()
    except Exception as exc:
        st.info(f"xarray could not open the file automatically: {exc}")


def _render_quick_plot(ds) -> None:
    """Best-effort one-panel plot of the first data variable.

    If the field is 2D it is rendered as a map using cartopy PlateCarree.
    If it is 1D (a time series), a simple line plot is rendered.
    Anything else: skip with a message.
    """
    import matplotlib.pyplot as plt

    data_vars = list(ds.data_vars)
    if not data_vars:
        st.info("No data variables to plot.")
        return
    var = data_vars[0]
    da = ds[var].squeeze()

    if da.ndim == 2 and {"latitude", "longitude"}.issubset(da.dims):
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        fig = plt.figure(figsize=(9, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        da.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="viridis")
        ax.coastlines(resolution="50m", linewidth=0.6)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="gray")
        ax.set_title(f"{var} (quick preview)")
        st.pyplot(fig)
    elif da.ndim == 1:
        fig, ax = plt.subplots(figsize=(9, 3))
        da.plot(ax=ax)
        ax.set_title(f"{var} (quick preview)")
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.info(
            f"{var} has dims {da.dims}, too many for an automatic quick plot. "
            "Open the file in a notebook to explore."
        )
