"""Shared Streamlit form widgets used by every dataset page.

Each widget returns a Python value the caller can plug straight into a
download function. Widgets do not perform downloads themselves; they
only build config.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import streamlit as st

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr


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
    """Render the post-download result: size, summary, optional plot.

    Detects file type and uses pandas for tabular formats (CSV, txt)
    or xarray for gridded formats (NetCDF, GRIB).
    """
    st.success(f"Saved to `{output_path}` ({output_path.stat().st_size / 1e6:.2f} MB)")

    suffix = output_path.suffix.lower()
    if suffix in (".csv", ".txt", ".dat"):
        _tabular_panel(output_path)
    else:
        _gridded_panel(output_path)


def _tabular_panel(output_path: Path) -> None:
    """Show a preview for CSV/text files using pandas.

    Falls back to xarray if the file turns out to be binary despite
    having a text-like extension (e.g. NetCDF saved as .csv).
    """
    try:
        import pandas as pd

        df = pd.read_csv(output_path)
        with st.expander("Data preview (first 50 rows)", expanded=True):
            st.dataframe(df.head(50), use_container_width=True, hide_index=True)
        st.caption(f"{len(df):,} rows, {len(df.columns)} columns")
        if st.toggle("Explore data", key="quick_plot"):
            _render_tabular_plot(df, output_path)
    except Exception:
        # File is likely binary despite the extension - try xarray.
        _gridded_panel(output_path)


def _render_tabular_plot(df: pd.DataFrame, output_path: Path) -> None:
    """Interactive explorer for tabular data with subsetting, multiple views."""
    import matplotlib.pyplot as plt

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.info("No numeric columns to plot.")
        return

    col = st.selectbox("Column to plot", numeric_cols, key="tabular_plot_col")

    # Row subsetting
    total_rows = len(df)
    row_range = st.slider(
        "Row range",
        0, total_rows - 1, (0, total_rows - 1),
        key="tabular_row_range",
        help="Subset the data by row index. Useful for focusing on a specific period.",
    )
    subset = df.iloc[row_range[0]:row_range[1] + 1]
    if row_range != (0, total_rows - 1):
        st.caption(f"Showing rows {row_range[0]:,} to {row_range[1]:,} ({len(subset):,} rows)")

    views = ["Time series", "Distribution", "Rolling mean"]
    view = st.segmented_control("View", views, default="Time series", key="tab_view")

    if view == "Time series":
        st.caption(
            "The raw values plotted in order. For time-indexed data (like HadCET), "
            "each point is one observation. Look for trends, seasonality, and outliers."
        )

        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.plot(subset[col].values, linewidth=0.7)
        ax.set_ylabel(col)
        ax.set_title(col)
        ax.grid(alpha=0.3)
        st.pyplot(fig)

        with st.expander(":material/code: Code for this plot"):
            code = (
                "import pandas as pd\n"
                "import matplotlib.pyplot as plt\n\n"
                f'df = pd.read_csv("{output_path}")\n'
            )
            if row_range != (0, total_rows - 1):
                code += f"df = df.iloc[{row_range[0]}:{row_range[1] + 1}]\n"
            code += (
                f'df["{col}"].plot()\n'
                "plt.grid(alpha=0.3)\n"
                "plt.tight_layout()\n"
                "plt.show()"
            )
            st.code(code, language="python")

    elif view == "Distribution":
        st.caption(
            "A histogram showing how frequently each value occurs. "
            "A normal (bell-shaped) distribution is common for temperature. "
            "Skewed distributions are typical for precipitation (many dry days, few wet)."
        )

        bins = st.slider("Number of bins", 10, 200, 50, key="hist_bins")
        values = subset[col].dropna().values

        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.hist(values, bins=bins, edgecolor="white", linewidth=0.3)
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        ax.set_title(f"Distribution of {col}")
        ax.grid(alpha=0.3, axis="y")
        st.pyplot(fig)

        st.caption(
            f"Mean: {values.mean():.3f}, Std: {values.std():.3f}, "
            f"Min: {values.min():.3f}, Max: {values.max():.3f}"
        )

        with st.expander(":material/code: Code for this plot"):
            code = (
                "import pandas as pd\n"
                "import matplotlib.pyplot as plt\n\n"
                f'df = pd.read_csv("{output_path}")\n'
            )
            if row_range != (0, total_rows - 1):
                code += f"df = df.iloc[{row_range[0]}:{row_range[1] + 1}]\n"
            code += (
                f'df["{col}"].dropna().hist(bins={bins})\n'
                f'plt.xlabel("{col}")\n'
                'plt.ylabel("Count")\n'
                "plt.tight_layout()\n"
                "plt.show()"
            )
            st.code(code, language="python")

    elif view == "Rolling mean":
        st.caption(
            "A rolling (moving) mean smooths out short-term variability to reveal "
            "the underlying trend. The window size controls how much smoothing is "
            "applied: a small window (e.g. 12 for monthly data = 1 year) preserves "
            "more detail, while a large window (e.g. 120 = 10 years) shows only the "
            "long-term signal. The raw data is shown faded behind for comparison."
        )

        window = st.slider(
            "Window size (number of data points)",
            2, min(len(subset) // 2, 1000), min(30, len(subset) // 4),
            key="rolling_window",
            help=(
                "For monthly data: 12 = 1 year, 60 = 5 years, 120 = 10 years. "
                "For daily data: 30 = 1 month, 365 = 1 year."
            ),
        )
        series = subset[col].dropna()
        rolling = series.rolling(window, center=True).mean()

        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.plot(series.values, linewidth=0.4, alpha=0.3, label="Raw data")
        ax.plot(rolling.values, linewidth=1.8, label=f"{window}-point rolling mean")
        ax.set_ylabel(col)
        ax.set_title(f"{col} with {window}-point rolling mean")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

        st.caption(
            f"The rolling mean uses a centred window of {window} points. "
            f"The first and last {window // 2} values will be NaN (not enough "
            f"neighbours to compute the average)."
        )

        with st.expander(":material/code: Code for this plot"):
            code = (
                "import pandas as pd\n"
                "import matplotlib.pyplot as plt\n\n"
                f'df = pd.read_csv("{output_path}")\n'
            )
            if row_range != (0, total_rows - 1):
                code += f"df = df.iloc[{row_range[0]}:{row_range[1] + 1}]\n"
            code += (
                f'raw = df["{col}"].dropna()\n'
                f"rolling = raw.rolling({window}, center=True).mean()\n\n"
                "fig, ax = plt.subplots(figsize=(10, 4))\n"
                'ax.plot(raw.values, alpha=0.3, linewidth=0.4, label="Raw data")\n'
                f'ax.plot(rolling.values, linewidth=1.8, label="{window}-point rolling mean")\n'
                "ax.legend()\n"
                "ax.grid(alpha=0.3)\n"
                "plt.tight_layout()\n"
                "plt.show()"
            )
            st.code(code, language="python")


def _open_dataset(output_path: Path) -> xr.Dataset:
    """Open a NetCDF or GRIB file, choosing the right engine automatically."""
    import xarray as xr

    suffix = output_path.suffix.lower()
    if suffix in (".grib", ".grib2", ".grb", ".grb2"):
        return xr.open_dataset(output_path, engine="cfgrib")
    return xr.open_dataset(output_path)


def _gridded_panel(output_path: Path) -> None:
    """Interactive preview for NetCDF/GRIB files using xarray."""
    try:
        ds = _open_dataset(output_path)
    except Exception as exc:
        st.info(f"xarray could not open the file: {exc}")
        return

    with st.expander("Dataset summary (xarray)", expanded=True):
        st.text(repr(ds))

    if st.toggle("Explore data", key="quick_plot"):
        try:
            _interactive_plot(ds, output_path)
        except Exception as exc:
            st.error(f"Plot failed: {type(exc).__name__}: {exc}")

    ds.close()


def _detect_dims(da: xr.DataArray) -> dict[str, str | None]:
    """Identify standard dimension names in a DataArray."""
    lat = next((d for d in da.dims if d in ("latitude", "lat")), None)
    lon = next((d for d in da.dims if d in ("longitude", "lon")), None)
    time = next((d for d in da.dims if d in ("time", "valid_time")), None)
    step = next((d for d in da.dims if d == "step"), None)
    ens = next(
        (d for d in da.dims if d in (
            "number", "realization", "member", "ensemble", "model", "source_id",
        )),
        None,
    )
    return {"lat": lat, "lon": lon, "time": time, "step": step, "ens": ens}


def _time_like_dim(dims: dict[str, str | None]) -> str | None:
    """Return whichever time-like dimension exists (time or step)."""
    return dims["time"] or dims["step"]


def _format_step_label(val: object) -> str:
    """Human-readable label for a step/time coordinate value."""
    import numpy as np

    if isinstance(val, np.timedelta64):
        days = int(val / np.timedelta64(1, "D"))
        if days >= 28:
            months = round(days / 30.44)
            return f"Month {months} ({days}d)"
        return f"{days}d"
    s = str(val)
    if "days" in s:
        return s.split(",")[0]
    return s[:16]


def _convert_cftime(ds: xr.Dataset) -> xr.Dataset:
    """Convert cftime time coordinates to pandas-compatible datetime64.

    CMIP6 models use non-standard calendars (noleap, 360_day) that
    matplotlib cannot plot without nc-time-axis. Converting to standard
    timestamps avoids the dependency at the cost of slightly inaccurate
    day-of-month for 360-day calendars.
    """
    import pandas as pd

    for dim in list(ds.dims):
        if dim not in ("time", "valid_time"):
            continue
        vals = ds[dim].values
        if len(vals) == 0 or not hasattr(vals[0], "year"):
            continue
        try:
            time_pd = pd.DatetimeIndex([
                pd.Timestamp(t.year, t.month, min(t.day, 28))
                for t in vals
            ])
            ds = ds.assign_coords({dim: time_pd})
        except Exception:
            pass
    return ds


def _interactive_plot(
    ds: xr.Dataset,
    output_path: Path | None = None,
    *,
    open_code: str | None = None,
) -> None:
    """Interactive explorer with multiple view modes and code snippets.

    Either output_path (file-based) or open_code (streaming) should be
    provided so that code snippets know how to open the data.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        import nc_time_axis  # noqa: F401 - registers cftime with matplotlib
    except ImportError:
        pass

    # Convert cftime calendars (noleap, 360_day) to pandas timestamps so
    # matplotlib can plot them without nc-time-axis edge cases.
    ds = _convert_cftime(ds)

    if open_code is None and output_path is not None:
        _oc = _snippet_open_line(output_path)
    elif open_code is not None:
        _oc = open_code
    else:
        _oc = 'ds = xr.open_dataset("your_file.nc")'

    data_vars = [
        v for v in ds.data_vars
        if not any(tag in v for tag in ("bnds", "bounds", "bound"))
        and not np.issubdtype(ds[v].dtype, np.datetime64)
    ]
    if not data_vars:
        st.info("No plottable data variables found.")
        return

    if len(data_vars) > 1:
        var = st.selectbox("Variable", data_vars, key="plot_var")
    else:
        var = data_vars[0]

    da = ds[var].squeeze()
    dims = _detect_dims(da)
    has_space = bool(dims["lat"] and dims["lon"])
    tdim = _time_like_dim(dims)
    has_time = bool(tdim)
    has_ens = bool(dims["ens"])
    ens_dim = dims["ens"]

    # ── Build view list ────────────────────────────────────────────
    views: list[str] = []
    if has_ens and has_time and has_space:
        views = [
            "Ensemble spread",
            "Ensemble spaghetti",
            "Ensemble statistics",
            "Map (ensemble mean)",
        ]
    elif has_ens and has_time:
        views = ["Ensemble spread", "Ensemble spaghetti", "Ensemble statistics"]
    elif has_ens and has_space:
        views = ["Map (ensemble mean)", "Ensemble statistics"]
    elif has_space and has_time:
        views = ["Map (single time step)", "Time series (area mean)"]
    elif has_space:
        views = ["Map"]
    elif has_time:
        views = ["Time series"]
    else:
        st.info(f"{var} has dims {da.dims} - cannot auto-plot.")
        return

    view = st.segmented_control("View", views, default=views[0], key="plot_view")

    # ── Time subsetting ────────────────────────────────────────────
    time_start = 0
    time_end = None
    if has_time:
        n_steps = da.sizes[tdim]
        time_coords = da.coords[tdim].values
        if n_steps > 1:
            time_range = st.slider(
                "Time / lead-time range",
                0, n_steps - 1, (0, n_steps - 1),
                key="plot_time_range",
                help=(
                    f"{n_steps} steps total. "
                    f"{_format_step_label(time_coords[0])} to "
                    f"{_format_step_label(time_coords[-1])}"
                ),
            )
            time_start, time_end = time_range
            if time_start > 0 or time_end < n_steps - 1:
                da = da.isel({tdim: slice(time_start, time_end + 1)})

    # ── Ensemble spread ────────────────────────────────────────────
    if view == "Ensemble spread":
        st.caption(
            "Each ensemble member starts from slightly different initial "
            "conditions. The shaded bands show where most members fall. A wider "
            "band means more forecast uncertainty at that lead time."
        )
        if has_space:
            ts = da.mean([dims["lat"], dims["lon"]])
        else:
            ts = da

        ens_mean = ts.mean(dim=ens_dim)
        ens_std = ts.std(dim=ens_dim)
        p10 = ts.quantile(0.1, dim=ens_dim)
        p25 = ts.quantile(0.25, dim=ens_dim)
        p75 = ts.quantile(0.75, dim=ens_dim)
        p90 = ts.quantile(0.9, dim=ens_dim)

        x = np.arange(len(ens_mean[tdim]))
        x_labels = [_format_step_label(v) for v in ens_mean.coords[tdim].values]

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.fill_between(x, p10.values, p90.values, alpha=0.15, color="C0", label="10th-90th percentile")
        ax.fill_between(x, p25.values, p75.values, alpha=0.3, color="C0", label="25th-75th percentile")
        ax.plot(x, ens_mean.values, linewidth=2, color="C0", label="Ensemble mean")
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=30, ha="right")
        ax.set_ylabel(var)
        ax.set_title(f"{var} - ensemble spread ({da.sizes[ens_dim]} members)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)

        with st.expander(":material/code: Code for this plot"):
            st.code(
                _snippet_ensemble_spread(_oc, var, tdim, ens_dim, dims["lat"], dims["lon"], has_space),
                language="python",
            )

    # ── Ensemble spaghetti ─────────────────────────────────────────
    elif view == "Ensemble spaghetti":
        st.caption(
            "Every ensemble member drawn as its own line. Clusters of lines "
            "that stay close together indicate higher confidence. Where members "
            "fan apart, the forecast is less certain."
        )
        if has_space:
            ts = da.mean([dims["lat"], dims["lon"]])
        else:
            ts = da

        n_members = ts.sizes[ens_dim]
        max_show = st.slider(
            "Members to show", 1, n_members, min(n_members, 25),
            key="spaghetti_n",
            help=f"{n_members} members available. Showing fewer keeps the plot readable.",
        )

        x = np.arange(ts.sizes[tdim])
        x_labels = [_format_step_label(v) for v in ts.coords[tdim].values]

        fig, ax = plt.subplots(figsize=(9, 4))
        for i in range(max_show):
            member = ts.isel({ens_dim: i})
            ax.plot(x, member.values, linewidth=0.6, alpha=0.5, color="C0")

        ens_mean = ts.mean(dim=ens_dim)
        ax.plot(x, ens_mean.values, linewidth=2.5, color="C3", label="Ensemble mean")

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=30, ha="right")
        ax.set_ylabel(var)
        ax.set_title(f"{var} - {max_show} of {n_members} ensemble members")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)

        with st.expander(":material/code: Code for this plot"):
            st.code(
                _snippet_ensemble_spaghetti(_oc, var, tdim, ens_dim, dims["lat"], dims["lon"], has_space),
                language="python",
            )

    # ── Ensemble statistics ────────────────────────────────────────
    elif view == "Ensemble statistics":
        st.caption(
            "Summary statistics across all ensemble members at each lead time. "
            "The range (max minus min) shows total ensemble spread. Standard "
            "deviation quantifies how tightly members agree."
        )
        if has_space:
            ts = da.mean([dims["lat"], dims["lon"]])
        else:
            ts = da

        import pandas as pd

        stats_rows = []
        for i in range(ts.sizes[tdim]):
            step_data = ts.isel({tdim: i})
            vals = step_data.values.ravel()
            label = _format_step_label(ts.coords[tdim].values[i])
            stats_rows.append({
                "Lead time": label,
                "Mean": float(np.nanmean(vals)),
                "Std": float(np.nanstd(vals)),
                "Min": float(np.nanmin(vals)),
                "25th pctl": float(np.nanpercentile(vals, 25)),
                "Median": float(np.nanmedian(vals)),
                "75th pctl": float(np.nanpercentile(vals, 75)),
                "Max": float(np.nanmax(vals)),
                "Range": float(np.nanmax(vals) - np.nanmin(vals)),
            })

        stats_df = pd.DataFrame(stats_rows)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        n_members = ts.sizes[ens_dim]
        overall_vals = ts.values.ravel()
        with st.container(horizontal=True):
            st.metric("Members", str(n_members), border=True)
            st.metric("Overall mean", f"{np.nanmean(overall_vals):.2f}", border=True)
            st.metric("Overall std", f"{np.nanstd(overall_vals):.2f}", border=True)
            st.metric(
                "Max spread",
                f"{stats_df['Range'].max():.2f}",
                help="Largest range across any single lead time",
                border=True,
            )

        with st.expander(":material/code: Code for ensemble statistics"):
            st.code(
                _snippet_ensemble_stats(_oc, var, tdim, ens_dim, dims["lat"], dims["lon"], has_space),
                language="python",
            )

    # ── Map (ensemble mean or single time) ─────────────────────────
    elif view and "Map" in view:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        if has_ens:
            st.caption(
                "Spatial map of the ensemble mean. The mean smooths out "
                "individual member noise and shows the most likely field."
            )
            map_mode = st.radio(
                "Show",
                ["Ensemble mean", "Ensemble std", "Single member"],
                horizontal=True,
                key="map_ens_mode",
            )
        else:
            st.caption(
                "A spatial map of the field at a single point in time. "
                "Drag the slider to step through different dates."
            )
            map_mode = None

        if has_time:
            subset_steps = da.sizes[tdim]
            step_idx = st.slider(
                "Time step within range", 0, subset_steps - 1, 0,
                key="plot_time_step",
                help="Select which time step to display on the map.",
            )
            plot_da = da.isel({tdim: step_idx})
            time_label = _format_step_label(da.coords[tdim].values[step_idx])
            st.caption(f"Showing: {time_label}")
        else:
            plot_da = da
            time_label = None

        if has_ens:
            if map_mode == "Ensemble mean":
                plot_da = plot_da.mean(dim=ens_dim)
                subtitle = "ensemble mean"
            elif map_mode == "Ensemble std":
                plot_da = plot_da.std(dim=ens_dim)
                subtitle = "ensemble std"
            else:
                member_idx = st.number_input(
                    "Member index", 0, da.sizes[ens_dim] - 1, 0, key="map_member",
                )
                plot_da = plot_da.isel({ens_dim: member_idx})
                subtitle = f"member {member_idx}"
        else:
            subtitle = None

        fig = plt.figure(figsize=(9, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plot_da.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="viridis")
        ax.coastlines(resolution="50m", linewidth=0.6)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="gray")
        parts = [var]
        if time_label:
            parts.append(time_label)
        if subtitle:
            parts.append(subtitle)
        ax.set_title(" - ".join(parts))
        st.pyplot(fig)

        with st.expander(":material/code: Code for this map"):
            step_val = (time_start + step_idx) if has_time else None
            st.code(_snippet_map(_oc, var, tdim, step_val), language="python")

    # ── Time series (non-ensemble) ─────────────────────────────────
    elif view and "Time series" in view:
        st.caption(
            "The spatially-averaged value at each time step. This collapses the "
            "map down to a single number per time step, showing how the field "
            "evolves over time across the whole region."
        )
        if has_space:
            ts = da.mean([dims["lat"], dims["lon"]])
        else:
            ts = da

        fig, ax = plt.subplots(figsize=(9, 3.5))
        ts.plot(ax=ax)
        ax.set_title(f"{var} - {'area mean' if has_space else 'time series'}")
        ax.grid(alpha=0.3)
        st.pyplot(fig)

        if has_space:
            st.caption(
                "This is a simple (unweighted) mean. Grid cells near the poles are "
                "smaller than those at the equator, so for a proper global average "
                "you should weight by cos(latitude). The code below shows both."
            )

        with st.expander(":material/code: Code for this time series"):
            st.code(
                _snippet_timeseries(_oc, var, tdim, dims["lat"], dims["lon"], has_space),
                language="python",
            )



