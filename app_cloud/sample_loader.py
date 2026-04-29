"""Resolve cached sample files for credentialed datasets.

The cloud app cannot run live API calls that need user credentials, so
visualisation modes load a small pre-cached file instead. Samples live
in ``cloud_samples/`` at the repo root and are committed alongside the
code. Provenance for each file is recorded in ``cloud_samples/README.md``.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SAMPLES_DIR = _REPO_ROOT / "cloud_samples"


# Map slug -> sample filename within cloud_samples/.
# Datasets not in this map have no sample yet; the UI handles that
# gracefully ("cached sample coming soon, here's the live download code").
SAMPLE_FILES: dict[str, str] = {
    "era5-single-levels": "era5_single_levels_sample.nc",
    "era5-pressure-levels": "era5_pressure_levels_sample.nc",
    "era5-land": "era5_land_sample.nc",
    "era5-daily-stats": "era5_daily_stats_sample.nc",
    "cmip6": "cmip6_sample.nc",
    "e-obs": "e_obs_sample.nc",
    "c3s-seasonal": "c3s_seasonal_sample.nc",
    "earth-data-hub": "edh_sample.nc",
    "edh-explorer": "edh_sample.nc",
    "glofas": "glofas_sample.grib",
    "ukcp18": "ukcp18_sample.nc",
    "gpw-population": "gpw_sample.tif",
}


def load_sample(slug: str) -> Path | None:
    """Return the path to the cached sample for a dataset, or None.

    Returns None when the sample is not yet committed for this dataset.
    Callers should fall back to a "no sample available" message and only
    show the code snippet in that case.
    """
    filename = SAMPLE_FILES.get(slug)
    if filename is None:
        return None
    path = _SAMPLES_DIR / filename
    if not path.exists():
        return None
    return path


def has_sample(slug: str) -> bool:
    """True if a cached sample is committed for this dataset."""
    return load_sample(slug) is not None
