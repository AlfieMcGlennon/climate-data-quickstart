"""C3S seasonal forecast form.

Monthly-mean seasonal forecast data from the Copernicus Climate Data Store.
Uses the CDS API (same credentials as ERA5). Output is GRIB only; NetCDF is
unreliable for this dataset.
"""

from __future__ import annotations

import streamlit as st

from app.forms import bbox_input, output_dir_input

SLUG = "c3s-seasonal"

TOP_VARIABLES = [
    "2m_temperature",
    "total_precipitation",
    "mean_sea_level_pressure",
    "sea_surface_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "maximum_2m_temperature_in_the_last_24_hours",
    "minimum_2m_temperature_in_the_last_24_hours",
    "total_cloud_cover",
    "sea_ice_cover",
]

CENTRES = [
    "ecmwf", "ukmo", "meteo_france", "dwd", "cmcc", "ncep", "jma", "eccc", "bom",
]

PRODUCT_TYPES = [
    "monthly_mean",
    "ensemble_mean",
    "hindcast_climate_mean",
    "monthly_minimum",
    "monthly_maximum",
    "monthly_standard_deviation",
]

MONTH_LABELS = [
    "01 Jan", "02 Feb", "03 Mar", "04 Apr", "05 May", "06 Jun",
    "07 Jul", "08 Aug", "09 Sep", "10 Oct", "11 Nov", "12 Dec",
]


def render_form() -> dict:
    st.markdown(
        "C3S multi-system seasonal forecast data from the Copernicus CDS. "
        "Monthly-mean fields from nine forecasting centres, up to 6 months ahead. "
        "See `docs/c3s-seasonal/README.md` in the repo for full reference."
    )

    variable = st.selectbox(
        "Variable",
        TOP_VARIABLES,
        help="Top 10 variables. See the CDS dataset page for the full catalogue.",
    )

    c1, c2 = st.columns(2)
    originating_centre = c1.selectbox(
        "Originating centre",
        CENTRES,
        help="Each centre runs its own seasonal model. System numbers are centre-specific.",
    )
    system = c2.text_input(
        "System version",
        value="51",
        help="System number depends on the centre. ECMWF system 51 is current as of 2024.",
    )

    product_type = st.selectbox("Product type", PRODUCT_TYPES)

    c3, c4 = st.columns(2)
    year = c3.number_input(
        "Initialisation year",
        min_value=1981,
        max_value=2026,
        value=2024,
    )
    month_label = c4.selectbox("Initialisation month", MONTH_LABELS)
    month = month_label.split()[0]

    leadtime_months = st.multiselect(
        "Lead time months",
        ["1", "2", "3", "4", "5", "6"],
        default=["1", "2", "3", "4", "5", "6"],
        help="Months ahead from the initialisation date.",
    )

    bbox = bbox_input(
        default_preset="Europe (72, -25, 34, 45)",
        key_prefix="c3s_bbox",
    )

    st.radio(
        "Format",
        ["grib"],
        horizontal=True,
        help="GRIB is the only reliable format for this dataset. NetCDF is experimental and often fails.",
    )
    fmt = "grib"

    output_dir, output_filename = output_dir_input(
        SLUG, key_prefix="c3s_output",
    )
    # Override the default .nc extension with .grib
    if output_filename.endswith(".nc"):
        output_filename = output_filename.replace(".nc", ".grib")

    return {
        "variable": variable,
        "originating_centre": originating_centre,
        "system": system,
        "product_type": product_type,
        "year": str(year),
        "month": month,
        "leadtime_months": leadtime_months,
        "area": bbox.as_list(),
        "fmt": fmt,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