def streaming_preview_panel(ds: xr.Dataset, open_snippet: str) -> None:
    """Render the interactive explorer for a streamed (in-memory) dataset.

    This is the streaming counterpart to result_panel(). Instead of
    reading from a file, the caller passes an already-loaded xr.Dataset
    and the open_snippet that code snippets should use.
    """
    with st.expander("Dataset summary (xarray)", expanded=True):
        st.text(repr(ds))
    _interactive_plot(ds, open_code=open_snippet)


# ──────────────────────────────────────────────────────────────────────
# Code snippet generators
# ──────────────────────────────────────────────────────────────────────

def _snippet_map(open_code: str, var: str, time_dim: str | None, step: int | None) -> str:
    lines = [
        "import xarray as xr",
        "import matplotlib.pyplot as plt",
        "import cartopy.crs as ccrs",
        "import cartopy.feature as cfeature",
        "",
        open_code,
        f'da = ds["{var}"]',
    ]
    if time_dim and step is not None:
        lines.append(f"da = da.isel({time_dim}={step})")
    lines += [
        "",
        "fig = plt.figure(figsize=(10, 6))",
        "ax = plt.axes(projection=ccrs.PlateCarree())",
        'da.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="viridis")',
        'ax.coastlines(resolution="50m")',
        "ax.add_feature(cfeature.BORDERS, linewidth=0.3)",
        f'ax.set_title("{var}")',
        "plt.tight_layout()",
        "plt.show()",
    ]
    return "\n".join(lines)


