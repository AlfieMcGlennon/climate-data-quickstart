"""One module per dataset, each exposing a ``render_form()`` function.

``render_form()`` returns a dict of keyword arguments ready to pass to
the matching ``scripts/*_download.download()`` function via
``app.runner.run``.
"""

from . import (
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
)


# Dataset registry: slug -> (human name, module)
DATASETS: dict[str, tuple[str, object]] = {
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
}
