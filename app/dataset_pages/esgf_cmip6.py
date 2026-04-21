"""ESGF CMIP6 form.

Direct access to the full CMIP6 archive via the Earth System Grid
Federation search API. Two modes: single-file download, or multi-model
comparison that downloads one file per model and renders them together.
"""

from __future__ import annotations

import streamlit as st

from app.forms import output_dir_input

SLUG = "esgf-cmip6"

# ── Models (source_id) ───────────────────────────────────────────

_MODELS: dict[str, str] = {
    "ACCESS-CM2 (Australia, ~250 km)": "ACCESS-CM2",
    "CanESM5 (Canada, ~250 km, 50+ ensemble members)": "CanESM5",
    "CESM2 (USA/NCAR, ~100 km)": "CESM2",
    "CNRM-CM6-1 (France, ~150 km, uses f2)": "CNRM-CM6-1",
    "EC-Earth3 (European consortium, ~100 km)": "EC-Earth3",
    "GFDL-ESM4 (USA/NOAA, ~100 km)": "GFDL-ESM4",
    "HadGEM3-GC31-LL (UK Met Office, ~250 km, uses f2)": "HadGEM3-GC31-LL",
    "IPSL-CM6A-LR (France, ~250 km)": "IPSL-CM6A-LR",
    "MIROC6 (Japan, ~250 km)": "MIROC6",
    "MPI-ESM1-2-HR (Germany, ~100 km, high-res)": "MPI-ESM1-2-HR",
    "MPI-ESM1-2-LR (Germany, ~250 km)": "MPI-ESM1-2-LR",
    "MRI-ESM2-0 (Japan, ~100 km)": "MRI-ESM2-0",
    "NorESM2-LM (Norway, ~250 km)": "NorESM2-LM",
    "NorESM2-MM (Norway, ~100 km)": "NorESM2-MM",
    "UKESM1-0-LL (UK NERC/Met Office, ~250 km, uses f2)": "UKESM1-0-LL",
}

_F2_MODELS = {"CNRM-CM6-1", "HadGEM3-GC31-LL", "UKESM1-0-LL"}

_MODEL_IDS = list(_MODELS.values())


def _flagship_member(source_id: str) -> str:
    return "r1i1p1f2" if source_id in _F2_MODELS else "r1i1p1f1"


# ── Experiments ──────────────────────────────────────────────────

_EXPERIMENTS: dict[str, tuple[str, str]] = {
    "Historical (1850-2014)": ("historical", "CMIP"),
    "SSP1-2.6 (low emissions, 2015-2100)": ("ssp126", "ScenarioMIP"),
    "SSP2-4.5 (intermediate, 2015-2100)": ("ssp245", "ScenarioMIP"),
    "SSP3-7.0 (high emissions, 2015-2100)": ("ssp370", "ScenarioMIP"),
    "SSP5-8.5 (very high emissions, 2015-2100)": ("ssp585", "ScenarioMIP"),
    "piControl (pre-industrial control)": ("piControl", "CMIP"),
    "amip (atmosphere-only, 1979-2014)": ("amip", "CMIP"),
}


# ── Variables ────────────────────────────────────────────────────

_VARIABLES: list[tuple[str, str]] = [
    ("Near-surface air temperature", "tas"),
    ("Daily max near-surface temperature", "tasmax"),
    ("Daily min near-surface temperature", "tasmin"),
    ("Precipitation", "pr"),
    ("Sea level pressure", "psl"),
    ("Near-surface relative humidity", "hurs"),
    ("Near-surface specific humidity", "huss"),
    ("Near-surface wind speed", "sfcWind"),
    ("Surface downwelling shortwave radiation", "rsds"),
    ("Total cloud cover", "clt"),
    ("Sea surface temperature", "tos"),
    ("Evaporation incl. sublimation and transpiration", "evspsbl"),
]


# ── Frequency / table_id ────────────────────────────────────────

_TABLES: dict[str, str] = {
    "Monthly (Amon)": "Amon",
    "Daily (day)": "day",
    "Monthly ocean (Omon)": "Omon",
    "Fixed fields (fx)": "fx",
}


# ── Form ─────────────────────────────────────────────────────────

