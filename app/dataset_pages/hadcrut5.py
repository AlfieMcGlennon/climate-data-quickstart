"""HadCRUT5 form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "hadcrut5"


def render_form() -> dict:
    st.markdown(
        "Global monthly temperature anomalies on a 5 deg grid, 1850-present. "
        "See `docs/hadcrut5/README.md` in the repo for full reference."
    )

    sub_version = st.text_input(
        "Sub-version", "5.1.0.0",
        help="Check https://www.metoffice.gov.uk/hadobs/hadcrut5/ for the current patch level.",
    )
    product = st.selectbox(
        "Product",
        [
            "analysis.anomalies.ensemble_mean",
            "noninfilled.anomalies.ensemble_mean",
            "analysis.summary_series.global.monthly",
            "analysis.summary_series.global.annual",
        ],
        help="'analysis' is infilled (recommended for maps); 'noninfilled' leaves gaps.",
    )
    output_dir, output_filename = output_dir_input(SLUG)

    return {
        "sub_version": sub_version,
        "product": product,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
