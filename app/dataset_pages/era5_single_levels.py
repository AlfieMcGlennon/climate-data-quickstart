"""ERA5 single levels form."""

from __future__ import annotations

import streamlit as st

from app.forms import (
    bbox_input,
    chunked_download_options,
    day_multiselect,
    hour_multiselect,
    month_multiselect,
    output_dir_input,
    year_range_input,
)

SLUG = "era5-single-levels"

COMMON_VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "mean_sea_level_pressure",
    "surface_pressure",
    "total_precipitation",
    "sea_surface_temperature",
    "surface_solar_radiation_downwards",
    "total_cloud_cover",
]


def render_form() -> dict:
    st.markdown(
        "Hourly ERA5 reanalysis on single (surface/near-surface) levels. "
        "Global, 0.25 deg, 1940-present. "
        "See `docs/era5-single-levels/README.md` in the repo for full reference."
    )

    variables = st.multiselect(
        "Variables",
        COMMON_VARIABLES,
        default=["2m_temperature"],
        help="Top 10 most common variables. For the full 250+ list see the docs.",
    )
    custom = st.text_input(
        "Add custom variable name (optional)",
        placeholder="e.g. 100m_u_component_of_wind",
    )
    if custom:
        variables = [*variables, custom.strip()]

    years = year_range_input(default=(2023, 2023))
    months = month_multiselect(default=(7,))
    days = day_multiselect()
    hours = hour_multiselect()
    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")

    data_format = st.radio("Format", ["netcdf", "grib"], horizontal=True)

    output_dir, output_filename = output_dir_input(SLUG)
    chunk_opts = chunked_download_options(key_prefix="era5sl_chunk")

    return {
        "variables": variables,
        "years": years,
        "months": months,
        "days": days,
        "hours": hours,
        "bbox": bbox.as_list(),
        "data_format": data_format,
        "download_format": "unarchived",
        "output_dir": output_dir,
        "output_filename": output_filename,
        "chunked": chunk_opts,
    }
