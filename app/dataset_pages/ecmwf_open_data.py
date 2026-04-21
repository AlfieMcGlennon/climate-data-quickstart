"""ECMWF Open Data form.

Direct HTTP download of IFS/AIFS forecast fields via the ``ecmwf-opendata``
package. No API key or registration required.
"""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "ecmwf-open-data"

COMMON_PARAMS = [
    "2t", "10u", "10v", "msl", "tp", "sp", "tcc", "2d", "tcwv", "cape",
]


def render_form() -> dict:
    st.markdown(
        "Real-time IFS and AIFS forecast fields from ECMWF Open Data. "
        "Global, 0.25 deg, updated four times daily, up to 10 days ahead. "
        "No registration needed. "
        "See `docs/ecmwf-open-data/README.md` in the repo for full reference."
    )

    params = st.multiselect(
        "Parameters (GRIB short names)",
        COMMON_PARAMS,
        default=["2t"],
        help="Top 10 common parameters. See the docs for the full parameter list.",
    )
    custom = st.text_input(
        "Add custom parameter (optional)",
        placeholder="e.g. gh, r, vo",
    )
    if custom:
        params = [*params, custom.strip()]

    step = st.number_input(
        "Forecast step (hours)",
        min_value=0,
        max_value=360,
        value=24,
        step=3,
        help="Lead time in hours. 0-144 every 3 h, then 150-240 every 6 h for 00z/12z runs.",
    )

    fc_type = st.radio(
        "Forecast type",
        ["fc", "cf", "pf"],
        horizontal=True,
        help="fc = HRES deterministic, cf = control, pf = perturbed ensemble members.",
    )

    model = st.radio(
        "Model",
        ["ifs", "aifs-single", "aifs-ens"],
        horizontal=True,
        help="IFS is the standard model. AIFS is the ML-based model.",
    )

    # Stream is determined by the combination of time and type, but the
    # download script handles this via the ecmwf-opendata client defaults.
    # We derive it automatically.
    stream = "oper" if fc_type == "fc" else "enfo"

    output_dir, output_filename = output_dir_input(
        SLUG, key_prefix="ecmwf_od_output",
    )
    # Override the default .nc extension with .grib2
    if output_filename.endswith(".nc"):
        output_filename = output_filename.replace(".nc", ".grib2")

    return {
        "params": params,
        "step": step,
        "fc_type": fc_type,
        "stream": stream,
        "model": model,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
