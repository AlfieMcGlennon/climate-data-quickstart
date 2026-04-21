"""EDH catalogue explorer form.

Simplified access to the full Earth Data Hub catalogue: ERA5 variants,
CMIP6 models across SSP scenarios, and Copernicus DEM. Builds the Zarr
URL automatically from dropdown selections instead of requiring the user
to paste a URL.

The primary output is a streaming code snippet (same pattern as the basic
EDH page). An optional download materialises the slice as a local NetCDF.
"""

from __future__ import annotations

import streamlit as st

from app.forms import bbox_input, output_dir_input

SLUG = "edh-explorer"


# ── ERA5 datasets on EDH ──────────────────────────────────────────

_ERA5_DATASETS = {
    "ERA5 single levels (hourly, 1940-present)": "reanalysis-era5-single-levels-v0.zarr",
    "ERA5 single levels monthly means": "reanalysis-era5-single-levels-monthly-means-v0.zarr",
    "ERA5 pressure levels (hourly)": "reanalysis-era5-pressure-levels-v0.zarr",
    "ERA5-Land (hourly, 1950-present)": "reanalysis-era5-land-no-antartica-v0.zarr",
    "ERA5-Land daily (EDH-derived)": "era5-land-daily-utc-v1.zarr",
}

_ERA5_COMMON_VARS = [
    ("2m temperature", "t2m"),
    ("2m dewpoint temperature", "d2m"),
    ("10m u-wind", "u10"),
    ("10m v-wind", "v10"),
    ("100m u-wind", "u100"),
    ("100m v-wind", "v100"),
    ("Mean sea level pressure", "msl"),
    ("Surface pressure", "sp"),
    ("Sea surface temperature", "sst"),
    ("Total cloud cover", "tcc"),
    ("Total precipitation", "tp"),
    ("Surface solar radiation downwards", "ssrd"),
]


# ── CMIP6 models on EDH ──────────────────────────────────────────

_CMIP6_MODELS = {
    "CESM2 (NCAR)": "CESM2",
    "CMCC-CM2-SR5 (CMCC)": "CMCC-CM2-SR5",
    "EC-Earth3-CC (EC-Earth Consortium)": "EC-Earth3-CC",
    "IPSL-CM6A-LR (IPSL)": "IPSL-CM6A-LR",
    "MPI-ESM1-2-HR (DKRZ)": "MPI-ESM1-2-HR",
    "NorESM2-MM (NCC)": "NorESM2-MM",
}

_CMIP6_SCENARIOS = {
    "CESM2": ["historical", "ssp126", "ssp245", "ssp370", "ssp585"],
    "CMCC-CM2-SR5": ["historical", "ssp126", "ssp245", "ssp370", "ssp585"],
    "EC-Earth3-CC": ["ssp245", "ssp585"],
    "IPSL-CM6A-LR": ["historical", "ssp119", "ssp126", "ssp245", "ssp370", "ssp434", "ssp460", "ssp585"],
    "MPI-ESM1-2-HR": ["historical", "ssp126", "ssp245", "ssp370", "ssp585"],
    "NorESM2-MM": ["historical", "ssp126", "ssp245", "ssp370", "ssp585"],
}

_CMIP6_SCENARIO_LABELS = {
    "historical": "Historical (1850-2014)",
    "ssp119": "SSP1-1.9 (very low emissions)",
    "ssp126": "SSP1-2.6 (low emissions)",
    "ssp245": "SSP2-4.5 (intermediate)",
    "ssp370": "SSP3-7.0 (high emissions)",
    "ssp434": "SSP4-3.4 (low forcing, high inequality)",
    "ssp460": "SSP4-6.0 (mid forcing, high inequality)",
    "ssp585": "SSP5-8.5 (very high emissions)",
}

_CMIP6_COMMON_VARS = [
    ("Near-surface air temperature", "tas"),
    ("Precipitation", "pr"),
    ("Sea level pressure", "psl"),
    ("Near-surface specific humidity", "huss"),
    ("Eastward near-surface wind", "uas"),
    ("Northward near-surface wind", "vas"),
    ("Surface downwelling shortwave radiation", "rsds"),
    ("Surface downwelling longwave radiation", "rlds"),
    ("Near-surface wind speed", "sfcWind"),
    ("Daily maximum near-surface temperature", "tasmax"),
    ("Daily minimum near-surface temperature", "tasmin"),
]

