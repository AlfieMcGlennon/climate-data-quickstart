"""Download ERA5 single-level reanalysis data from the Copernicus CDS.

Edit the USER CONFIGURATION block below and run directly:

    python scripts/era5_single_levels_download.py

The defaults pull a single hour of 2 metre temperature over the UK as a minimal
test. Larger requests are queued server-side and may take minutes to hours.

Documentation: docs/era5-single-levels/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

# Make ``common`` importable when running this script from the repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.credentials import check_cds_credentials  # noqa: E402


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# CDS API variable names. See docs/era5-single-levels/variables.md for the
# full list, or the CDS download form for the authoritative catalogue.
VARIABLES: list[str] = ["2m_temperature"]

# Years, months, days, and hours to request. Each list can be expanded.
YEARS: list[str] = ["2023"]
MONTHS: list[str] = ["07"]
DAYS: list[str] = ["01"]
HOURS: list[str] = ["12:00"]

# Bounding box as [north, west, south, east] in decimal degrees.
# Default: UK.
BBOX: list[float] = [55, -8, 49, 2]

# Output format. "grib" is faster and the native archive format. "netcdf"
# is more convenient for xarray workflows but is marked experimental by
# the CDS.
DATA_FORMAT: str = "netcdf"

# "unarchived" returns a single file. "zip" returns a zip archive.
DOWNLOAD_FORMAT: str = "unarchived"

# Where to save the output, relative to the repo root.
OUTPUT_DIR: str = "./data/era5-single-levels"
OUTPUT_FILENAME: str = "era5_single_levels_test.nc"
# ==================================================================


def build_request(
    variables: Iterable[str],
    years: Iterable[str],
    months: Iterable[str],
    days: Iterable[str],
    hours: Iterable[str],
    bbox: list[float],
    data_format: str,
    download_format: str,
) -> dict:
    """Build the CDS API request dictionary for ERA5 single levels.

    Args:
        variables: CDS API variable names (snake_case).
        years: Years as zero-padded strings (e.g., ``["2023"]``).
        months: Months as zero-padded strings (e.g., ``["07"]``).
        days: Days as zero-padded strings (e.g., ``["01"]``).
        hours: Hours as ``"HH:00"`` strings (e.g., ``["12:00"]``).
        bbox: Bounding box as ``[north, west, south, east]``.
        data_format: ``"netcdf"`` or ``"grib"``.
        download_format: ``"unarchived"`` or ``"zip"``.

    Returns:
        A dict suitable for ``cdsapi.Client().retrieve()``.
    """
    return {
        "product_type": ["reanalysis"],
        "variable": list(variables),
        "year": list(years),
        "month": list(months),
        "day": list(days),
        "time": list(hours),
        "data_format": data_format,
        "download_format": download_format,
        "area": bbox,
    }


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
    """Download an ERA5 single-levels slice to disk.

    The CDS queues requests server-side. Small single-day pulls typically
    complete in minutes; larger requests can take hours.

    Args:
        variables: CDS API variable names.
        years: Years as strings.
        months: Months as zero-padded strings.
        days: Days as zero-padded strings.
        hours: Hours as ``"HH:00"``.
        bbox: ``[north, west, south, east]`` in degrees.
        data_format: Output format.
        download_format: Packaging.
        output_dir: Directory to write to, relative or absolute.
        output_filename: Output filename.

    Returns:
        The path to the downloaded file.

    Raises:
        FileNotFoundError: If ``~/.cdsapirc`` is missing. The message includes
            the registration URL.
    """
    # Fail fast with a clear message if credentials are missing
    check_cds_credentials()

    import cdsapi

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    request = build_request(
        variables=variables,
        years=years,
        months=months,
        days=days,
        hours=hours,
        bbox=bbox,
        data_format=data_format,
        download_format=download_format,
    )

    client = cdsapi.Client()
    client.retrieve("reanalysis-era5-single-levels", request).download(str(output_path))

    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
