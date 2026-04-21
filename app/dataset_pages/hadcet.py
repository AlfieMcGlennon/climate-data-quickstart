"""HadCET form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "hadcet"


def render_form() -> dict:
    st.markdown(
        "Central England Temperature: monthly from 1659, daily from 1772. "
        "The longest instrumental temperature record in the world. "
        "See `docs/hadcet/README.md` in the repo for full reference."
    )

    resolution = st.radio("Resolution", ["monthly", "daily"], horizontal=True)
    statistic = st.radio(
        "Statistic", ["mean", "max", "min"], horizontal=True,
        help="max/min are available monthly and daily from 1878.",
    )
    output_dir, output_filename = output_dir_input(SLUG)
    # HadCET writes CSV, override default .nc suffix
    if not output_filename.endswith(".csv"):
        output_filename = f"hadcet_{resolution}_{statistic}.csv"

    return {
        "resolution": resolution,
        "statistic": statistic,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
