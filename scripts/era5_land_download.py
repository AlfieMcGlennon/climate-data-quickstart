"""Download ERA5-Land hourly reanalysis data from the Copernicus CDS.

Edit the USER CONFIGURATION block and run:

    python scripts/era5_land_download.py

The defaults pull one hour of 2 metre temperature over the UK as a minimal
test.

Documentation: docs/era5-land/README.md
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
VARIABLES: list[str] = ["2m_temperature"]

YEARS: list[str] = ["2023"]
MONTHS: list[str] = ["07"]
DAYS: list[str] = ["01"]
HOURS: list[str] = ["12:00"]

# Bounding box as [north, west, south, east].
BBOX: list[float] = [55, -8, 49, 2]  # UK

DATA_FORMAT: str = "netcdf"
DOWNLOAD_FORMAT: str = "unarchived"

OUTPUT_DIR: str = "./data/era5-land"
OUTPUT_FILENAME: str = "era5_land_test.nc"
# ==================================================================


def download(
    variables: Iterable[str] = VARIABLES,
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
    """Download an ERA5-Land slice to disk.

    ERA5-Land has no ``product_type`` field (it is reanalysis only) and
    no ``expver`` stream distinction in the main CDS endpoint, so requests
    are slightly simpler than ERA5 single levels.

    Args:
        variables: CDS API variable names from the ERA5-Land catalogue.
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
        "variable": list(variables),
        "year": list(years),
        "month": list(months),
        "day": list(days),
        "time": list(hours),
        "data_format": data_format,
        "download_format": download_format,
        "area": bbox,
    }

    client = cdsapi.Client()
    client.retrieve("reanalysis-era5-land", request).download(str(output_path))

    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
