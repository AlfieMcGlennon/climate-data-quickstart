"""Landing page for the climate data quickstart app."""

from __future__ import annotations

import streamlit as st


# ── Dataset cards: (slug, name, one-liner, coverage, access) ──────

_ERA5_CARDS = [
    ("era5-single-levels", "ERA5 single levels", "Surface and atmospheric fields, hourly from 1940", "Global, 0.25 deg", "CDS API"),
    ("era5-pressure-levels", "ERA5 pressure levels", "Upper-air fields on 37 pressure levels", "Global, 0.25 deg", "CDS API"),
    ("era5-land", "ERA5-Land", "Land surface at higher resolution", "Global land, 0.1 deg", "CDS API"),
    ("era5-daily-stats", "ERA5 daily statistics", "Pre-computed daily mean, max, min", "Global, 0.25 deg", "CDS API"),
]

_STREAMING_CARDS = [
    ("earth-data-hub", "Earth Data Hub", "Stream ERA5 lazily via Zarr, no queue", "Global, 0.25 deg", "Zarr"),
    ("arco-era5", "ARCO-ERA5", "ERA5 on Google Cloud, no API key needed", "Global, 0.25 deg", "Zarr"),
    ("edh-explorer", "EDH catalogue explorer", "Browse ERA5 + CMIP6 models from EDH", "Global", "Zarr"),
]

_MODELS_CARDS = [
    ("cmip6", "CMIP6 (CDS)", "Curated subset of models via Copernicus", "Global", "CDS API"),
    ("esgf-cmip6", "ESGF CMIP6", "Full archive, every model and experiment", "Global", "Direct HTTP"),
    ("c3s-seasonal", "C3S seasonal", "Multi-system forecasts, up to 6 months ahead", "Global, 1 deg", "CDS API"),
]

_OBS_CARDS = [
    ("hadcet", "HadCET", "Central England temperature, 1659 to present", "Single region", "Direct HTTP"),
    ("hadcrut5", "HadCRUT5", "Global temperature anomalies, 1850 to present", "Global, 5 deg", "Direct HTTP"),
    ("ghcnd", "GHCNd", "100,000+ weather stations, daily records", "Station network", "Direct HTTP"),
    ("e-obs", "E-OBS", "European gridded daily observations", "Europe, 0.1 deg", "CDS API"),
    ("chirps", "CHIRPS", "Satellite-station rainfall blend, tropics", "50S-50N, 0.05 deg", "Direct HTTP"),
]

_FORECAST_CARDS = [
    ("ecmwf-open-data", "ECMWF Open Data", "Real-time IFS/AIFS, four times daily", "Global, 0.25 deg", "Direct HTTP"),
    ("glofas", "GloFAS", "Global river discharge reanalysis", "Global, 0.05 deg", "EWDS API"),
]

_SECTIONS = [
    (":material/public: ERA5 reanalysis", _ERA5_CARDS),
    (":material/cloud: Cloud streaming", _STREAMING_CARDS),
    (":material/timeline: Climate projections", _MODELS_CARDS),
    (":material/thermostat: Observations", _OBS_CARDS),
    (":material/water_drop: Forecasts and hydrology", _FORECAST_CARDS),
]

_ACCESS_BADGE_COLOR = {
    "CDS API": "blue",
    "Direct HTTP": "green",
    "Zarr": "violet",
    "EWDS API": "orange",
}

_SLUG_TO_CATEGORY: dict[str, str] = {}


def _ensure_slug_map() -> None:
    """Build slug->category lookup on first use (avoids circular import)."""
    if _SLUG_TO_CATEGORY:
        return
    from app.dataset_pages import CATEGORIES
    for cat, (_icon, slugs) in CATEGORIES.items():
        for s in slugs:
            _SLUG_TO_CATEGORY[s] = cat


# ──────────────────────────────────────────────────────────────────────
# Dataset finder
# ──────────────────────────────────────────────────────────────────────

