"""CMIP6 form."""

from __future__ import annotations

import streamlit as st

from app.forms import (
    bbox_input,
    month_multiselect,
    output_dir_input,
    year_range_input,
)

SLUG = "cmip6"

# Commonly used models on the CDS
MODELS = [
    "mpi_esm1_2_lr", "mpi_esm1_2_hr", "cnrm_cm6_1", "cnrm_esm2_1",
    "miroc6", "miroc_es2l", "ukesm1_0_ll", "hadgem3_gc31_ll",
    "access_cm2", "cesm2", "cesm2_waccm", "ec_earth3", "ec_earth3_cc",
    "gfdl_esm4", "ipsl_cm6a_lr", "mri_esm2_0", "noresm2_mm",
    "canesm5", "inm_cm5_0",
]

EXPERIMENTS = [
    "historical",
    "ssp1_2_6", "ssp2_4_5", "ssp3_7_0", "ssp5_8_5",
    "ssp1_1_9", "ssp4_3_4", "ssp4_6_0",
]

COMMON_VARIABLES = [
    "near_surface_air_temperature",
    "daily_maximum_near_surface_air_temperature",
    "daily_minimum_near_surface_air_temperature",
    "precipitation",
    "sea_level_pressure",
    "surface_air_pressure",
    "near_surface_wind_speed",
    "sea_surface_temperature",
    "total_cloud_cover_percentage",
    "snowfall_flux",
    "evaporation_including_sublimation_and_transpiration",
]


def render_form() -> dict:
    st.markdown(
        "Multi-model CMIP6 projections via the CDS. "
        "One model, one scenario per request is the simplest start. "
        "[Full docs](docs/cmip6/README.md)."
    )
    st.info(
        "For research-grade ensemble work, `intake-esm` with the Pangeo Zarr "
        "mirror is far more efficient than the CDS."
    )

    model = st.selectbox("Model", MODELS, index=0)
    experiment = st.selectbox("Experiment", EXPERIMENTS, index=4)  # ssp5_8_5
    variable = st.selectbox("Variable", COMMON_VARIABLES, index=0)
    temporal_resolution = st.radio(
        "Temporal resolution", ["monthly", "daily", "fixed"], horizontal=True,
    )

    years = year_range_input(default=(2050, 2050), min_year=1850, max_year=2100)
    months = month_multiselect(default=tuple(range(1, 13)))
    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")
    output_dir, output_filename = output_dir_input(SLUG)

    return {
        "model": model,
        "experiment": experiment,
        "variable": variable,
        "temporal_resolution": temporal_resolution,
        "years": years,
        "months": months,
        "bbox": bbox.as_list(),
        "output_dir": output_dir,
        "output_filename": output_filename,
    }