def _snippet_timeseries(
    open_code: str, var: str,
    time_dim: str | None, lat_dim: str | None, lon_dim: str | None,
    has_space: bool,
) -> str:
    lines = [
        "import xarray as xr",
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "",
        open_code,
        f'da = ds["{var}"]',
        "",
    ]
    if has_space:
        lines += [
            "# Simple area mean (unweighted)",
            f'simple_mean = da.mean(["{lat_dim}", "{lon_dim}"])',
            "",
            "# Area-weighted mean (accounts for grid cell size varying with latitude)",
            f'weights = np.cos(np.deg2rad(ds["{lat_dim}"]))',
            f'weighted = da.weighted(weights)',
            f'weighted_mean = weighted.mean(["{lat_dim}", "{lon_dim}"])',
            "",
            "fig, ax = plt.subplots(figsize=(10, 4))",
            'simple_mean.plot(ax=ax, label="Simple mean", alpha=0.7)',
            'weighted_mean.plot(ax=ax, label="Area-weighted mean", alpha=0.7)',
            "ax.legend()",
            "ax.grid(alpha=0.3)",
            f'ax.set_title("{var} - area mean time series")',
            "plt.tight_layout()",
            "plt.show()",
        ]
    else:
        lines += [
            "da.plot()",
            "plt.grid(alpha=0.3)",
            "plt.tight_layout()",
            "plt.show()",
        ]
    return "\n".join(lines)


