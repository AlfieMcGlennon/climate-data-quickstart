"""E-OBS form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "e-obs"

VARIABLES = [
    "mean_temperature", "maximum_temperature", "minimum_temperature",
    "precipitation_amount", "mean_sea_level_pressure",
    "relative_humidity", "global_radiation", "wind_speed",
]


def render_form() -> dict:
    st.markdown(
        "European gridded daily observations from the ECA&D station network. "
        "[Full docs](docs/e-obs/README.md)."
    )
    st.warning(
        "The CDS returns the WHOLE 1950-present history in a single file. "
        "Expect ~1 GB per variable; first download is slow."
    )

    variable = st.selectbox("Variable", VARIABLES, index=0)
    product_type = st.selectbox(
        "Product type",
        ["ensemble_mean", "ensemble_spread", "ensemble_members"],
        help="'ensemble_members' returns up to 100 files.",
    )
    grid_resolution = st.radio("Grid", ["0.1deg", "0.25deg"], horizontal=True)
    version = st.text_input(
        "Version", "29.0e",
        help="Pin a version for reproducible work. Check the CDS dataset page for the current release.",
    )

    output_dir, output_filename = output_dir_input(SLUG)

    return {
        "variable": variable,
        "product_type": product_type,
        "grid_resolution": grid_resolution,
        "version": version,
        "period": "full_period",
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
