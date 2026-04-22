"""Recipe: How colourmap choices shape what you see in climate data.

Uses ARCO-ERA5 (public Google Cloud Zarr, no credentials) to stream
a single global snapshot and render it with different colourmaps,
projections, and normalisation choices.
"""

from __future__ import annotations

import streamlit as st

TITLE = "How do visualisation choices change what you see?"
DESCRIPTION = (
    "Load a global temperature snapshot from ERA5 and see how colourmap, "
    "projection, and colour scaling change the story the map tells."
)
DATASETS_USED = ["ARCO-ERA5"]
CREDENTIALS = "None"
ESTIMATED_TIME = "5-10 seconds"


_CMAPS = {
    "RdBu_r (diverging, good for anomalies)": "RdBu_r",
    "viridis (sequential, perceptually uniform)": "viridis",
    "plasma (sequential, high contrast)": "plasma",
    "coolwarm (diverging, subtle)": "coolwarm",
    "hot (sequential, heat emphasis)": "hot",
    "BrBG (diverging, drought/wet)": "BrBG",
    "RdYlBu_r (diverging, classic climate)": "RdYlBu_r",
    "Greys (sequential, print-friendly)": "Greys",
    "turbo (rainbow, high detail but misleading)": "turbo",
}

_PROJECTIONS = {
    "PlateCarree (flat map)": "PlateCarree",
    "Robinson (compromise, common in atlases)": "Robinson",
    "Mollweide (equal-area, good for global data)": "Mollweide",
    "Orthographic (globe view)": "Orthographic",
}

_VARIABLES = {
    "2m temperature": "2m_temperature",
    "Mean sea level pressure": "mean_sea_level_pressure",
    "Total precipitation": "total_precipitation",
    "10m u-component of wind": "10m_u_component_of_wind",
    "10m v-component of wind": "10m_v_component_of_wind",
}


def _build_map_code(
    variable: str,
    date: str,
    cmap: str,
    projection: str,
    vmin: float | None,
    vmax: float | None,
    kelvin_to_celsius: bool,
) -> str:
    proj_import = f"ccrs.{projection}()" if projection != "Orthographic" else "ccrs.Orthographic(0, 0)"
    lines = [
        "import xarray as xr",
        "import matplotlib.pyplot as plt",
        "import cartopy.crs as ccrs",
        "import cartopy.feature as cfeature",
        "",
        "# Stream a single time step from ARCO-ERA5 (public, no auth)",
        'store = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"',
        "ds = xr.open_zarr(",
        '    store, chunks=None,',
        '    storage_options=dict(token="anon"),',
        ")",
        "",
        f'da = ds["{variable}"].sel(time="{date}", method="nearest")',
    ]
    if kelvin_to_celsius:
        lines.append("da = da - 273.15  # Kelvin to Celsius")
    lines += [
        "",
        f"fig = plt.figure(figsize=(14, 7))",
        f"ax = plt.axes(projection={proj_import})",
        "ax.set_global()",
        "da.plot(",
        "    ax=ax,",
        "    transform=ccrs.PlateCarree(),",
        f'    cmap="{cmap}",',
    ]
    if vmin is not None and vmax is not None:
        lines.append(f"    vmin={vmin:.1f}, vmax={vmax:.1f},")
    lines += [
        ")",
        'ax.coastlines(resolution="110m", linewidth=0.5)',
        "ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='gray')",
        "ax.gridlines(draw_labels=False, linewidth=0.3, alpha=0.5)",
        f'ax.set_title("{variable}")',
        "plt.tight_layout()",
        "plt.show()",
    ]
    return "\n".join(lines)


def _build_download_code(variable: str, date: str) -> str:
    return (
        "import xarray as xr\n"
        "from pathlib import Path\n"
        "\n"
        "# Stream from ARCO-ERA5 (public Google Cloud, no auth needed)\n"
        'store = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"\n'
        "ds = xr.open_zarr(\n"
        '    store, chunks=None,\n'
        '    storage_options=dict(token="anon"),\n'
        ")\n"
        "\n"
        f"# Select variable and time\n"
        f'da = ds["{variable}"].sel(time="{date}", method="nearest")\n'
        "da.load()  # pull the data into memory\n"
        "\n"
        "# Save to NetCDF\n"
        "out = Path('arco_era5_" + variable.replace(" ", "_") + "_" + date[:10] + ".nc')\n"
        "da.to_netcdf(out)\n"
        "print(f'Saved {out} ({out.stat().st_size / 1e6:.1f} MB)')\n"
    )


