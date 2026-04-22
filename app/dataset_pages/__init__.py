"""One module per dataset, each exposing a ``render_form()`` function.

``render_form()`` returns a dict of keyword arguments ready to pass to
the matching ``scripts/*_download.download()`` function via
``app.runner.run``.
"""

from . import (
    home,
    explore,
    era5_single_levels,
    era5_pressure_levels,
    era5_land,
    era5_daily_stats,
    earth_data_hub,
    hadcet,
    hadcrut5,
    cmip6,
    glofas,
    ghcnd,
    e_obs,
    chirps,
    ecmwf_open_data,
    c3s_seasonal,
    arco_era5,
    edh_explorer,
    esgf_cmip6,
    gpw_population,
    ukcp18,
)


# Dataset registry: slug -> (human name, module)
# "home" is the landing page, handled specially in main.py.
DATASETS: dict[str, tuple[str, object]] = {
    "home": ("Overview", home),
    "era5-single-levels": ("ERA5 single levels", era5_single_levels),
    "era5-pressure-levels": ("ERA5 pressure levels", era5_pressure_levels),
    "era5-land": ("ERA5-Land", era5_land),
    "era5-daily-stats": ("ERA5 daily statistics", era5_daily_stats),
    "earth-data-hub": ("Earth Data Hub", earth_data_hub),
    "hadcet": ("HadCET", hadcet),
    "hadcrut5": ("HadCRUT5", hadcrut5),
    "cmip6": ("CMIP6", cmip6),
    "glofas": ("GloFAS historical", glofas),
    "ghcnd": ("GHCNd", ghcnd),
    "e-obs": ("E-OBS", e_obs),
    "chirps": ("CHIRPS", chirps),
    "ecmwf-open-data": ("ECMWF Open Data", ecmwf_open_data),
    "c3s-seasonal": ("C3S seasonal", c3s_seasonal),
    "arco-era5": ("ARCO-ERA5", arco_era5),
    "edh-explorer": ("EDH catalogue explorer", edh_explorer),
    "esgf-cmip6": ("ESGF CMIP6 (full archive)", esgf_cmip6),
    "gpw-population": ("GPWv4 population", gpw_population),
    "ukcp18": ("UKCP18", ukcp18),
}


# One-line descriptions shown under each dataset title
DATASET_INFO: dict[str, str] = {
    "era5-single-levels": (
        "Global atmospheric reanalysis at 0.25 deg, hourly from 1940. "
        "The workhorse dataset for most climate analysis."
    ),
    "era5-pressure-levels": (
        "ERA5 on pressure levels (1000 to 1 hPa). "
        "For upper-air analysis, jet streams, vertical profiles."
    ),
    "era5-land": (
        "Higher-resolution (0.1 deg) land-only reanalysis. "
        "Soil moisture, snow depth, evaporation."
    ),
    "era5-daily-stats": (
        "Pre-computed daily mean, max, and min from hourly ERA5. "
        "Saves you doing the aggregation yourself."
    ),
    "earth-data-hub": (
        "Stream ERA5 data lazily via Zarr. "
        "No queue, no file download, subset on the fly."
    ),
    "hadcet": (
        "The longest instrumental temperature record in the world, "
        "1659 to present. Central England only."
    ),
    "hadcrut5": (
        "Global temperature anomalies on a 5-degree grid, 1850 to present. "
        "The standard reference for long-term warming."
    ),
    "cmip6": (
        "Climate model projections via the Copernicus CDS. "
        "Curated subset of models and scenarios."
    ),
    "glofas": (
        "Global river discharge reanalysis at 0.05 deg. "
        "For flood risk and hydrological analysis."
    ),
    "ghcnd": (
        "Daily weather station records from 100,000+ stations worldwide. "
        "Temperature, precipitation, snow."
    ),
    "e-obs": (
        "European daily gridded observations from station networks. "
        "Temperature, precipitation, pressure."
    ),
    "chirps": (
        "Satellite-station blend of daily rainfall, 50S to 50N. "
        "Best for tropical and subtropical regions."
    ),
    "ecmwf-open-data": (
        "Real-time IFS and AIFS forecast fields. "
        "Updated four times daily, no registration needed."
    ),
    "c3s-seasonal": (
        "Multi-system seasonal forecasts from nine centres, "
        "up to 6 months ahead."
    ),
    "arco-era5": (
        "Cloud-native ERA5 on Google Cloud Storage. "
        "No API key, no queue, stream with xarray."
    ),
    "edh-explorer": (
        "Browse the full Earth Data Hub catalogue. "
        "ERA5 variants and 6 CMIP6 models, all streaming."
    ),
    "esgf-cmip6": (
        "Full CMIP6 archive via ESGF. Every model, "
        "every experiment, every ensemble member."
    ),
    "gpw-population": (
        "Global gridded population density from census data. "
        "Overlay on climate hazards to estimate exposed populations."
    ),
    "ukcp18": (
        "UK climate projections at 12 km resolution. "
        "Temperature, precipitation, wind under RCP8.5 to 2080."
    ),
}


# Sidebar categories: label -> (icon, list of slugs)
# Order matters: first category is the default selection.
CATEGORIES: dict[str, tuple[str, list[str]]] = {
    "ERA5": (
        ":material/public:",
        ["era5-single-levels", "era5-pressure-levels", "era5-land", "era5-daily-stats"],
    ),
    "Streaming": (
        ":material/cloud:",
        ["earth-data-hub", "arco-era5", "edh-explorer"],
    ),
    "Models": (
        ":material/timeline:",
        ["cmip6", "esgf-cmip6", "c3s-seasonal", "ukcp18"],
    ),
    "Observations": (
        ":material/thermostat:",
        ["hadcet", "hadcrut5", "ghcnd", "e-obs", "chirps", "gpw-population"],
    ),
    "Forecast": (
        ":material/water_drop:",
        ["ecmwf-open-data", "glofas"],
    ),
}
