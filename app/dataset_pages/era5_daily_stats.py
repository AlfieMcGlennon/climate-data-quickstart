"""ERA5 daily statistics form."""

from __future__ import annotations

import streamlit as st

from app.forms import (
    bbox_input,
    day_multiselect,
    month_multiselect,
    output_dir_input,
    year_range_input,
)

SLUG = "era5-daily-stats"

VARIABLES = [
    "2m_temperature", "2m_dewpoint_temperature",
    "10m_u_component_of_wind", "10m_v_component_of_wind",
    "total_precipitation", "mean_sea_level_pressure", "surface_pressure",
    "sea_surface_temperature", "total_cloud_cover",
    "surface_solar_radiation_downwards", "snowfall", "evaporation",
]


def render_form() -> dict:
    st.markdown(
        "Pre-computed daily aggregates of ERA5 single levels. "
        "Roughly 24x smaller than pulling hourly data and resampling yourself. "
        "[Full docs](docs/era5-daily-stats/README.md)."
    )

    variables = st.multiselect("Variables", VARIABLES, default=["2m_temperature"])

    daily_statistic = st.selectbox(
        "Statistic",
        ["daily_mean", "daily_maximum", "daily_minimum", "daily_sum"],
        help="daily_sum only works on accumulated variables (e.g. total_precipitation).",
    )
    frequency = st.selectbox(
        "Sub-daily sampling",
        ["1_hourly", "3_hourly", "6_hourly"],
        help="Sampling frequency used under the hood for the aggregation.",
    )
    time_zone = st.selectbox(
        "Time zone",
        [f"utc{sign}{h:02d}:00" for sign in ["+", "-"] for h in range(0, 13)],
        index=0,
    )

    years = year_range_input(default=(2023, 2023))
    months = month_multiselect(default=(7,))
    days = day_multiselect(default_all=True)
    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")

    output_dir, output_filename = output_dir_input(SLUG)

    return {
        "variables": variables,
        "daily_statistic": daily_statistic,
        "frequency": frequency,
        "time_zone": time_zone,
        "years": years,
        "months": months,
        "days": days,
        "bbox": bbox.as_list(),
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
