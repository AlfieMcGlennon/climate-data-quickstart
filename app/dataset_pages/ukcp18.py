"""UKCP18 regional projections form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "ukcp18"


def render_form() -> dict:
    st.markdown(
        "UK Climate Projections 2018, regional 12 km strand. "
        "See `docs/ukcp18/README.md` in the repo for full reference."
    )
    st.info(
        "Requires a free CEDA account. Set the `CEDA_TOKEN` environment "
        "variable or save the token to `~/.ceda_token`."
    )

    variable = st.selectbox(
        "Variable",
        ["tas", "tasmin", "tasmax", "pr", "psl", "hurs", "sfcWind", "clt"],
        format_func=lambda v: {
            "tas": "tas - Mean air temperature",
            "tasmin": "tasmin - Minimum temperature",
            "tasmax": "tasmax - Maximum temperature",
            "pr": "pr - Precipitation rate",
            "psl": "psl - Mean sea level pressure",
            "hurs": "hurs - Relative humidity",
            "sfcWind": "sfcWind - Wind speed",
            "clt": "clt - Total cloud cover",
        }.get(v, v),
    )

    ensemble_member = st.selectbox(
        "Ensemble member",
        [f"{i:02d}" for i in range(1, 13)],
        help="12 members available (01 to 12).",
    )

    frequency = st.radio(
        "Frequency", ["mon", "day"], horizontal=True,
        format_func=lambda f: {"mon": "Monthly", "day": "Daily"}.get(f, f),
    )

    output_dir, _ = output_dir_input(SLUG)

    return {
        "variable": variable,
        "scenario": "rcp85",
        "collection": "land-rcm",
        "domain": "uk",
        "resolution": "12km",
        "ensemble_member": ensemble_member,
        "frequency": frequency,
        "version": "v20190731",
        "time_period": "198012-208011",
        "output_dir": output_dir,
    }