def _snippet_open_line(output_path: Path) -> str:
    """Return the xr.open_dataset line with the right engine for the file type."""
    suffix = output_path.suffix.lower()
    if suffix in (".grib", ".grib2", ".grb", ".grb2"):
        return f'ds = xr.open_dataset("{output_path}", engine="cfgrib")'
    return f'ds = xr.open_dataset("{output_path}")'


def _snippet_ensemble_spread(
    open_code: str, var: str, time_dim: str, ens_dim: str,
    lat_dim: str | None, lon_dim: str | None, has_space: bool,
) -> str:
    lines = [
        "import xarray as xr",
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "",
        open_code,
        f'da = ds["{var}"]',
        "",
    ]
    if has_space:
        lines.append(f'da = da.mean(["{lat_dim}", "{lon_dim}"])')
        lines.append("")
    lines += [
        f'ens_mean = da.mean(dim="{ens_dim}")',
        f'p10 = da.quantile(0.1, dim="{ens_dim}")',
        f'p25 = da.quantile(0.25, dim="{ens_dim}")',
        f'p75 = da.quantile(0.75, dim="{ens_dim}")',
        f'p90 = da.quantile(0.9, dim="{ens_dim}")',
        "",
        "x = np.arange(len(ens_mean))",
        "",
        "fig, ax = plt.subplots(figsize=(10, 4))",
        'ax.fill_between(x, p10.values, p90.values, alpha=0.15, label="10th-90th pctl")',
        'ax.fill_between(x, p25.values, p75.values, alpha=0.3, label="25th-75th pctl")',
        'ax.plot(x, ens_mean.values, linewidth=2, label="Ensemble mean")',
        "ax.legend()",
        "ax.grid(alpha=0.3)",
        f'ax.set_ylabel("{var}")',
        f'ax.set_title("{var} - ensemble spread")',
        "plt.tight_layout()",
        "plt.show()",
    ]
    return "\n".join(lines)