_FINDER_ENTRIES = [
    {
        "keywords": ["temperature", "temp", "t2m", "heat", "warming", "hot", "cold"],
        "dataset": "ERA5 single levels",
        "slug": "era5-single-levels",
        "variables": "2m_temperature, 2m_dewpoint_temperature",
        "note": "Hourly gridded reanalysis. For long-term trends see HadCRUT5.",
    },
    {
        "keywords": ["temperature", "temp", "warming", "anomaly", "anomalies", "climate change"],
        "dataset": "HadCRUT5",
        "slug": "hadcrut5",
        "variables": "tas_mean (temperature anomaly)",
        "note": "Monthly 5-deg grid, 1850-present. Best for long-term global warming trends.",
    },
    {
        "keywords": ["temperature", "temp", "england", "uk", "central england", "cet", "historical"],
        "dataset": "HadCET",
        "slug": "hadcet",
        "variables": "mean_temp, max_temp, min_temp",
        "note": "Longest instrumental temperature record in the world (1659-present). Central England only.",
    },
    {
        "keywords": ["wind", "gust", "u10", "v10", "wind speed", "wind direction"],
        "dataset": "ERA5 single levels",
        "slug": "era5-single-levels",
        "variables": "10m_u_component_of_wind, 10m_v_component_of_wind",
        "note": "Combine u and v to get wind speed: sqrt(u10² + v10²).",
    },
    {
        "keywords": ["wind", "upper", "jet", "jet stream", "upper level"],
        "dataset": "ERA5 pressure levels",
        "slug": "era5-pressure-levels",
        "variables": "u_component_of_wind, v_component_of_wind (at 250 hPa for jet stream)",
        "note": "Select 250 hPa for jet stream analysis, 850 hPa for low-level wind.",
    },
    {
        "keywords": ["rain", "rainfall", "precipitation", "precip", "tp", "wet", "drought", "dry"],
        "dataset": "ERA5 single levels",
        "slug": "era5-single-levels",
        "variables": "total_precipitation",
        "note": "Cumulative per hour. Multiply by 1000 for mm. Global coverage.",
    },
    {
        "keywords": ["rain", "rainfall", "precipitation", "tropical", "africa", "monsoon", "chirps"],
        "dataset": "CHIRPS",
        "slug": "chirps",
        "variables": "precip (daily rainfall estimate, mm/day)",
        "note": "Satellite + station blend. 50S-50N only. Best for tropical/subtropical rainfall.",
    },
    {
        "keywords": ["rain", "rainfall", "precipitation", "europe", "daily"],
        "dataset": "E-OBS",
        "slug": "e-obs",
        "variables": "rr (daily precipitation sum)",
        "note": "Station-interpolated European gridded data. Also has temperature, pressure.",
    },
    {
        "keywords": ["flood", "river", "discharge", "runoff", "streamflow", "glofas", "hydrology"],
        "dataset": "GloFAS",
        "slug": "glofas",
        "variables": "dis24 (daily river discharge, m3/s)",
        "note": "Global river discharge reanalysis. Good for flood risk and hydrological analysis.",
    },
    {
        "keywords": ["pressure", "msl", "slp", "sea level pressure", "synoptic", "cyclone", "storm"],
        "dataset": "ERA5 single levels",
        "slug": "era5-single-levels",
        "variables": "mean_sea_level_pressure, surface_pressure",
        "note": "For upper-level geopotential, use ERA5 pressure levels instead.",
    },
    {
        "keywords": ["cloud", "clouds", "radiation", "solar", "sunshine", "shortwave"],
        "dataset": "ERA5 single levels",
        "slug": "era5-single-levels",
        "variables": "total_cloud_cover, surface_solar_radiation_downwards",
        "note": "Cloud cover is 0-1 fraction. Radiation is cumulative J/m2 per hour.",
    },
    {
        "keywords": ["sst", "sea surface", "ocean", "ocean temperature"],
        "dataset": "ERA5 single levels",
        "slug": "era5-single-levels",
        "variables": "sea_surface_temperature",
        "note": "ERA5 SST is prescribed from HadISST/OSTIA, not a model forecast.",
    },
    {
        "keywords": ["soil", "soil moisture", "land", "evaporation", "vegetation", "snow"],
        "dataset": "ERA5-Land",
        "slug": "era5-land",
        "variables": "volumetric_soil_water_layer_1, snow_depth, evaporation",
        "note": "Higher resolution (0.1 deg) land-only reanalysis. No ocean points.",
    },
    {
        "keywords": ["station", "stations", "point", "weather station", "observation", "obs"],
        "dataset": "GHCNd",
        "slug": "ghcnd",
        "variables": "TMAX, TMIN, PRCP, SNOW, SNWD",
        "note": "Individual weather station daily records. 100,000+ stations worldwide.",
    },
    {
        "keywords": ["climate model", "projection", "future", "scenario", "ssp", "rcp", "cmip"],
        "dataset": "CMIP6",
        "slug": "cmip6",
        "variables": "Model-dependent (tas, pr, psl common across models)",
        "note": "Multi-model climate projections. Historical + SSP scenarios to 2100.",
    },
    {
        "keywords": ["europe", "european", "eu"],
        "dataset": "E-OBS",
        "slug": "e-obs",
        "variables": "tg (mean temp), tn (min), tx (max), rr (precip), pp (pressure)",
        "note": "European-only gridded observations from station networks. Daily, 1950-present.",
    },
    {
        "keywords": ["streaming", "zarr", "lazy", "cloud", "xarray", "no download"],
        "dataset": "Earth Data Hub",
        "slug": "earth-data-hub",
        "variables": "Same as ERA5 (t2m, u10, v10, tp, etc.) via GRIB short names",
        "note": "Stream data lazily with xarray. No queue, no file download needed. Subset on the fly.",
    },
    {
        "keywords": ["daily statistics", "daily mean", "daily max", "daily min", "diurnal"],
        "dataset": "ERA5 daily statistics",
        "slug": "era5-daily-stats",
        "variables": "Any ERA5 single-level variable, aggregated to daily mean/max/min",
        "note": "Pre-computed daily stats from hourly ERA5. Saves you doing the aggregation yourself.",
    },
    {
        "keywords": ["forecast", "weather forecast", "ifs", "next week", "tomorrow", "operational", "nwp"],
        "dataset": "ECMWF Open Data",
        "slug": "ecmwf-open-data",
        "variables": "2t, 10u, 10v, msl, tp (GRIB short names)",
        "note": "Real-time IFS/AIFS forecast fields. No registration, no queue. Updated four times daily.",
    },
    {
        "keywords": ["seasonal", "season", "monsoon", "enso", "el nino", "la nina", "outlook", "months ahead", "s2s"],
        "dataset": "C3S seasonal",
        "slug": "c3s-seasonal",
        "variables": "2m_temperature, total_precipitation, sea_surface_temperature",
        "note": "Multi-system seasonal forecasts from nine centres, up to 6 months ahead. CDS API.",
    },
    {
        "keywords": ["cloud", "zarr", "google", "no download", "lazy", "streaming", "free", "no auth", "no queue", "arco"],
        "dataset": "ARCO-ERA5",
        "slug": "arco-era5",
        "variables": "Same as ERA5 (2m_temperature, msl, tp, etc.) via Zarr variable names",
        "note": "Cloud-native ERA5 on Google Cloud Storage. No API key, no queue. Stream with xarray.",
    },
    {
        "keywords": ["edh", "catalogue", "explorer", "cmip6", "model", "scenario", "ssp", "projection", "streaming", "zarr"],
        "dataset": "EDH catalogue explorer",
        "slug": "edh-explorer",
        "variables": "ERA5 (t2m, tp, msl, etc.) + CMIP6 (tas, pr, psl, etc.)",
        "note": "Browse the full EDH catalogue: 6 CMIP6 models across SSP scenarios, ERA5 variants, all streaming.",
    },
    {
        "keywords": ["esgf", "cmip6", "cmip", "model", "ensemble", "multi-model", "scenario", "ssp", "projection", "archive", "full"],
        "dataset": "ESGF CMIP6",
        "slug": "esgf-cmip6",
        "variables": "tas, tasmax, tasmin, pr, psl, hurs, huss, sfcWind, rsds, clt, tos",
        "note": "Full CMIP6 archive via ESGF: 20+ models, all ensemble members, all experiments. Direct HTTP download, no auth.",
    },
]