_CMIP6_FREQUENCIES = ["day", "mon"]


# ── URL builders ──────────────────────────────────────────────────

_EDH_BASE = "https://data.earthdatahub.destine.eu"


def _era5_url(dataset_suffix: str) -> str:
    return f"{_EDH_BASE}/era5/{dataset_suffix}"


def _cmip6_url(model: str, scenario: str, frequency: str) -> str:
    activity = "ScenarioMIP" if scenario != "historical" else "CMIP"
    return f"{_EDH_BASE}/cmip6/{model}-{activity}-r1i1p1f1-{frequency}-gr-v0.zarr"


# ── Form ──────────────────────────────────────────────────────────

def render_form() -> dict:
    st.markdown(
        "Browse the full Earth Data Hub catalogue from one page. "
        "Pick a dataset family, model, scenario, and variable, and the "
        "app builds the Zarr URL for you. Same streaming-first pattern "
        "as the basic EDH page, but with no URL to paste."
    )

    family = st.radio(
        "Dataset family",
        ["ERA5 (reanalysis)", "CMIP6 (climate projections)"],
        horizontal=True,
        key="edh_family",
    )

    if family == "ERA5 (reanalysis)":
        return _era5_form()
    else:
        return _cmip6_form()


def _era5_form() -> dict:
    dataset_label = st.selectbox("Dataset", list(_ERA5_DATASETS.keys()))
    dataset_suffix = _ERA5_DATASETS[dataset_label]
    zarr_url = _era5_url(dataset_suffix)

    st.caption(f"Zarr URL: `{zarr_url}`")

    var_options = [f"{label} ({short})" for label, short in _ERA5_COMMON_VARS]
    var_options.append("Custom (type short name below)")
    var_choice = st.selectbox("Variable", var_options, key="edh_era5_var")

    if var_choice.startswith("Custom"):
        variable = st.text_input(
            "GRIB short name", "t2m",
            help="EDH ERA5 stores use GRIB short names. Check ds.data_vars after opening.",
            key="edh_era5_custom_var",
        )
    else:
        idx = var_options.index(var_choice)
        variable = _ERA5_COMMON_VARS[idx][1]

    c1, c2 = st.columns(2)
    time_start = c1.text_input("Start time (ISO)", "2023-07-01T00:00", key="edh_era5_t0")
    time_end = c2.text_input("End time (ISO)", "2023-07-01T23:00", key="edh_era5_t1")

    bbox = bbox_input(
        default_preset="UK (55, -8, 49, 2)",
        key_prefix="edh_era5_bbox",
    )

    output_dir, output_filename = output_dir_input(
        SLUG, key_prefix="edh_era5_output",
    )

    return {
        "edh_dataset_url": zarr_url,
        "variable": variable,
        "time_start": time_start,
        "time_end": time_end,
        "lat_north": bbox.north,
        "lat_south": bbox.south,
        "lon_west": bbox.west,
        "lon_east": bbox.east,
        "output_dir": output_dir,
        "output_filename": output_filename,
        "family": "era5",
    }


