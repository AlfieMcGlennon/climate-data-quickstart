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
        "See `docs/e-obs/README.md` in the repo for full reference."
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
    grid_resolution = st.radio("Grid", ["0_1deg", "0_25deg"], horizontal=True,
        format_func=lambda g: g.replace("_", "."),
    )
    version = st.text_input(
        "Version", "31_0e",
        help="Use underscores not dots (e.g. 31_0e). Check the CDS dataset page for the current release.",
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
