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

from common.chunked import (  # noqa: E402
    ChunkSpec,
    ProgressCallback,
    plan_chunks,
    run_chunked_download,
)
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

# Chunked download settings (used by download_chunked() only).
CHUNK_BY: str = "month"      # "month" or "year"
MAX_RETRIES: int = 3
MERGE_OUTPUT: bool = True
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


def download_chunked(
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
    chunk_by: str = CHUNK_BY,
    max_retries: int = MAX_RETRIES,
    merge_output: bool = MERGE_OUTPUT,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Download ERA5 pressure levels in chunks with resume and retry.

    Args:
        variables: CDS API variable names.
        pressure_levels: Pressure levels in hPa as strings.
        years: Years as strings.
        months: Months as zero-padded strings.
        days: Days as zero-padded strings.
        hours: Hours as ``"HH:00"``.
        bbox: ``[north, west, south, east]`` in degrees.
        data_format: ``"netcdf"`` or ``"grib"``.
        download_format: ``"unarchived"`` or ``"zip"``.
        output_dir: Directory to write to.
        output_filename: Final merged filename.
        chunk_by: ``"month"`` or ``"year"``.
        max_retries: Maximum attempts per chunk.
        merge_output: Whether to merge chunks into one file.
        progress_callback: Optional callback for progress reporting.

    Returns:
        Path to the merged file (if merge_output) or the output directory.
    """
    check_cds_credentials()

    ext = ".grib" if data_format == "grib" else ".nc"
    template = "era5_pl_{year}_{month}" + ext

    chunks = plan_chunks(
        years=list(years),
        months=list(months),
        chunk_by=chunk_by,
        filename_template=template,
    )

    def _download_one(chunk: ChunkSpec) -> Path:
        return download(
            variables=variables,
            pressure_levels=pressure_levels,
            years=chunk.years,
            months=chunk.months,
            days=days,
            hours=hours,
            bbox=bbox,
            data_format=data_format,
            download_format=download_format,
            output_dir=output_dir,
            output_filename=chunk.filename,
        )

    return run_chunked_download(
        download_one=_download_one,
        chunks=chunks,
        output_dir=output_dir,
        dataset="era5-pressure-levels",
        chunk_by=chunk_by,
        max_retries=max_retries,
        merge_output=merge_output,
        merged_filename=output_filename,
        data_format=data_format,
        progress_callback=progress_callback,
    )


if __name__ == "__main__":
    if "--chunked" in sys.argv:
        path = download_chunked()
    else:
        path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
