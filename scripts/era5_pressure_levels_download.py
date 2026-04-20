"""Download ERA5 pressure-level reanalysis data from the Copernicus CDS.

Edit the USER CONFIGURATION block and run:

    python scripts/era5_pressure_levels_download.py

The defaults pull one hour of 500 hPa temperature over the UK as a minimal
test.

Documentation: docs/era5-pressure-levels/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.credentials import check_cds_credentials  # noqa: E402


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# CDS API variable names. See docs/era5-pressure-levels/variables.md for
# the full list of 16 pressure-level variables.
VARIABLES: list[str] = ["temperature"]

# Pressure levels in hPa. Valid values come from the set of 37 levels
# listed in the docs. Levels are passed as strings to the CDS.
PRESSURE_LEVELS: list[str] = ["500"]

YEARS: list[str] = ["2023"]
MONTHS: list[str] = ["07"]
DAYS: list[str] = ["01"]
HOURS: list[str] = ["12:00"]

# Bounding box as [north, west, south, east].
BBOX: list[float] = [55, -8, 49, 2]  # UK

DATA_FORMAT: str = "netcdf"
DOWNLOAD_FORMAT: str = "unarchived"

OUTPUT_DIR: str = "./data/era5-pressure-levels"
OUTPUT_FILENAME: str = "era5_pressure_levels_test.nc"
# ==================================================================


def download(
    variables: Iterable[str] = VARIABLES,
    pressure_levels: Iterable[str] = PRESSURE_LEVELS,
    years: Iterable[str] = YEARS,
    months: Iterable[str] = MONTHS,
    days: Iterable[str] = DAYS,
    hours: Iterable[str] = HOURS,
    bbox: list[float] = BBOX,
    data_format: str = DATA_FORMAT,
    download_format: str = DOWNLOAD_FORMAT,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download an ERA5 pressure-levels slice to disk.

    The request-size cap multiplies by the number of pressure levels, so
    multi-level requests fill the cap faster than single-levels requests.

    Args:
        variables: CDS API variable names from the 16-entry pressure-levels list.
        pressure_levels: List of pressure levels in hPa as strings.
        years: Years as strings.
        months: Months as zero-padded strings.
        days: Days as zero-padded strings.
        hours: Hours as ``"HH:00"``.
        bbox: ``[north, west, south, east]`` in degrees.
        data_format: ``"netcdf"`` or ``"grib"``.
        download_format: ``"unarchived"`` or ``"zip"``.
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        The path to the downloaded file.

    Raises:
        FileNotFoundError: If ``~/.cdsapirc`` is missing.
    """
    check_cds_credentials()

    import cdsapi

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    request = {
        "product_type": ["reanalysis"],
        "variable": list(variables),
        "pressure_level": list(pressure_levels),
        "year": list(years),
        "month": list(months),
        "day": list(days),
        "time": list(hours),
        "data_format": data_format,
        "download_format": download_format,
        "area": bbox,
    }

    client = cdsapi.Client()
    client.retrieve("reanalysis-era5-pressure-levels", request).download(str(output_path))

    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