def _snippet_ensemble_spaghetti(
    open_code: str, var: str, time_dim: str, ens_dim: str,
    lat_dim: str | None, lon_dim: str | None, has_space: bool,
) -> str:
    lines = [
        "import xarray as xr",
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "",
        open_code,
        f'da = ds["{var}"]',
        "",
    ]
    if has_space:
        lines.append(f'da = da.mean(["{lat_dim}", "{lon_dim}"])')
        lines.append("")
    lines += [
        f'n_members = da.sizes["{ens_dim}"]',
        "",
        "fig, ax = plt.subplots(figsize=(10, 4))",
        "for i in range(n_members):",
        f'    member = da.isel({ens_dim}=i)',
        '    ax.plot(member.values, linewidth=0.6, alpha=0.5, color="C0")',
        "",
        f'ens_mean = da.mean(dim="{ens_dim}")',
        'ax.plot(ens_mean.values, linewidth=2.5, color="C3", label="Ensemble mean")',
        "ax.legend()",
        "ax.grid(alpha=0.3)",
        f'ax.set_ylabel("{var}")',
        f'ax.set_title(f"{var} - {{n_members}} ensemble members")',
        "plt.tight_layout()",
        "plt.show()",
    ]
    return "\n".join(lines)


def _snippet_ensemble_stats(
    open_code: str, var: str, time_dim: str, ens_dim: str,
    lat_dim: str | None, lon_dim: str | None, has_space: bool,
) -> str:
    lines = [
        "import xarray as xr",
        "import numpy as np",
        "import pandas as pd",
        "",
        open_code,
        f'da = ds["{var}"]',
        "",
    ]
    if has_space:
        lines.append(f'da = da.mean(["{lat_dim}", "{lon_dim}"])')
        lines.append("")
    lines += [
        "# Per-step statistics across ensemble members",
        "stats = pd.DataFrame({",
        f'    "mean": da.mean(dim="{ens_dim}").values,',
        f'    "std": da.std(dim="{ens_dim}").values,',
        f'    "min": da.min(dim="{ens_dim}").values,',
        f'    "max": da.max(dim="{ens_dim}").values,',
        "})",
        'stats["range"] = stats["max"] - stats["min"]',
        "print(stats)",
    ]
    return "\n".join(lines)