def _search_datasets(query: str) -> list[dict]:
    """Return matching finder entries for a query string."""
    if not query.strip():
        return []
    terms = query.lower().split()
    results = []
    for entry in _FINDER_ENTRIES:
        score = sum(
            1 for term in terms
            if any(term in kw for kw in entry["keywords"])
        )
        if score > 0:
            results.append((score, entry))
    results.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in results]


def _navigate_to(slug: str) -> None:
    """Callback: switch to Download mode for a specific dataset."""
    _ensure_slug_map()
    category = _SLUG_TO_CATEGORY.get(slug)
    if category:
        st.session_state["app_mode"] = "Download"
        st.session_state["dataset_category"] = category
        st.session_state["dataset_radio"] = slug


def _render_card(
    slug: str, name: str, description: str, coverage: str, access: str,
) -> None:
    """Render a single dataset card with badge and navigation button."""
    badge_color = _ACCESS_BADGE_COLOR.get(access, "gray")
    with st.container(border=True):
        st.markdown(f"**{name}**")
        st.caption(description)
        col_cov, col_badge = st.columns([3, 1])
        with col_cov:
            st.caption(coverage)
        with col_badge:
            st.badge(access, color=badge_color)
        st.button(
            ":material/arrow_forward: Open",
            key=f"card_{slug}",
            use_container_width=True,
            type="secondary",
            on_click=_navigate_to,
            args=(slug,),
        )


