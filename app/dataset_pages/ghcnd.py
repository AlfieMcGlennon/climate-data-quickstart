"""GHCNd form."""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "ghcnd"

# Sample UK stations - users can type any 11-char GHCNd ID
UK_STATIONS = {
    "London Heathrow (UKM00003772)": "UKM00003772",
    "London Gatwick (UKM00003776)": "UKM00003776",
    "Manchester Airport (UKM00003334)": "UKM00003334",
    "Edinburgh Gogarbank (UKM00003166)": "UKM00003166",
    "Belfast Aldergrove (UKM00003917)": "UKM00003917",
    "Lerwick Shetland (UKM00003005)": "UKM00003005",
    "Custom (type ID below)": None,
}

ELEMENTS = ["TMAX", "TMIN", "TAVG", "PRCP", "SNOW", "SNWD"]


def render_form() -> dict:
    st.markdown(
        "Daily weather-station observations from NOAA. "
        "100,000+ stations worldwide. [Full docs](docs/ghcnd/README.md)."
    )

    label = st.selectbox("Station", list(UK_STATIONS.keys()))
    station_id = UK_STATIONS[label]
    if station_id is None:
        station_id = st.text_input(
            "GHCNd station ID (11 chars)",
            "UKM00003772",
            help="Find yours in ghcnd-stations.txt - see the docs.",
        )

    elements = st.multiselect(
        "Elements", ELEMENTS,
        default=["TMAX", "TMIN", "PRCP"],
        help="GHCNd has ~50 total; these are the common core five plus TAVG.",
    )

    drop_failed_qc = st.checkbox(
        "Drop rows that failed QC (recommended)", value=True,
    )

    output_dir, output_filename = output_dir_input(SLUG)
    if not output_filename.endswith(".csv"):
        output_filename = f"ghcnd_{station_id}.csv"

    return {
        "station_id": station_id,
        "elements": tuple(elements),
        "drop_failed_qc": drop_failed_qc,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