def render_mode_selector() -> None:
    """Render the mode radio outside the form so it triggers immediate reruns."""
    st.markdown(
        "Search the full CMIP6 archive on ESGF and download files directly. "
        "No special Python packages needed. ESGF hosts every model, every "
        "experiment, every ensemble member, not just the CDS subset."
    )

    st.radio(
        "Mode",
        ["Single model", "Ensemble members", "Multi-model comparison"],
        horizontal=True,
        key="esgf_mode",
        help=(
            "Single model: one file. Ensemble members: multiple realisations "
            "of one model (r1, r2, ...) to see internal variability. "
            "Multi-model: one file per model for cross-model comparison."
        ),
    )


def render_form() -> dict:
    mode = st.session_state.get("esgf_mode", "Single model")

    if mode == "Single model":
        return _single_form()
    if mode == "Ensemble members":
        return _ensemble_form()
    return _multi_form()


def _shared_fields() -> tuple[str, str, str, str]:
    """Render shared fields (experiment, variable, frequency, search node).

    Returns (experiment_id, variable_id, table_id, search_url).
    """
    # Experiment
    exp_label = st.selectbox(
        "Experiment",
        list(_EXPERIMENTS.keys()),
        key="esgf_exp",
        help=(
            "Historical uses observed forcings (1850-2014). SSP scenarios are "
            "future projections (2015-2100) with different emission pathways. "
            "piControl is the pre-industrial baseline with no forcing changes."
        ),
    )
    experiment_id, _activity_id = _EXPERIMENTS[exp_label]

    # Variable
    var_options = [f"{label} ({vid})" for label, vid in _VARIABLES]
    var_options.append("Custom (type below)")
    var_choice = st.selectbox(
        "Variable", var_options, key="esgf_var",
        help=(
            "Standard CMIP6/CMOR variable names. tas = temperature at surface, "
            "pr = precipitation, psl = sea level pressure. Temperature is in "
            "Kelvin, precipitation in kg m-2 s-1 (multiply by 86400 for mm/day)."
        ),
    )
    if var_choice.startswith("Custom"):
        variable_id = st.text_input(
            "CMIP6 variable ID", "tas",
            help="Full list at https://clipc-services.ceda.ac.uk/dreq/mipVars.html",
            key="esgf_custom_var",
        )
    else:
        idx = var_options.index(var_choice)
        variable_id = _VARIABLES[idx][1]

    # Table / frequency
    table_label = st.selectbox("Frequency", list(_TABLES.keys()), key="esgf_table")
    table_id = _TABLES[table_label]

    # Search node
    search_node = st.selectbox(
        "Search node",
        [
            "esgf-data.dkrz.de",
            "esgf-node.ipsl.upmc.fr",
            "esgf-index1.ceda.ac.uk",
        ],
        key="esgf_node",
        help="ESGF index node to query. DKRZ is the most reliable.",
    )
    search_url = f"https://{search_node}/esg-search/search"

    return experiment_id, variable_id, table_id, search_url


def _single_form() -> dict:
    st.caption(
        "Download one file from one model. CMIP6 data on ESGF is open "
        "access (CC BY 4.0), no registration required."
    )

    # Auto-sync ensemble member when the model changes
    if "esgf_model" in st.session_state and "esgf_member" in st.session_state:
        sid = _MODELS.get(st.session_state["esgf_model"])
        if sid and sid in _F2_MODELS and st.session_state["esgf_member"] == "r1i1p1f1":
            st.session_state["esgf_member"] = "r1i1p1f2"
        elif sid and sid not in _F2_MODELS and st.session_state["esgf_member"] == "r1i1p1f2":
            st.session_state["esgf_member"] = "r1i1p1f1"

    model_label = st.selectbox(
        "Model",
        list(_MODELS.keys()),
        key="esgf_model",
        help=(
            "Models marked 'uses f2' need variant_label r1i1p1f2. "
            "This is set automatically in the member field below."
        ),
    )
    source_id = _MODELS[model_label]

    experiment_id, variable_id, table_id, search_url = _shared_fields()

    default_member = _flagship_member(source_id)
    c1, c2 = st.columns(2)
    variant_label = c1.text_input(
        f"Ensemble member ({source_id} flagship: {default_member})",
        default_member,
        help=(
            "r<k>i<l>p<m>f<n> format. r = realisation (initial conditions), "
            "p = physics, f = forcing. Change r to r2, r3 for other members."
        ),
        key="esgf_member",
    )
    grid_label = c2.selectbox(
        "Grid",
        ["gn (native)", "gr (regridded)", "gr1 (alt regridded)"],
        key="esgf_grid",
        help="gn = native model grid, gr = regridded to regular lat/lon.",
    )

    output_dir, output_filename = output_dir_input(SLUG, key_prefix="esgf_output")

    return {
        "search_node": search_url,
        "source_id": source_id,
        "experiment_id": experiment_id,
        "variable_id": variable_id,
        "table_id": table_id,
        "variant_label": variant_label,
        "grid_label": grid_label.split(" ")[0],
        "output_dir": output_dir,
        "output_filename": output_filename,
    }


