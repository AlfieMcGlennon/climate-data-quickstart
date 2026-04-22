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

# Chunked download settings (used by download_chunked() only).
CHUNK_BY: str = "month"      # "month" or "year"
MAX_RETRIES: int = 3
MERGE_OUTPUT: bool = True
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


def download_chunked(
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
    chunk_by: str = CHUNK_BY,
    max_retries: int = MAX_RETRIES,
    merge_output: bool = MERGE_OUTPUT,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Download ERA5 single levels in chunks with resume and retry.

    Splits the request by month or year so each chunk is a manageable
    size. Completed chunks are skipped on re-run. Failed chunks are
    retried automatically.

    Args:
        variables: CDS API variable names.
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
    template = "era5_sl_{year}_{month}" + ext

    chunks = plan_chunks(
        years=list(years),
        months=list(months),
        chunk_by=chunk_by,
        filename_template=template,
    )

    def _download_one(chunk: ChunkSpec) -> Path:
        return download(
            variables=variables,
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
        dataset="era5-single-levels",
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
