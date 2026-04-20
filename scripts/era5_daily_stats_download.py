"""Download pre-computed daily statistics from ERA5 via the CDS.

Edit the USER CONFIGURATION block and run:

    python scripts/era5_daily_stats_download.py

The defaults pull three days of daily-mean 2 metre temperature over the UK.

The CDS returns a zip containing a single NetCDF; this script unpacks it
for you, leaving just the .nc file in the output directory.

Documentation: docs/era5-daily-stats/README.md
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.credentials import check_cds_credentials  # noqa: E402


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
VARIABLES: list[str] = ["2m_temperature"]

# One of: "daily_mean", "daily_maximum", "daily_minimum", "daily_sum".
# Note: "daily_sum" only applies to accumulated variables (precipitation,
# radiation, fluxes). It is a no-op or an error on instantaneous fields
# like 2m_temperature.
DAILY_STATISTIC: str = "daily_mean"

# Sub-daily sampling used to compute the aggregate.
# "1_hourly" is the most faithful; "3_hourly" or "6_hourly" save compute.
FREQUENCY: str = "1_hourly"

# UTC offset for the 24-hour window. Format: "utc+HH:00" or "utc-HH:00".
TIME_ZONE: str = "utc+00:00"

YEARS: list[str] = ["2023"]
MONTHS: list[str] = ["07"]
DAYS: list[str] = ["01", "02", "03"]

# Bounding box as [north, west, south, east].
BBOX: list[float] = [55, -8, 49, 2]  # UK

OUTPUT_DIR: str = "./data/era5-daily-stats"
OUTPUT_FILENAME: str = "era5_daily_stats_test.nc"
# ==================================================================


def download(
    variables: Iterable[str] = VARIABLES,
    daily_statistic: str = DAILY_STATISTIC,
    frequency: str = FREQUENCY,
    time_zone: str = TIME_ZONE,
    years: Iterable[str] = YEARS,
    months: Iterable[str] = MONTHS,
    days: Iterable[str] = DAYS,
    bbox: list[float] = BBOX,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download ERA5 daily-statistics data to disk.

    The CDS always returns a zip archive for this dataset. This function
    extracts the NetCDF from the zip and leaves only the .nc file at
    ``output_dir/output_filename``.

    Args:
        variables: CDS API variable names (same catalogue as ERA5 single levels).
        daily_statistic: One of ``daily_mean``, ``daily_maximum``,
            ``daily_minimum``, ``daily_sum``.
        frequency: Sub-daily sampling: ``1_hourly``, ``3_hourly``, or ``6_hourly``.
        time_zone: UTC offset string, e.g. ``utc+00:00``.
        years: Years as strings.
        months: Months as zero-padded strings.
        days: Days as zero-padded strings.
        bbox: ``[north, west, south, east]`` in degrees.
        output_dir: Directory to write to.
        output_filename: Final NetCDF filename (after unzip).

    Returns:
        The path to the unzipped NetCDF.

    Raises:
        FileNotFoundError: If ``~/.cdsapirc`` is missing.
    """
    check_cds_credentials()

    import cdsapi

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir_path / (output_filename + ".zip")
    nc_path = output_dir_path / output_filename

    request = {
        "product_type": "reanalysis",
        "variable": list(variables),
        "year": list(years),
        "month": list(months),
        "day": list(days),
        "daily_statistic": daily_statistic,
        "time_zone": time_zone,
        "frequency": frequency,
        "area": bbox,
    }

    client = cdsapi.Client()
    client.retrieve(
        "derived-era5-single-levels-daily-statistics",
        request,
    ).download(str(zip_path))

    # Unzip and rename the contained NetCDF to OUTPUT_FILENAME
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.namelist() if m.endswith(".nc")]
        if not members:
            raise RuntimeError(f"No NetCDF found in {zip_path}")
        with zf.open(members[0]) as src, open(nc_path, "wb") as dst:
            dst.write(src.read())
    zip_path.unlink()

    return nc_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