def _ensemble_form() -> dict:
    """Form for downloading multiple ensemble members of one model."""
    st.caption(
        "Download multiple realisations (r1, r2, r3, ...) of a single model "
        "to see the spread of internal climate variability. Each realisation "
        "starts from different initial conditions but uses the same physics "
        "and forcings. Models like CanESM5 have 50+ members."
    )

    model_label = st.selectbox(
        "Model",
        list(_MODELS.keys()),
        key="esgf_ens_model",
        help=(
            "Pick one model. CanESM5 has ~50 members, MPI-ESM1-2-LR has ~30, "
            "UKESM1-0-LL has ~19. Smaller ensembles (5-10) are common for "
            "most other models."
        ),
    )
    source_id = _MODELS[model_label]

    experiment_id, variable_id, table_id, search_url = _shared_fields()

    c1, c2 = st.columns(2)
    n_members = c1.number_input(
        "Number of members",
        min_value=2, max_value=50, value=5,
        key="esgf_ens_n_members",
        help=(
            "Downloads realisations r1 through rN. If a member does not "
            "exist on ESGF, it is silently skipped."
        ),
    )
    grid_label = c2.selectbox(
        "Grid",
        ["gn (native)", "gr (regridded)"],
        key="esgf_ens_grid",
    )

    output_dir, _output_filename = output_dir_input(SLUG, key_prefix="esgf_ens_output")

    return {
        "mode": "multi",
        "search_node": search_url,
        "source_ids": [source_id],
        "experiment_id": experiment_id,
        "variable_id": variable_id,
        "table_id": table_id,
        "n_members": n_members,
        "grid_label": grid_label.split(" ")[0],
        "output_dir": output_dir,
    }


def _multi_form() -> dict:
    st.caption(
        "Pick multiple models and/or ensemble members. One file per "
        "combination is downloaded (the first time-chunk, typically ~20 "
        "years). Results are concatenated along a model/member dimension "
        "for side-by-side comparison."
    )

    # Model multi-select
    model_labels = st.multiselect(
        "Models to compare",
        list(_MODELS.keys()),
        default=[
            "MPI-ESM1-2-LR (Germany, ~250 km)",
            "MPI-ESM1-2-HR (Germany, ~100 km, high-res)",
            "UKESM1-0-LL (UK NERC/Met Office, ~250 km, uses f2)",
        ],
        key="esgf_multi_models",
        help=(
            "Select 2 or more models. Each model downloads one file (~5-15 MB). "
            "During the ESGF-NG transition, the DKRZ node reliably indexes "
            "MPI-ESM1-2-LR, MPI-ESM1-2-HR, UKESM1-0-LL, IPSL-CM6A-LR, and "
            "CNRM-CM6-1. Other models may not be found. The script automatically "
            "tries both native (gn) and regridded (gr) grids."
        ),
    )
    source_ids = [_MODELS[lbl] for lbl in model_labels]

    experiment_id, variable_id, table_id, search_url = _shared_fields()

    c1, c2 = st.columns(2)
    n_members = c1.number_input(
        "Ensemble members per model",
        min_value=1, max_value=10, value=1,
        key="esgf_n_members",
        help=(
            "How many realisations (r1, r2, ...) to download per model. "
            "More members let you see internal climate variability within "
            "each model. Not all models have many members available."
        ),
    )
    grid_label = c2.selectbox(
        "Grid",
        ["gn (native)", "gr (regridded)"],
        key="esgf_multi_grid",
    )

    output_dir, _output_filename = output_dir_input(SLUG, key_prefix="esgf_multi_output")

    return {
        "mode": "multi",
        "search_node": search_url,
        "source_ids": source_ids,
        "experiment_id": experiment_id,
        "variable_id": variable_id,
        "table_id": table_id,
        "n_members": n_members,
        "grid_label": grid_label.split(" ")[0],
        "output_dir": output_dir,
    }
