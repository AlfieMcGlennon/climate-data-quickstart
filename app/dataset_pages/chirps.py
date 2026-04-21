"""CHIRPS form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "chirps"


def render_form() -> dict:
    st.markdown(
        "Quasi-global daily rainfall from UCSB Climate Hazards Center. "
        "See `docs/chirps/README.md` in the repo for full reference."
    )
    st.warning(
        "CHIRPS covers 50 S to 50 N only. The UK is outside coverage. "
        "Use ERA5-Land or HadUK-Grid for UK precipitation."
    )

    year = st.number_input("Year", 1981, 2026, 2023)
    grid = st.radio(
        "Grid", ["p25", "p05"], horizontal=True,
        help="p25 = 0.25 deg (~100 MB per year). p05 = 0.05 deg (~3 GB per year).",
    )

    output_dir, output_filename = output_dir_input(SLUG)
    # CHIRPS uses its own filename scheme by default
    if output_filename.endswith("_download.nc"):
        output_filename = f"chirps-v2.0.{int(year)}.days_{grid}.nc"

    return {
        "year": int(year),
        "grid": grid,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
