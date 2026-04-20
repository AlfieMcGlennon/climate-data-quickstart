"""ERA5-Land form."""

from __future__ import annotations

import streamlit as st

from app.forms import (
    bbox_input,
    day_multiselect,
    hour_multiselect,
    month_multiselect,
    output_dir_input,
    year_range_input,
)

SLUG = "era5-land"

COMMON_VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "skin_temperature",
    "soil_temperature_level_1",
    "volumetric_soil_water_layer_1",
    "snow_depth_water_equivalent",
    "total_precipitation",
    "surface_solar_radiation_downwards",
    "surface_latent_heat_flux",
    "surface_sensible_heat_flux",
]


def render_form() -> dict:
    st.markdown(
        "Hourly ERA5-Land reanalysis at 0.1 deg (~9 km), land-only, 1950-present. "
        "[Full docs](docs/era5-land/README.md)."
    )

    variables = st.multiselect(
        "Variables",
        COMMON_VARIABLES,
        default=["2m_temperature"],
        help="Top 10 most common. See docs for the full ~50 variable list.",
    )
    custom = st.text_input("Add custom variable name (optional)")
    if custom:
        variables = [*variables, custom.strip()]

    years = year_range_input(default=(2023, 2023), min_year=1950)
    months = month_multiselect(default=(7,))
    days = day_multiselect()
    hours = hour_multiselect()
    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")

    data_format = st.radio("Format", ["netcdf", "grib"], horizontal=True)
    output_dir, output_filename = output_dir_input(SLUG)

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
    }
