"""Streamlit entry point for the climate data quickstart app.

Launch via ``run_app.bat`` / ``run_app.sh`` or manually with::

    streamlit run app/main.py

The app binds to ``localhost`` only. It never reads or stores credential
strings; it invokes the same ``scripts/*_download.download()`` functions
as the command-line route, which in turn call ``cdsapi.Client()`` and
``requests`` with the user's standard config files.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Ensure the repo root is on sys.path so ``scripts.*`` and ``common.*``
# imports resolve when streamlit launches this file directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st  # noqa: E402

from app import credentials  # noqa: E402
from app.dataset_pages import (  # noqa: E402
    CATEGORIES,
    DATASET_INFO,
    DATASETS,
)
from app.dataset_pages import explore as explore_page  # noqa: E402
from app.forms import result_panel, streaming_preview_panel  # noqa: E402
from app.runner import run  # noqa: E402


# Download-only datasets (exclude navigation pages)
_DOWNLOAD_DATASETS = {k: v for k, v in DATASETS.items() if k != "home"}


# ── Sidebar ────────────────────────────────────────────────────────

def _set_mode(mode: str) -> None:
    """Callback for navigation buttons."""
    st.session_state["app_mode"] = mode


def _render_sidebar() -> tuple[str, str | None]:
    """Render the sidebar and return (mode, dataset_slug)."""
    st.sidebar.markdown("## :material/cloud_download: Climate data quickstart")
    st.sidebar.caption(
        "Download, stream, and explore climate datasets. "
        "Your API keys never leave this machine."
    )

    if "app_mode" not in st.session_state:
        st.session_state["app_mode"] = "Home"

    current = st.session_state["app_mode"]

    nav_items = [
        (":material/home: Home", "Home"),
        (":material/search: Explore data", "Explore"),
        (":material/download: Download", "Download"),
    ]
    for label, mode in nav_items:
        st.sidebar.button(
            label,
            key=f"nav_{mode}",
            use_container_width=True,
            type="primary" if current == mode else "tertiary",
            on_click=_set_mode,
            args=(mode,),
        )

    slug = None
    if current == "Download":
        slug = _render_dataset_picker()
        _render_credential_panel()

    return current, slug


def _render_dataset_picker() -> str:
    """Two-step dataset picker: category pills, then radio within category."""
    cat_labels = list(CATEGORIES.keys())

    if "dataset_category" not in st.session_state:
        st.session_state["dataset_category"] = cat_labels[0]

    category = st.sidebar.pills(
        "Category",
        cat_labels,
        key="dataset_category",
        label_visibility="collapsed",
    )

    icon, slugs = CATEGORIES[category or cat_labels[0]]

    # Build radio options: human-readable names
    options = {s: _DOWNLOAD_DATASETS[s][0] for s in slugs}

    selected_slug = st.sidebar.radio(
        f"{icon} {category}",
        list(options.keys()),
        format_func=lambda s: options[s],
        key="dataset_radio",
        label_visibility="visible",
    )

    return selected_slug


def _render_credential_panel() -> None:
    statuses = credentials.all_statuses()
    labels = {
        "cds": "CDS API",
        "edh": "Earth Data Hub",
        "earthdata": "NASA Earthdata",
        "ceda": "CEDA",
        "ewds": "EWDS (GloFAS)",
    }
    st.sidebar.caption(":material/key: **Credentials**")
    for key, label in labels.items():
        status = statuses[key]
        if status.configured:
            st.sidebar.badge(
                f"{label}: ready",
                icon=":material/check_circle:",
                color="green",
            )
        else:
            with st.sidebar.expander(
                label,
                expanded=False,
                icon=":material/error:",
            ):
                st.markdown(f"**Location:** {status.location}")
                st.markdown(
                    f"**Register:** [{status.registration_url}]"
                    f"({status.registration_url})"
                )
                st.code(status.instructions, language="text")


# ── Main page ──────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="Climate data quickstart",
        page_icon=":material/cloud_download:",
        layout="wide",
    )

    mode, slug = _render_sidebar()

    if mode == "Home":
        home_module = DATASETS["home"][1]
        home_module.render_page()
        return

    if mode == "Explore":
        st.title(":material/search: Explore data")
        explore_page.render_page()
        return

    # ── Download mode ───────────────────────────────────────────────
    name, module = _DOWNLOAD_DATASETS[slug]

    # Clear stale results when the user switches dataset.
    if st.session_state.get("last_result_slug") != slug:
        st.session_state.pop("last_result_path", None)
        st.session_state.pop("stream_preview_ds", None)
        st.session_state.pop("stream_preview_config", None)
        st.session_state.pop("stream_preview_slug", None)
        st.session_state.pop("esgf_multi_ts_ds", None)
        st.session_state.pop("esgf_multi_paths", None)
        st.session_state.pop("esgf_multi_config", None)
        st.session_state["last_result_slug"] = slug

    st.title(name)
    info = DATASET_INFO.get(slug)
    if info:
        st.caption(info)

    ready, missing = credentials.dataset_ready(slug)
    if missing:
        st.warning(
            "This dataset needs credentials that are not configured yet. "
            "Check the sidebar to see what to set up."
        )
        for m in missing:
            st.caption(f"- Missing: `{m.location}` (register at {m.registration_url})")

    # ESGF mode selector must be outside the form so switching mode
    # triggers an immediate rerun rather than waiting for form submit.
    if hasattr(module, "render_mode_selector"):
        module.render_mode_selector()

    # Render the dataset-specific form.
    with st.form(key=f"form_{slug}"):
        config = module.render_form()

        if slug in ("earth-data-hub", "arco-era5", "edh-explorer"):
            c1, c2, c3 = st.columns(3)
            show_code = c1.form_submit_button(
                ":material/code: Show code",
                use_container_width=True,
                disabled=not ready,
            )
            stream_preview = c2.form_submit_button(
                ":material/visibility: Stream & preview",
                use_container_width=True,
                disabled=not ready,
            )
            download = c3.form_submit_button(
                ":material/download: Download",
                use_container_width=True,
                disabled=not ready,
            )
            submitted = download
        else:
            submitted = st.form_submit_button(
                ":material/download: Download",
                disabled=not ready,
                use_container_width=True,
            )
            show_code = False
            stream_preview = False

    # Streaming code display
    _is_streaming = slug in ("earth-data-hub", "arco-era5", "edh-explorer")
    if _is_streaming and (show_code or stream_preview or submitted):
        st.subheader("Streaming code snippet")
        st.caption(
            "Copy this into a notebook or script to work with the data lazily. "
            "Only the bytes you actually reduce or save flow over the network."
        )
        st.code(module.streaming_snippet(config), language="python")

    # Stream & preview: open remote store, load subset, render explorer
    if _is_streaming and stream_preview:
        _stream_preview(slug, config)

    if submitted:
        if slug == "esgf-cmip6" and config.get("mode") == "multi":
            _run_esgf_multi(config)
        else:
            _run_download(slug, config)

    # Persist streamed preview across reruns
    if (
        st.session_state.get("stream_preview_ds") is not None
        and st.session_state.get("stream_preview_slug") == slug
    ):
        open_code = _streaming_open_code(slug, st.session_state["stream_preview_config"])
        streaming_preview_panel(st.session_state["stream_preview_ds"], open_code)

    # Persist ESGF multi-model results
    if st.session_state.get("esgf_multi_ts_ds") is not None:
        _esgf_multi_panel(
            st.session_state["esgf_multi_ts_ds"],
            st.session_state["esgf_multi_paths"],
            st.session_state["esgf_multi_config"],
        )

    # Persist the downloaded result panel across reruns
    if st.session_state.get("last_result_path"):
        result_path = Path(st.session_state["last_result_path"])
        if result_path.exists():
            result_panel(result_path)


# ── Streaming helpers ──────────────────────────────────────────────

def _streaming_open_code(slug: str, config: dict) -> str:
    """Return the xr.open code for streaming snippet generators."""
    if slug == "arco-era5":
        return (
            "ds = xr.open_zarr(\n"
            f'    "{config["store_url"]}",\n'
            "    chunks=None,\n"
            '    storage_options=dict(token="anon"),\n'
            ")\n"
            'ds = ds.sel(time=slice(ds.attrs["valid_time_start"], ds.attrs["valid_time_stop"]))'
        )
    return (
        "ds = xr.open_dataset(\n"
        f'    "{config["edh_dataset_url"]}",\n'
        '    engine="zarr",\n'
        "    chunks={},\n"
        '    storage_options={"client_kwargs": {"trust_env": True}},\n'
        ")\n"
        'if float(ds["longitude"].max()) > 180:\n'
        '    ds = ds.assign_coords(longitude=(((ds["longitude"] + 180) % 360) - 180))\n'
        'ds = ds.sortby("latitude").sortby("longitude")'
    )


def _stream_preview(slug: str, config: dict) -> None:
    """Open a remote Zarr store, load a subset, and store it for the explorer."""
    import xarray as xr

    status = st.empty()
    status.info(
        "Opening remote store and streaming subset. "
        "Time depends on the slice size, not a queue."
    )

    try:
        if slug == "arco-era5":
            ds = xr.open_zarr(
                config["store_url"],
                chunks=None,
                storage_options=dict(token="anon"),
            )
            ds = ds.sel(time=slice(
                ds.attrs.get("valid_time_start"),
                ds.attrs.get("valid_time_stop"),
            ))
            subset = ds[config["variable"]].sel(
                time=slice(config["time_start"], config["time_end"]),
                latitude=slice(config["lat_north"], config["lat_south"]),
                longitude=slice(config["lon_west"], config["lon_east"]),
            )
        else:
            ds = xr.open_dataset(
                config["edh_dataset_url"],
                engine="zarr",
                chunks={},
                storage_options={"client_kwargs": {"trust_env": True}},
            )
            if float(ds["longitude"].max()) > 180:
                ds = ds.assign_coords(
                    longitude=(((ds["longitude"] + 180) % 360) - 180)
                )
            ds = ds.sortby("latitude").sortby("longitude")

            dim_names = tuple(ds.sizes)
            if "valid_time" in dim_names:
                time_dim = "valid_time"
            elif "time" in dim_names:
                time_dim = "time"
            else:
                raise RuntimeError(
                    f"No time dimension found. Available: {dim_names}"
                )
            lat_dim = "latitude" if "latitude" in dim_names else "lat"
            lon_dim = "longitude" if "longitude" in dim_names else "lon"

            subset = ds[config["variable"]].sel({
                time_dim: slice(config["time_start"], config["time_end"]),
                lat_dim: slice(config["lat_south"], config["lat_north"]),
                lon_dim: slice(config["lon_west"], config["lon_east"]),
            })

        subset.load()
        preview_ds = subset.to_dataset(name=config["variable"])

    except Exception as exc:
        status.empty()
        st.error(f"Streaming failed: {type(exc).__name__}: {exc}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc(), language="python")
        return

    status.empty()
    st.success(
        f"Streamed `{config['variable']}`: shape {subset.shape} "
        f"({subset.nbytes / 1e6:.2f} MB in memory)"
    )

    st.session_state["stream_preview_ds"] = preview_ds
    st.session_state["stream_preview_config"] = config
    st.session_state["stream_preview_slug"] = slug


# ── Download helpers ───────────────────────────────────────────────

def _run_download(slug: str, config: dict) -> None:
    """Invoke the download, store result path in session state."""
    status = st.empty()
    if slug == "earth-data-hub":
        status.info(
            "Streaming sliced bytes from Earth Data Hub. Time scales with "
            "how much data you asked for, not with a queue."
        )
    elif slug == "arco-era5":
        status.info(
            "Streaming sliced bytes from ARCO-ERA5 on Google Cloud Storage. "
            "Time scales with the size of the slice, not with a queue."
        )
    else:
        status.info(
            "Submitting request. CDS requests are queued server-side; direct "
            "downloads are usually immediate."
        )

    try:
        output_path = run(slug, config)
    except Exception as exc:
        status.empty()
        st.error(f"Download failed: {type(exc).__name__}: {exc}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc(), language="python")
        st.session_state.pop("last_result_path", None)
        return

    status.empty()
    st.session_state["last_result_path"] = str(output_path)


# ── ESGF multi-model ──────────────────────────────────────────────

def _run_esgf_multi(config: dict) -> None:
    """Download multiple CMIP6 models, build combined dataset, store in state."""
    from scripts.esgf_cmip6_download import download_multi

    status = st.empty()
    source_ids = config["source_ids"]
    n_members = config.get("n_members", 1)
    total = len(source_ids) * n_members
    status.info(
        f"Downloading {total} file(s) from ESGF "
        f"({len(source_ids)} model(s), {n_members} member(s) each). "
        f"Each file is typically 5-15 MB."
    )

    try:
        multi_config = {k: v for k, v in config.items() if k != "mode"}
        paths = download_multi(**multi_config)
    except Exception as exc:
        status.empty()
        st.error(f"Multi-model download failed: {type(exc).__name__}: {exc}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc(), language="python")
        return

    if not paths:
        status.empty()
        st.error("No files were downloaded. Check that the selected models "
                 "have data for this experiment/variable/frequency combination.")
        return

    status.info(f"Downloaded {len(paths)} file(s). Building combined dataset...")

    try:
        ts_ds = _build_multi_model_ts(paths, config["variable_id"])
    except Exception as exc:
        status.empty()
        st.error(f"Post-processing failed: {type(exc).__name__}: {exc}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc(), language="python")
        return

    status.empty()
    st.success(
        f"Downloaded {len(paths)} file(s). "
        f"Combined time series: {dict(ts_ds.sizes)}"
    )

    st.session_state["esgf_multi_ts_ds"] = ts_ds
    st.session_state["esgf_multi_paths"] = [str(p) for p in paths]
    st.session_state["esgf_multi_config"] = config


def _build_multi_model_ts(paths: list[Path], variable_id: str):
    """Open multiple CMIP6 files and build a (time, model) area-mean dataset.

    Each model file may use a different grid and calendar. We compute the
    area-weighted global mean for each, convert cftime to pandas timestamps,
    and concatenate along a "model" dimension.
    """
    import numpy as np
    import pandas as pd
    import xarray as xr

    series = []
    labels = []

    model_names = set()
    for path in paths:
        parts = path.stem.split("_")
        model_names.add(parts[2] if len(parts) > 2 else "unknown")
    single_model = len(model_names) == 1

    for path in paths:
        ds = xr.open_dataset(path)
        da = ds[variable_id]

        # CMIP6 DRS filename: var_table_model_exp_member_grid_dates.nc
        parts = path.stem.split("_")
        model_name = parts[2] if len(parts) > 2 else "unknown"
        member_id = parts[4] if len(parts) > 4 else ""
        if single_model:
            label = member_id or model_name
        else:
            label = f"{model_name} {member_id}" if member_id else model_name

        weights = np.cos(np.deg2rad(da.lat))
        ts = da.weighted(weights).mean(["lat", "lon"])

        # Convert cftime to pandas timestamps for cross-model alignment
        time_vals = ts.time.values
        if hasattr(time_vals[0], "year"):
            time_pd = pd.DatetimeIndex([
                pd.Timestamp(t.year, t.month, getattr(t, "day", 1))
                for t in time_vals
            ])
            ts = ts.assign_coords(time=time_pd)

        series.append(ts)
        labels.append(label)
        ds.close()

    # Align to the overlapping time range
    common_start = max(s.time.values[0] for s in series)
    common_end = min(s.time.values[-1] for s in series)
    aligned = [s.sel(time=slice(common_start, common_end)) for s in series]

    # Ensure all have the same number of time steps (take the minimum)
    min_len = min(len(a.time) for a in aligned)
    trimmed = [a.isel(time=slice(0, min_len)) for a in aligned]

    # Use the first series' time coordinates as the common axis
    for i in range(1, len(trimmed)):
        trimmed[i] = trimmed[i].assign_coords(time=trimmed[0].time.values)

    dim_name = "member" if single_model else "model"
    combined = xr.concat(trimmed, dim=pd.Index(labels, name=dim_name))
    return combined.to_dataset(name=variable_id)


def _esgf_multi_panel(
    ts_ds,
    paths: list[str],
    config: dict,
) -> None:
    """Render the multi-model or ensemble comparison with views and maps."""
    import xarray as xr

    variable_id = config["variable_id"]
    is_ensemble = "member" in ts_ds.dims
    ens_dim = "member" if is_ensemble else "model"
    n_items = ts_ds.sizes.get(ens_dim, 0)

    if is_ensemble:
        ts_label = ":material/timeline: Ensemble time series"
        map_label = ":material/map: Per-member maps"
    else:
        ts_label = ":material/timeline: Multi-model time series"
        map_label = ":material/map: Spatial maps"

    tab_ts, tab_map = st.tabs([ts_label, map_label])

    with tab_ts:
        if is_ensemble:
            model_name = config.get("source_ids", [""])[0]
            st.caption(
                f"{n_items} ensemble members of {model_name}, "
                f"{ts_ds.sizes.get('time', 0)} time steps. "
                f"Area-weighted global mean of {variable_id}."
            )
        else:
            st.caption(
                f"{n_items} model/member combinations, "
                f"{ts_ds.sizes.get('time', 0)} time steps. "
                f"Area-weighted global mean of {variable_id}."
            )
        with st.expander("Dataset summary", expanded=False):
            st.text(repr(ts_ds))

        try:
            import nc_time_axis  # noqa: F401
        except ImportError:
            pass

        from app.forms import _interactive_plot
        _interactive_plot(ts_ds, open_code=_esgf_multi_open_snippet(config))

    with tab_map:
        if not paths:
            st.info("No files available for maps.")
            return

        # Let user pick which model file to display
        path_labels = []
        for p in paths:
            parts = Path(p).stem.split("_")
            model = parts[2] if len(parts) > 2 else "unknown"
            member = parts[4] if len(parts) > 4 else ""
            path_labels.append(f"{model} {member}".strip())

        selected_label = st.selectbox(
            "Model to map",
            path_labels,
            key="esgf_multi_map_model",
        )
        selected_path = Path(paths[path_labels.index(selected_label)])

        try:
            ds = xr.open_dataset(selected_path)
            da = ds[variable_id]

            # Shift 0-360 longitude to -180/180
            if float(da.lon.max()) > 180:
                da = da.assign_coords(
                    lon=(((da.lon + 180) % 360) - 180)
                ).sortby("lon")

            # Convert Kelvin to Celsius if temperature variable
            if variable_id in ("tas", "tasmax", "tasmin", "tos"):
                if float(da.mean()) > 100:
                    da = da - 273.15
                    unit_label = "deg C"
                else:
                    unit_label = da.attrs.get("units", "")
            else:
                unit_label = da.attrs.get("units", "")

            n_times = da.sizes.get("time", 1)
            if n_times > 1:
                time_idx = st.slider(
                    "Time step", 0, n_times - 1, 0,
                    key="esgf_multi_map_time",
                )
                plot_da = da.isel(time=time_idx)
                time_val = da.time.values[time_idx]
                time_str = str(time_val)[:10]
            else:
                plot_da = da.squeeze()
                time_str = ""

            import cartopy.crs as ccrs
            import cartopy.feature as cfeature
            import matplotlib.pyplot as plt

            fig = plt.figure(figsize=(10, 5))
            ax = plt.axes(projection=ccrs.PlateCarree())
            plot_da.plot(
                ax=ax, transform=ccrs.PlateCarree(),
                cmap="RdYlBu_r" if "tas" in variable_id or variable_id == "tos" else "viridis",
                cbar_kwargs={"label": f"{variable_id} ({unit_label})"},
            )
            ax.coastlines(resolution="110m", linewidth=0.6)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="gray")
            title = f"{selected_label} - {variable_id}"
            if time_str:
                title += f" ({time_str})"
            ax.set_title(title)
            plt.tight_layout()
            st.pyplot(fig)

            ds.close()

        except Exception as exc:
            st.error(f"Map failed: {type(exc).__name__}: {exc}")
            with st.expander("Full traceback"):
                st.code(traceback.format_exc(), language="python")


def _esgf_multi_open_snippet(config: dict) -> str:
    """Code snippet showing how to reproduce the multi-model comparison."""
    source_ids = config.get("source_ids", [])
    models_str = ", ".join(f'"{s}"' for s in source_ids)
    return (
        "from scripts.esgf_cmip6_download import download_multi\n"
        "\n"
        f"paths = download_multi(\n"
        f'    search_node="{config.get("search_node", "")}",\n'
        f"    source_ids=[{models_str}],\n"
        f'    experiment_id="{config.get("experiment_id", "")}",\n'
        f'    variable_id="{config.get("variable_id", "")}",\n'
        f'    table_id="{config.get("table_id", "")}",\n'
        f'    n_members={config.get("n_members", 1)},\n'
        f'    grid_label="{config.get("grid_label", "gn")}",\n'
        ")\n"
        "\n"
        "import xarray as xr\n"
        "import numpy as np\n"
        "\n"
        "# Open each file and compute area-weighted global mean\n"
        "datasets = []\n"
        "for path in paths:\n"
        "    ds = xr.open_dataset(path)\n"
        f'    da = ds["{config.get("variable_id", "tas")}"]\n'
        "    weights = np.cos(np.deg2rad(da.lat))\n"
        '    ts = da.weighted(weights).mean(["lat", "lon"])\n'
        "    datasets.append(ts)\n"
    )


main()
