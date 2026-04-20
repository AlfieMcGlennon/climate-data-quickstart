"""Earth Data Hub form."""

from __future__ import annotations

import streamlit as st

from app.forms import bbox_input, output_dir_input

SLUG = "earth-data-hub"

EDH_DATASETS = {
    "ERA5 single levels (1940-present)": (
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-single-levels-v0.zarr",
        "2m_temperature",
    ),
    "ERA5-Land (1950-present)": (
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-land-v0.zarr",
        "2m_temperature",
    ),
    "ERA5 single levels monthly means": (
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-single-levels-monthly-means-v0.zarr",
        "2m_temperature",
    ),
}


def render_form() -> dict:
    st.markdown(
        "Stream ERA5 / ERA5-Land / CMIP6 from Earth Data Hub via xarray + Zarr. "
        "Same data as the CDS entries above, accessed lazily instead of downloaded. "
        "[Full docs](docs/earth-data-hub/README.md)."
    )
    st.info(
        "EDH is ideal for point time-series and small regional slices. For "
        "dense global cubes, use the standard CDS route instead."
    )

    dataset = st.selectbox("EDH dataset", list(EDH_DATASETS.keys()))
    edh_dataset_url, default_var = EDH_DATASETS[dataset]

    edh_dataset_url = st.text_input("Zarr URL", edh_dataset_url)
    variable = st.text_input("Variable", default_var)

    c1, c2 = st.columns(2)
    time_start = c1.text_input("Start (ISO)", "2023-07-01T00:00")
    time_end = c2.text_input("End (ISO)", "2023-07-01T23:00")

    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")
    output_dir, output_filename = output_dir_input(SLUG)

    return {
        "edh_dataset_url": edh_dataset_url,
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