def download_code_snippet(slug: str, config: dict[str, Any]) -> str:
    """Build a fully standalone download snippet for the dataset + form config.

    Returns valid Python the user can paste into an empty .py file or
    notebook cell anywhere on disk - no dependency on this repo. See
    ``app.standalone_script`` for the transformer.
    """
    from app.standalone_script import standalone_snippet

    return standalone_snippet(slug, config)


def chunked_download_options(
    key_prefix: str = "chunk",
    default_chunk_by: str = "month",
    show_merge: bool = True,
) -> dict[str, Any] | None:
    """Render chunked download toggle and options.

    Returns a dict with keys ``enabled``, ``chunk_by``, ``max_retries``,
    ``merge_output`` when enabled, or None when disabled.
    """
    with st.expander("Chunked download (for large date ranges)"):
        enabled = st.checkbox(
            "Split into chunks",
            value=False,
            key=f"{key_prefix}_enabled",
            help=(
                "Downloads each month (or year) as a separate request. "
                "Completed chunks are skipped on re-run; failed chunks "
                "are retried automatically."
            ),
        )
        if not enabled:
            st.caption(
                "Enable this for multi-month or multi-year pulls. Each "
                "chunk downloads independently, so a failure does not "
                "lose completed work."
            )
            return None

        chunk_options = ["month", "year"]
        default_idx = chunk_options.index(default_chunk_by)
        chunk_by = st.radio(
            "Chunk by",
            chunk_options,
            index=default_idx,
            horizontal=True,
            key=f"{key_prefix}_by",
        )
        max_retries = st.number_input(
            "Max retries per chunk",
            min_value=1,
            max_value=10,
            value=3,
            key=f"{key_prefix}_retries",
        )
        merge_output = True
        if show_merge:
            merge_output = st.checkbox(
                "Merge chunks into single file when done",
                value=True,
                key=f"{key_prefix}_merge",
            )

    return {
        "enabled": True,
        "chunk_by": chunk_by,
        "max_retries": max_retries,
        "merge_output": merge_output,
    }
