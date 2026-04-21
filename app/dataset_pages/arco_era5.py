"""ARCO-ERA5 form.

Cloud-native access to ERA5 via public Zarr stores on Google Cloud Storage.
No API key, no queue, no registration. The primary output is a streaming
code snippet; an optional download materialises a sliced NetCDF locally.

This follows the same streaming-first pattern as earth_data_hub.py.
"""

from __future__ import annotations

import streamlit as st

from app.forms import bbox_input, output_dir_input

SLUG = "arco-era5"

COMMON_VARIABLES = [
    "2m_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "mean_sea_level_pressure",
    "surface_pressure",
    "total_precipitation",
    "sea_surface_temperature",
    "2m_dewpoint_temperature",
    "total_cloud_cover",
]


def render_form() -> dict:
    st.markdown(
        "Stream ERA5 reanalysis data from the public ARCO-ERA5 Zarr store "
        "on Google Cloud Storage. No API key, no queue, no registration. "
        "See `docs/arco-era5/README.md` in the repo for full reference."
    )
    st.caption(
        "ARCO-ERA5 is a cloud-native copy of ERA5. When you open the store, "
        "only coordinate metadata travels over the wire. Actual data bytes "
        "are fetched only when you compute, plot, or save the slice."
    )

    store_url = st.text_input(
        "Zarr store URL",
        value="gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3",
        help="The public GCS bucket. No authentication needed.",
    )

    var_options = [*COMMON_VARIABLES, "Custom (type below)"]
    var_choice = st.selectbox("Variable", var_options)
    if var_choice == "Custom (type below)":
        variable = st.text_input(
            "Variable name",
            "2m_temperature",
            help="Use the name as it appears in the AR store (matches CDS API names for surface variables).",
        )
    else:
        variable = var_choice

    c1, c2 = st.columns(2)
    time_start = c1.text_input("Start time (ISO)", "2023-07-01T00:00")
    time_end = c2.text_input("End time (ISO)", "2023-07-01T23:00")

    bbox = bbox_input(
        default_preset="UK (55, -8, 49, 2)",
        key_prefix="arco_bbox",
    )

    output_dir, output_filename = output_dir_input(
        SLUG, key_prefix="arco_output",
    )

    return {
        "store_url": store_url,
        "variable": variable,
        "time_start": time_start,
        "time_end": time_end,
        "lat_north": bbox.north,
        "lat_south": bbox.south,
        "lon_west": bbox.west,
        "lon_east": bbox.east,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }


def streaming_snippet(config: dict) -> str:
    """Return a copy-pasteable code block for lazy access to ARCO-ERA5."""
    return f'''\
import xarray as xr

# Open the ARCO-ERA5 Zarr store lazily. Only coordinate metadata is
# fetched here. No API key or registration needed.
ds = xr.open_zarr(
    "{config["store_url"]}",
    chunks=None,
    storage_options=dict(token="anon"),
)

# Filter to the valid time range recorded in the store metadata
ds = ds.sel(time=slice(ds.attrs["valid_time_start"], ds.attrs["valid_time_stop"]))

# Subset to the region and time window. Still lazy at this point.
subset = ds["{config["variable"]}"].sel(
    time=slice("{config["time_start"]}", "{config["time_end"]}"),
    latitude=slice({config["lat_north"]}, {config["lat_south"]}),
    longitude=slice({config["lon_west"]}, {config["lon_east"]}),
)

# Materialise only the bytes for this slice
subset.load()
print(subset)

# Optional: save to NetCDF
# subset.to_netcdf("arco_era5_slice.nc")
'''
