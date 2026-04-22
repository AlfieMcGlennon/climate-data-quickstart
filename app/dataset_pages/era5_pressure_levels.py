"""ERA5 pressure levels form."""

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

SLUG = "era5-pressure-levels"

VARIABLES = [
    "geopotential", "temperature", "u_component_of_wind", "v_component_of_wind",
    "specific_humidity", "relative_humidity", "vertical_velocity",
    "divergence", "vorticity", "potential_vorticity",
    "fraction_of_cloud_cover", "ozone_mass_mixing_ratio",
    "specific_cloud_liquid_water_content", "specific_cloud_ice_water_content",
    "specific_rain_water_content", "specific_snow_water_content",
]

PRESSURE_LEVELS = [
    "1", "2", "3", "5", "7", "10", "20", "30", "50", "70", "100", "125", "150",
    "175", "200", "225", "250", "300", "350", "400", "450", "500", "550", "600",
    "650", "700", "750", "775", "800", "825", "850", "875", "900", "925", "950",
    "975", "1000",
]


def render_form() -> dict:
    st.markdown(
        "Hourly ERA5 reanalysis on 37 pressure levels (1 to 1000 hPa). "
        "See `docs/era5-pressure-levels/README.md` in the repo for full reference."
    )

    variables = st.multiselect("Variables", VARIABLES, default=["temperature"])
    pressure_levels = st.multiselect(
        "Pressure levels (hPa)",
        PRESSURE_LEVELS,
        default=["500"],
        help="500 hPa is the classic mid-troposphere level; 850 hPa for boundary layer proxies; above 100 hPa for stratospheric work.",
    )

    years = year_range_input(default=(2023, 2023))
    months = month_multiselect(default=(7,))
    days = day_multiselect()
    hours = hour_multiselect()
    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")

    data_format = st.radio("Format", ["netcdf", "grib"], horizontal=True)
    output_dir, output_filename = output_dir_input(SLUG)
    chunk_opts = chunked_download_options(key_prefix="era5pl_chunk")

    return {
        "variables": variables,
        "pressure_levels": pressure_levels,
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
