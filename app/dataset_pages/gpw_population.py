"""GPWv4 population density form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "gpw-population"


def render_form() -> dict:
    st.markdown(
        "Global gridded population density from CIESIN/NASA SEDAC. "
        "See `docs/gpw-population/README.md` in the repo for full reference."
    )
    st.info(
        "Requires a free NASA Earthdata account. "
        "Credentials must be in `~/.netrc` or `~/_netrc` with an entry for "
        "`machine urs.earthdata.nasa.gov`."
    )

    year = st.selectbox(
        "Year", [2000, 2005, 2010, 2015, 2020], index=4,
        help="Five discrete census-based snapshots. 2020 is an extrapolation.",
    )
    resolution = st.selectbox(
        "Resolution",
        ["2pt5_min", "30_sec", "15_min", "30_min", "1_deg"],
        format_func=lambda r: {
            "30_sec": "30 arc-sec (~1 km) - several GB",
            "2pt5_min": "2.5 arc-min (~5 km) - recommended",
            "15_min": "15 arc-min (~28 km)",
            "30_min": "30 arc-min (~55 km)",
            "1_deg": "1 degree (~111 km)",
        }.get(r, r),
    )

    output_dir, _ = output_dir_input(SLUG)

    return {
        "year": year,
        "resolution": resolution,
        "output_dir": output_dir,
    }
