"""Explore data page: load an existing file and explore interactively.

No download needed - just point at a file you already have on disk.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr


def render_page() -> None:
    """Render the explore-data page."""
    st.markdown(
        "Load a file you already have on disk and explore it interactively. "
        "No re-downloading needed."
    )

    file_path = st.text_input(
        "File path",
        placeholder=r"e.g. ./data/era5-single-levels/era5_single_levels_download.nc",
        key="explore_file_path",
    )

    if not file_path:
        st.caption("Paste or type the path to a NetCDF, GRIB, or CSV file.")
        _show_recent_files()
        return

    path = Path(file_path)
    if not path.exists():
        st.error(f"File not found: `{path}`")
        return

    st.success(f"`{path.name}` ({path.stat().st_size / 1e6:.2f} MB)")

    suffix = path.suffix.lower()
    if suffix in (".csv", ".txt", ".dat"):
        _explore_tabular(path)
    else:
        _explore_gridded(path)


def _load_file(path: str) -> None:
    """Callback: set the file path input to the given path."""
    st.session_state["explore_file_path"] = path


def _show_recent_files() -> None:
    """Scan ./data/ for existing downloads and list them."""
    data_dir = Path("./data")
    if not data_dir.exists():
        return

    files = sorted(data_dir.rglob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    files = [f for f in files if f.is_file() and not f.name.startswith(".")][:10]

    if not files:
        return

    st.subheader("Recent downloads")
    for f in files:
        size_mb = f.stat().st_size / 1e6
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{f.name}**")
            st.caption(f"{f.parent} - {size_mb:.2f} MB")
        with col_btn:
            st.button(
                ":material/folder_open: Load",
                key=f"recent_{f}",
                use_container_width=True,
                on_click=_load_file,
                args=(str(f),),
            )


def _explore_tabular(path: Path) -> None:
    """Full explore experience for CSV/tabular files."""
    import pandas as pd

    try:
        df = pd.read_csv(path)
    except Exception:
        # Might be binary despite extension
        _explore_gridded(path)
        return

    # Data quality section
    st.subheader("Data quality")
    _tabular_quality(df, path)

    # Preview
    st.subheader("Preview")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
    st.caption(f"{len(df):,} rows, {len(df.columns)} columns")

    # Interactive plots
    st.subheader("Explore")
    from app.forms import _render_tabular_plot
    _render_tabular_plot(df, path)


def _tabular_quality(df: pd.DataFrame, path: Path) -> None:
    """Data completeness and quality summary for a DataFrame."""
    import pandas as pd

    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()
    completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 0

    with st.container(horizontal=True):
        st.metric("Rows", f"{len(df):,}", border=True)
        st.metric("Columns", str(len(df.columns)), border=True)
        st.metric("Completeness", f"{completeness:.1f}%", border=True)

    # Per-column missing data
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        with st.expander(f"Missing values ({len(missing)} columns with gaps)"):
            missing_pct = (missing / len(df) * 100).round(1)
            summary = pd.DataFrame({
                "Missing count": missing,
                "Missing %": missing_pct,
            })
            st.dataframe(summary, use_container_width=True)
    else:
        st.caption("No missing values - dataset is fully complete.")

    # Basic stats
    with st.expander("Descriptive statistics"):
        st.dataframe(df.describe(), use_container_width=True)

    # Code for quality checks
    with st.expander(":material/code: Code for data quality checks"):
        st.code(
            "import pandas as pd\n\n"
            f'df = pd.read_csv("{path}")\n\n'
            "# Completeness\n"
            "print(f\"Shape: {df.shape}\")\n"
            "print(f\"Missing values:\\n{df.isna().sum()}\")\n"
            "print(f\"Completeness: {(1 - df.isna().sum().sum() / df.size) * 100:.1f}%\")\n\n"
            "# Summary statistics\n"
            "print(df.describe())",
            language="python",
        )


def _explore_gridded(path: Path) -> None:
    """Full explore experience for NetCDF/GRIB files."""
    try:
        from app.forms import _open_dataset
        ds = _open_dataset(path)
    except Exception as exc:
        st.error(f"Could not open file: {exc}")
        return

    # Data quality section
    st.subheader("Data quality")
    _gridded_quality(ds, path)

    # Summary
    st.subheader("Structure")
    with st.expander("Full xarray repr", expanded=True):
        st.text(repr(ds))

    # Interactive plots
    st.subheader("Explore")
    from app.forms import _interactive_plot
    _interactive_plot(ds, path)

    ds.close()


def _gridded_quality(ds: xr.Dataset, path: Path) -> None:
    """Data completeness and quality summary for an xarray Dataset."""
    import numpy as np

    data_vars = list(ds.data_vars)

    # Identify dims
    lat_dim = next((d for d in ds.dims if d in ("latitude", "lat")), None)
    lon_dim = next((d for d in ds.dims if d in ("longitude", "lon")), None)
    time_dim = next((d for d in ds.dims if d in ("time", "valid_time")), None)

    # Summary metrics
    metrics = {}
    if time_dim:
        time_vals = ds.coords[time_dim].values
        metrics["Time range"] = f"{str(time_vals[0])[:10]} to {str(time_vals[-1])[:10]}"
        metrics["Time steps"] = str(len(time_vals))
    if lat_dim and lon_dim:
        metrics["Spatial extent"] = (
            f"{float(ds[lat_dim].min()):.1f} to {float(ds[lat_dim].max()):.1f} lat, "
            f"{float(ds[lon_dim].min()):.1f} to {float(ds[lon_dim].max()):.1f} lon"
        )
        metrics["Grid points"] = f"{ds.sizes[lat_dim]} x {ds.sizes[lon_dim]}"

    with st.container(horizontal=True):
        st.metric("Variables", str(len(data_vars)), border=True)
        if "Time steps" in metrics:
            st.metric("Time steps", metrics["Time steps"], border=True)
        if "Grid points" in metrics:
            st.metric("Grid points", metrics["Grid points"], border=True)

    if "Time range" in metrics:
        st.caption(f"Time range: {metrics['Time range']}")
    if "Spatial extent" in metrics:
        st.caption(f"Spatial extent: {metrics['Spatial extent']}")

    # NaN check on first variable (sampled for large datasets)
    if data_vars:
        var = data_vars[0]
        da = ds[var]
        total = int(np.prod(da.shape))
        nbytes_est = total * 4  # float32 estimate
        max_bytes = 500 * 1024 * 1024  # 500 MB threshold

        sampled = False
        if nbytes_est > max_bytes and time_dim and time_dim in da.dims:
            sample_steps = max(1, int(max_bytes / (nbytes_est / da.sizes[time_dim])))
            da_sample = da.isel({time_dim: slice(0, sample_steps)})
            sample_total = int(np.prod(da_sample.shape))
            values = da_sample.values
            nan_count = int(np.isnan(values).sum())
            completeness = (1 - nan_count / sample_total) * 100
            sampled = True
            st.caption(
                f"Completeness of `{var}` (sampled, first {sample_steps} "
                f"of {da.sizes[time_dim]:,} time steps): {completeness:.1f}% "
                f"({nan_count:,} NaN out of {sample_total:,} values)"
            )
            st.info(
                f"Full dataset is ~{nbytes_est / 1e9:.1f} GB in memory. "
                f"Showing a preview of the first {sample_steps} time steps. "
                f"See the code snippet below for how to check the full file."
            )
        else:
            values = da.values
            nan_count = int(np.isnan(values).sum())
            completeness = (1 - nan_count / total) * 100
            st.caption(
                f"Completeness of `{var}`: {completeness:.1f}% "
                f"({nan_count:,} NaN out of {total:,} values)"
            )

    # Code
    var_name = data_vars[0] if data_vars else "var"
    with st.expander(":material/code: Code for data quality checks"):
        code_lines = [
            "import xarray as xr",
            "import numpy as np",
            "",
            f'ds = xr.open_dataset("{path}")',
            "",
            "# Overview",
            "print(ds)",
            "",
            "# Check for missing data",
            f'da = ds["{var_name}"]',
        ]
        if data_vars and nbytes_est > max_bytes:
            code_lines += [
                "",
                "# Large file - iterate over time slices to avoid memory errors",
                "nan_count = 0",
                "total = 0",
                f"n_steps = da.sizes['{time_dim}']",
                "batch = 100",
                "for start in range(0, n_steps, batch):",
                f"    chunk = da.isel({time_dim}=slice(start, start + batch)).values",
                "    nan_count += int(np.isnan(chunk).sum())",
                "    total += chunk.size",
                "    print(f\"  {min(start + batch, n_steps)}/{n_steps}\", end=\"\\r\")",
                'print(f"\\nCompleteness: {(1 - nan_count/total)*100:.1f}%")',
                'print(f"NaN count: {nan_count:,} / {total:,}")',
            ]
        else:
            code_lines += [
                "total = np.prod(da.shape)",
                "nans = np.isnan(da.values).sum()",
                'print(f"Completeness: {(1 - nans/total)*100:.1f}%")',
                'print(f"NaN count: {nans:,} / {total:,}")',
            ]
        st.code("\n".join(code_lines), language="python")