def _cmip6_form() -> dict:
    st.caption(
        "EDH hosts a curated set of six CMIP6 models. Each store contains "
        "one ensemble member (r1i1p1f1), daily or monthly frequency, on a "
        "regridded latitude-longitude grid. Historical runs cover 1850-2014; "
        "SSP scenarios cover 2015-2100."
    )

    model_label = st.selectbox("Model", list(_CMIP6_MODELS.keys()), key="edh_cmip6_model")
    model_id = _CMIP6_MODELS[model_label]

    available_scenarios = _CMIP6_SCENARIOS[model_id]
    scenario_options = [
        _CMIP6_SCENARIO_LABELS.get(s, s) for s in available_scenarios
    ]
    scenario_label = st.selectbox(
        "Scenario", scenario_options, key="edh_cmip6_scenario",
    )
    scenario_id = available_scenarios[scenario_options.index(scenario_label)]

    frequency = st.radio(
        "Frequency", _CMIP6_FREQUENCIES, horizontal=True, key="edh_cmip6_freq",
        help="Daily (day) or monthly (mon). Not all combinations may be available.",
    )

    zarr_url = _cmip6_url(model_id, scenario_id, frequency)
    st.caption(f"Zarr URL: `{zarr_url}`")

    var_options = [f"{label} ({short})" for label, short in _CMIP6_COMMON_VARS]
    var_options.append("Custom (type below)")
    var_choice = st.selectbox("Variable", var_options, key="edh_cmip6_var")

    if var_choice.startswith("Custom"):
        variable = st.text_input(
            "CMIP6 variable ID", "tas",
            help="Standard CMIP6 variable identifiers (tas, pr, psl, etc.).",
            key="edh_cmip6_custom_var",
        )
    else:
        idx = var_options.index(var_choice)
        variable = _CMIP6_COMMON_VARS[idx][1]

    c1, c2 = st.columns(2)
    if scenario_id == "historical":
        default_t0, default_t1 = "2000-01-01", "2000-12-31"
    else:
        default_t0, default_t1 = "2050-01-01", "2050-12-31"
    time_start = c1.text_input("Start time", default_t0, key="edh_cmip6_t0")
    time_end = c2.text_input("End time", default_t1, key="edh_cmip6_t1")

    bbox = bbox_input(
        default_preset="UK (55, -8, 49, 2)",
        key_prefix="edh_cmip6_bbox",
    )

    output_dir, output_filename = output_dir_input(
        SLUG, key_prefix="edh_cmip6_output",
    )

    return {
        "edh_dataset_url": zarr_url,
        "variable": variable,
        "time_start": time_start,
        "time_end": time_end,
        "lat_north": bbox.north,
        "lat_south": bbox.south,
        "lon_west": bbox.west,
        "lon_east": bbox.east,
        "output_dir": output_dir,
        "output_filename": output_filename,
        "family": "cmip6",
        "model": model_id,
        "scenario": scenario_id,
        "frequency": frequency,
    }


def streaming_snippet(config: dict) -> str:
    """Return a copy-pasteable code block for lazy access via EDH."""
    url = config["edh_dataset_url"]
    var = config["variable"]
    t0 = config["time_start"]
    t1 = config["time_end"]
    s = config["lat_south"]
    n = config["lat_north"]
    w = config["lon_west"]
    e = config["lon_east"]

    lines = [
        "import xarray as xr",
        "",
        "ds = xr.open_dataset(",
        f'    "{url}",',
        '    engine="zarr",',
        "    chunks={},",
        '    storage_options={"client_kwargs": {"trust_env": True}},',
        ")",
        "",
    ]

    if config.get("family") == "cmip6":
        lines += [
            '# CMIP6 stores typically use "time" as the dimension name',
            "",
            "# Normalise longitude to -180..180 if needed",
            'if float(ds["longitude"].max()) > 180:',
            '    ds = ds.assign_coords(longitude=(((ds["longitude"] + 180) % 360) - 180))',
            'ds = ds.sortby("latitude").sortby("longitude")',
            "",
            f'subset = ds["{var}"].sel(',
            f'    time=slice("{t0}", "{t1}"),',
            f"    latitude=slice({s}, {n}),",
            f"    longitude=slice({w}, {e}),",
            ")",
        ]
    else:
        lines += [
            '# EDH ERA5 stores use "valid_time"; older ones used "time"',
            'time_dim = "valid_time" if "valid_time" in ds.sizes else "time"',
            "",
            "# Normalise longitude to -180..180 if needed",
            'if float(ds["longitude"].max()) > 180:',
            '    ds = ds.assign_coords(longitude=(((ds["longitude"] + 180) % 360) - 180))',
            'ds = ds.sortby("latitude").sortby("longitude")',
            "",
            f'subset = ds["{var}"].sel(**{{',
            f'    time_dim: slice("{t0}", "{t1}"),',
            f'    "latitude": slice({s}, {n}),',
            f'    "longitude": slice({w}, {e}),',
            "})",
        ]

    lines += [
        "",
        "subset.load()",
        "print(subset)",
    ]
    return "\n".join(lines)