def render_page() -> None:
    """Render the landing/overview page."""
    st.title(":material/cloud_download: Climate data quickstart")

    total = sum(len(cards) for _, cards in _SECTIONS)

    st.markdown(
        f"A local toolkit for accessing **{total} climate and weather datasets** "
        "from the Copernicus Climate Data Store, ECMWF, ESGF, and other major "
        "providers. It covers ERA5 reanalysis (surface, pressure levels, land, "
        "daily statistics), cloud-native streaming via Zarr, CMIP6 climate "
        "projections, station and satellite observations, real-time forecasts, "
        "and river discharge data."
    )
    st.markdown(
        "Everything runs locally on your machine. The app never reads or stores "
        "your API keys - it uses the same credential files as the command-line "
        "scripts (`~/.cdsapirc`, `~/.netrc`). You configure a request, download "
        "the data, and explore it interactively with maps and time series, "
        "all without writing any code."
    )

    # ── Quick-start steps ──────────────────────────────────────────
    st.subheader(":material/rocket_launch: Getting started")
    qs1, qs2, qs3 = st.columns(3)
    with qs1:
        with st.container(border=True):
            st.markdown(":material/key: **1. Set up credentials**")
            st.caption(
                "Most datasets need a free API key from Copernicus or another "
                "provider. Click **Download** in the sidebar to see which "
                "credentials you have and which are missing. "
                "Some datasets (HadCET, CHIRPS, ARCO-ERA5, ESGF CMIP6) "
                "need no registration at all."
            )
    with qs2:
        with st.container(border=True):
            st.markdown(":material/download: **2. Pick and download**")
            st.caption(
                "Browse the dataset cards below, or type a keyword in the "
                "search box (temperature, wind, rain, Europe, forecast). "
                "Each form lets you choose variables, date range, region, "
                "and output format. CDS requests queue server-side and can "
                "take a few minutes; direct downloads are usually immediate."
            )
    with qs3:
        with st.container(border=True):
            st.markdown(":material/visibility: **3. Explore your data**")
            st.caption(
                "After downloading, the built-in explorer opens your file "
                "and lets you scrub through time steps, switch variables, "
                "and view spatial maps or time series. You can also open any "
                "NetCDF, GRIB, or CSV file from the **Explore data** tab at "
                "any time, including files you downloaded in a previous session."
            )

    # ── Dataset finder ──────────────────────────────────────────────
    st.text_input(
        ":material/search: Find a dataset",
        placeholder="Search by topic: temperature, wind, precipitation, flood, model, Europe...",
        key="dataset_search",
        label_visibility="collapsed",
    )
    query = st.session_state.get("dataset_search", "")

    results = _search_datasets(query)
    if query and not results:
        st.caption(
            "No matches. Try broader terms: temperature, wind, rain, "
            "flood, pressure, cloud, ocean, station, model."
        )
    elif results:
        _ensure_slug_map()
        for entry in results[:4]:
            slug = entry.get("slug", "")
            with st.container(border=True):
                st.markdown(f"**{entry['dataset']}**")
                st.caption(f"`{entry['variables']}`")
                st.caption(entry["note"])
                if slug and slug in _SLUG_TO_CATEGORY:
                    st.button(
                        "Open",
                        key=f"search_{slug}_{entry['dataset']}",
                        type="tertiary",
                        on_click=_navigate_to,
                        args=(slug,),
                    )

    # ── Dataset cards by category ──────────────────────────────────
    _ensure_slug_map()
    for section_title, cards in _SECTIONS:
        st.subheader(section_title)
        cols_per_row = 3 if len(cards) >= 3 else 2
        for i in range(0, len(cards), cols_per_row):
            row = cards[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            for j, (slug, name, desc, coverage, access) in enumerate(row):
                with cols[j]:
                    _render_card(slug, name, desc, coverage, access)

    st.caption(
        "See `docs/` in the repo for full documentation on each dataset."
    )