def _load_snapshot(variable: str, date: str):
    """Stream a single global snapshot from ARCO-ERA5.

    Uses session_state to avoid re-streaming when only display widgets
    (colourmap, projection, colour range) change. Only re-streams when
    variable or date changes.
    """
    cache_key = f"{variable}_{date}"
    if (
        st.session_state.get("_spatial_cache_key") == cache_key
        and st.session_state.get("_spatial_cache_da") is not None
    ):
        return st.session_state["_spatial_cache_da"]

    import xarray as xr

    store = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
    ds = xr.open_zarr(
        store, chunks=None,
        storage_options=dict(token="anon"),
    )
    da = ds[variable].sel(time=date, method="nearest")
    da.load()

    st.session_state["_spatial_cache_key"] = cache_key
    st.session_state["_spatial_cache_da"] = da
    return da


def render_recipe() -> None:
    """Render the spatial maps / colourmap recipe."""
    st.header("How do visualisation choices change what you see?")
    st.markdown(
        "The same data can tell different stories depending on how you "
        "plot it. Colourmap choice, colour scaling, and map projection "
        "all affect what patterns jump out and what gets hidden. This "
        "recipe streams a global snapshot from ERA5 and lets you "
        "experiment with these choices side by side."
    )
    st.markdown(
        "This is not just an aesthetic question. A badly chosen colourmap "
        "can hide real patterns, create false boundaries, or mislead "
        "readers. Understanding these choices is a core data literacy skill."
    )

    st.caption(
        ":material/cloud: Streamed from ARCO-ERA5 on Google Cloud Storage. "
        "No API key, no download queue. Public access."
    )

    # Widgets
    col1, col2 = st.columns(2)
    with col1:
        var_label = st.selectbox(
            "Variable",
            list(_VARIABLES.keys()),
            key="spatial_var",
        )
        variable = _VARIABLES[var_label]

    with col2:
        date = st.text_input(
            "Date and hour (UTC)",
            value="2023-07-15T12:00",
            key="spatial_date",
            help="Format: YYYY-MM-DDTHH:MM. ARCO-ERA5 has hourly data from 1979.",
        )

    col3, col4 = st.columns(2)
    with col3:
        cmap_label = st.selectbox(
            "Colourmap",
            list(_CMAPS.keys()),
            key="spatial_cmap",
        )
        cmap = _CMAPS[cmap_label]

    with col4:
        proj_label = st.selectbox(
            "Map projection",
            list(_PROJECTIONS.keys()),
            key="spatial_proj",
        )
        projection = _PROJECTIONS[proj_label]

    use_custom_range = st.toggle(
        "Set custom colour range",
        key="spatial_custom_range",
        help="Override the automatic min/max to highlight a specific range.",
    )
    vmin, vmax = None, None
    if use_custom_range:
        cr1, cr2 = st.columns(2)
        with cr1:
            vmin = st.number_input("Colour min", value=-40.0, key="spatial_vmin")
        with cr2:
            vmax = st.number_input("Colour max", value=40.0, key="spatial_vmax")

    st.caption(
        ":material/info: Changing the colourmap, projection, or colour range "
        "updates the plots instantly. Changing the **variable** or **date** "
        "will re-stream the data, which takes 5-10 seconds."
    )

    # Load data (cached in session_state, only re-streams on variable/date change)
    try:
        da = _load_snapshot(variable, date)
    except Exception as exc:
        st.error(f"Failed to stream data: {type(exc).__name__}: {exc}")
        st.caption("Check that the date is within ARCO-ERA5's range (1979-present).")
        return

    # Convert Kelvin to Celsius for temperature
    kelvin_to_celsius = False
    if "temperature" in variable and float(da.mean()) > 100:
        da = da - 273.15
        kelvin_to_celsius = True
        unit = "deg C"
    elif "pressure" in variable:
        da = da / 100  # Pa to hPa
        unit = "hPa"
    elif "precipitation" in variable:
        da = da * 1000  # m to mm
        unit = "mm"
    else:
        unit = da.attrs.get("units", "")

    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.pyplot as plt

    # Main map
    st.subheader("Global map")
    actual_time = str(da.time.values)[:16]
    st.markdown(
        f"**{var_label}** at {actual_time} UTC, shown with `{cmap}` "
        f"colourmap on a {proj_label.split('(')[0].strip()} projection."
    )

    proj_map = {
        "PlateCarree": ccrs.PlateCarree(),
        "Robinson": ccrs.Robinson(),
        "Mollweide": ccrs.Mollweide(),
        "Orthographic": ccrs.Orthographic(0, 0),
    }

    fig, ax = plt.subplots(
        figsize=(14, 7),
        subplot_kw={"projection": proj_map[projection]},
    )
    ax.set_global()
    plot_kwargs = dict(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        cbar_kwargs={"label": f"{var_label} ({unit})", "shrink": 0.6},
    )
    if vmin is not None and vmax is not None:
        plot_kwargs["vmin"] = vmin
        plot_kwargs["vmax"] = vmax
    da.plot(**plot_kwargs)
    ax.coastlines(resolution="110m", linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="gray")
    ax.gridlines(draw_labels=False, linewidth=0.3, alpha=0.5)
    ax.set_title(f"{var_label} - {actual_time} UTC")
    fig.tight_layout()
    st.pyplot(fig)

    with st.expander(":material/code: Code for this map"):
        st.code(
            _build_map_code(variable, date, cmap, projection, vmin, vmax, kelvin_to_celsius),
            language="python",
        )

    # Side-by-side comparison
    st.markdown("---")
    st.subheader("Colourmap comparison")
    st.caption(
        ":material/info: The panels below use the streamed data and will "
        "re-render when you change any widget. Changing colourmap, projection, "
        "or colour range is instant. Changing variable or date re-streams "
        "the data (5-10 seconds)."
    )
    st.markdown(
        "The same data rendered with four different colourmaps. Notice how "
        "some make gradients obvious while others obscure them. Diverging "
        "colourmaps (like RdBu_r) emphasise a midpoint; sequential "
        "colourmaps (like viridis) show magnitude."
    )

    import numpy as np

    compare_cmaps = ["RdBu_r", "viridis", "turbo", "Greys"]
    cmap_plot_kwargs = {}
    if vmin is not None and vmax is not None:
        cmap_plot_kwargs["vmin"] = vmin
        cmap_plot_kwargs["vmax"] = vmax

    fig2, axes2 = plt.subplots(
        2, 2, figsize=(14, 8),
        subplot_kw={"projection": ccrs.PlateCarree()},
    )
    for i, (ax_i, cm) in enumerate(zip(axes2.flat, compare_cmaps)):
        ax_i.remove()
        ax_new = fig2.add_subplot(2, 2, i + 1, projection=proj_map[projection])
        da.plot(
            ax=ax_new, transform=ccrs.PlateCarree(), cmap=cm,
            add_colorbar=True,
            cbar_kwargs={"shrink": 0.5, "label": unit},
            **cmap_plot_kwargs,
        )
        ax_new.coastlines(resolution="110m", linewidth=0.4)
        ax_new.set_global()
        ax_new.set_title(cm, fontsize=11)
    fig2.suptitle(f"{var_label} - same data, four colourmaps", fontsize=13)
    fig2.tight_layout()
    st.pyplot(fig2)

    st.markdown(
        "**Key takeaways:**\n"
        "- `RdBu_r` centres on a midpoint (often zero) and shows warm/cool "
        "as red/blue. Best for anomalies and differences.\n"
        "- `viridis` is perceptually uniform and designed for consistent "
        "brightness progression, but uses a blue-yellow range that can be "
        "difficult for some forms of colour vision deficiency (tritanopia). "
        "It is not universally colour-blind safe.\n"
        "- `turbo` (rainbow) shows fine detail but creates artificial "
        "boundaries where the colour wraps. The human eye reads sharp "
        "colour transitions as data boundaries that do not exist. Avoid "
        "for publication.\n"
        "- `Greys` works for print and removes colour as a variable. "
        "Useful for checking if your pattern depends on colour choice.\n\n"
        "No single colourmap is perfect for all audiences and all data. "
        "Test your plots in greyscale and with a colour-blindness "
        "simulator before publishing."
    )

    # Projection comparison
    st.subheader("Projection comparison")
    st.markdown(
        "Every flat map distorts the globe. The choice of projection "
        "affects what looks big, what looks small, and where features "
        "appear. No projection is 'correct' - each is a compromise. "
        "All four panels use your selected colourmap and colour range."
    )

    proj_list = [
        ("PlateCarree", ccrs.PlateCarree()),
        ("Robinson", ccrs.Robinson()),
        ("Mollweide", ccrs.Mollweide()),
        ("Orthographic", ccrs.Orthographic(0, 0)),
    ]
    fig3, axes3 = plt.subplots(
        2, 2, figsize=(14, 8),
        subplot_kw={"projection": ccrs.PlateCarree()},
    )
    for i, (ax_i, (name, proj)) in enumerate(zip(axes3.flat, proj_list)):
        ax_i.remove()
        ax_new = fig3.add_subplot(2, 2, i + 1, projection=proj)
        da.plot(
            ax=ax_new, transform=ccrs.PlateCarree(), cmap=cmap,
            add_colorbar=False,
            **cmap_plot_kwargs,
        )
        ax_new.coastlines(resolution="110m", linewidth=0.4)
        ax_new.set_global()
        ax_new.set_title(name, fontsize=11)
    fig3.suptitle(f"{var_label} - same data, four projections", fontsize=13)
    fig3.tight_layout()
    st.pyplot(fig3)

    st.markdown(
        "**Key takeaways:**\n"
        "- PlateCarree stretches the poles (Greenland looks enormous).\n"
        "- Robinson is a good compromise for general-purpose maps.\n"
        "- Mollweide preserves area (each grid cell is the right size "
        "relative to others). Best for global averages.\n"
        "- Orthographic shows the globe as seen from space. Intuitive "
        "but hides half the planet."
    )

    # At a glance
    st.subheader("At a glance")
    import numpy as np
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Variable", var_label, border=True)
    col_b.metric("Time step", actual_time[:10], border=True)
    col_c.metric(
        "Global mean",
        f"{float(da.mean()):.1f} {unit}",
        border=True,
    )
    col_d.metric(
        "Range",
        f"{float(da.min()):.1f} to {float(da.max()):.1f} {unit}",
        border=True,
    )

    # Get this data yourself
    st.markdown("---")
    st.subheader("Get this data yourself")
    st.markdown(
        "ARCO-ERA5 is hosted on Google Cloud Storage as a public Zarr "
        "store. No API key, no download queue. You stream the bytes you "
        "need directly into xarray."
    )

    with st.expander(":material/download: Download code", expanded=False):
        st.code(_build_download_code(variable, date), language="python")

    with st.expander(":material/folder_open: Open and inspect", expanded=False):
        st.code(
            "import xarray as xr\n"
            "\n"
            "# Open the Zarr store (lazy, no data downloaded yet)\n"
            'store = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"\n'
            "ds = xr.open_zarr(\n"
            '    store, chunks=None,\n'
            '    storage_options=dict(token="anon"),\n'
            ")\n"
            "\n"
            "print(ds)\n"
            "print(f'\\nVariables: {list(ds.data_vars)}')\n"
            "print(f'Time range: {ds.time.values[0]} to {ds.time.values[-1]}')\n"
            "print(f'Resolution: {float(ds.latitude[1] - ds.latitude[0]):.2f} degrees')\n",
            language="python",
        )

    st.caption(
        "Requires `xarray`, `zarr`, and `gcsfs`. "
        "No authentication. Works in Colab, Jupyter, or any Python 3.10+ environment."
    )

    # Next steps
    st.markdown("---")
    st.subheader("Next steps")
    st.markdown(
        "- See the full ARCO-ERA5 documentation in `docs/arco-era5/README.md`\n"
        "- Try different dates to see how weather patterns change\n"
        "- Compare summer vs winter to see the seasonal cycle spatially\n"
        "- Use the Download tab to stream ARCO-ERA5 data for your own analysis\n"
        "- Read [Ed Hawkins on colourmap choice](https://www.climate-lab-book.ac.uk/) "
        "for more on why this matters"
    )
