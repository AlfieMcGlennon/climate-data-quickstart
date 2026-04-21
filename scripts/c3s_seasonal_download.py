"""Download C3S seasonal forecast data from the Copernicus CDS.

Edit the USER CONFIGURATION block below and run directly:

    python scripts/c3s_seasonal_download.py

The defaults pull ECMWF system 51 monthly-mean 2 metre temperature for a
January 2024 initialisation, all six lead times, over a European region.
Output is GRIB format (recommended for this dataset).

Documentation: docs/c3s-seasonal/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make ``common`` importable when running this script from the repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.credentials import check_cds_credentials  # noqa: E402


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# CDS API variable name. See the CDS dataset page for the full catalogue:
# https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels
VARIABLE: str = "2m_temperature"

# Originating centre and system version. System numbers are centre-specific
# and change when centres upgrade their models.
ORIGINATING_CENTRE: str = "ecmwf"
SYSTEM: str = "51"

# Product type: "monthly_mean" gives one value per ensemble member per month.
PRODUCT_TYPE: str = "monthly_mean"

# Initialisation date. Seasonal forecasts are issued monthly.
YEAR: str = "2024"
MONTH: str = "01"

# Lead times in months ahead (1 = first full calendar month after init).
LEADTIME_MONTHS: list[str] = ["1", "2", "3", "4", "5", "6"]

# Bounding box as [north, west, south, east] in decimal degrees.
# Default: Europe (covers UK with context).
AREA: list[float] = [72, -12, 35, 30]

# GRIB is strongly recommended. NetCDF is experimental and unreliable
# for this dataset.
FORMAT: str = "grib"

# Where to save the output, relative to the repo root.
OUTPUT_DIR: str = "./data/c3s-seasonal"
OUTPUT_FILENAME: str = "c3s_seasonal_test.grib"
# ==================================================================


def build_request(
    variable: str,
    originating_centre: str,
    system: str,
    product_type: str,
    year: str,
    month: str,
    leadtime_months: list[str],
    area: list[float],
    fmt: str,
) -> dict:
    """Build the CDS API request dictionary for C3S seasonal monthly data.

    Args:
        variable: CDS API variable name (e.g., ``"2m_temperature"``).
        originating_centre: Centre identifier (e.g., ``"ecmwf"``).
        system: System version number (e.g., ``"51"``).
        product_type: ``"monthly_mean"`` or ``"ensemble_mean"``.
        year: Initialisation year as a string (e.g., ``"2024"``).
        month: Initialisation month as a zero-padded string (e.g., ``"01"``).
        leadtime_months: Lead times as strings (e.g., ``["1", "2", "3"]``).
        area: Bounding box as ``[north, west, south, east]``.
        fmt: Output format, ``"grib"`` recommended.

    Returns:
        A dict suitable for ``cdsapi.Client().retrieve()``.
    """
    return {
        "format": fmt,
        "originating_centre": originating_centre,
        "system": system,
        "variable": variable,
        "product_type": product_type,
        "year": year,
        "month": month,
        "leadtime_month": leadtime_months,
        "area": area,
    }


def download(
    variable: str = VARIABLE,
    originating_centre: str = ORIGINATING_CENTRE,
    system: str = SYSTEM,
    product_type: str = PRODUCT_TYPE,
    year: str = YEAR,
    month: str = MONTH,
    leadtime_months: list[str] = LEADTIME_MONTHS,
    area: list[float] = AREA,
    fmt: str = FORMAT,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download a C3S seasonal forecast slice to disk.

    The CDS queues requests server-side. Seasonal forecast data is served
    from tape archive and can be slower than ERA5 requests.

    Args:
        variable: CDS API variable name.
        originating_centre: Centre identifier.
        system: System version number.
        product_type: Product type string.
        year: Initialisation year.
        month: Initialisation month (zero-padded).
        leadtime_months: Lead time months as strings.
        area: ``[north, west, south, east]`` in degrees.
        fmt: Output format.
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
        variable=variable,
        originating_centre=originating_centre,
        system=system,
        product_type=product_type,
        year=year,
        month=month,
        leadtime_months=leadtime_months,
        area=area,
        fmt=fmt,
    )

    client = cdsapi.Client()
    client.retrieve("seasonal-monthly-single-levels", request).download(
        str(output_path)
    )

    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
