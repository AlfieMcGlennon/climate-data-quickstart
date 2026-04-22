"""GloFAS historical form."""

from __future__ import annotations

import streamlit as st

from app.forms import bbox_input, chunked_download_options, output_dir_input


SLUG = "glofas"


def render_form() -> dict:
    st.markdown(
        "Daily global river discharge reanalysis from GloFAS. "
        "See `docs/glofas/README.md` in the repo for full reference."
    )
    st.warning(
        "GloFAS is on the Copernicus CEMS Early Warning Data Store (EWDS), "
        "not the main CDS. You need a separate EWDS account and token in "
        "the `EWDS_KEY` environment variable."
    )

    system_version = st.selectbox(
        "System version",
        ["version_4_0", "version_3_1", "version_2_1"],
        index=0,
    )
    hydrological_model = (
        "lisflood" if system_version == "version_4_0" else "htessel_lisflood"
    )
    st.caption(f"Hydrological model (auto): `{hydrological_model}`")

    product_type = st.radio(
        "Product type", ["consolidated", "intermediate"], horizontal=True,
        help="'consolidated' for the main back-catalogue; 'intermediate' for the ERA5T-driven NRT tail.",
    )

    c1, c2 = st.columns(2)
    hyear = [str(c1.number_input("Year (hyear)", 1979, 2026, 2020))]
    hmonth = [f"{c2.number_input('Month (hmonth)', 1, 12, 12):02d}"]
    hday = st.multiselect(
        "Day(s) of month (hday)",
        [f"{d:02d}" for d in range(1, 32)],
        default=["01"],
    )

    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")
    data_format = st.radio("Format", ["grib2", "netcdf"], horizontal=True)
    output_dir, output_filename = output_dir_input(SLUG)
    if data_format == "grib2" and not output_filename.endswith(".grib"):
        output_filename = output_filename.rsplit(".", 1)[0] + ".grib"
    chunk_opts = chunked_download_options(
        key_prefix="glofas_chunk", default_chunk_by="year",
    )

    return {
        "system_version": system_version,
        "hydrological_model": hydrological_model,
        "product_type": product_type,
        "variable": "river_discharge_in_the_last_24_hours",
        "hyear": hyear,
        "hmonth": hmonth,
        "hday": hday,
        "bbox": bbox.as_list(),
        "data_format": data_format,
        "download_format": "unarchived",
        "output_dir": output_dir,
        "output_filename": output_filename,
        "chunked": chunk_opts,
    }
