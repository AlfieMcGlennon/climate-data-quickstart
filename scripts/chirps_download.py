"""Download CHIRPS precipitation data from the UCSB Climate Hazards Center.

Edit the USER CONFIGURATION block and run:

    python scripts/chirps_download.py

The default pulls one year of CHIRPS daily precipitation at 0.25 degree
resolution, globally. Full year at 0.05 degree is several GB; 0.25 degree
is much smaller and sufficient for regional analysis.

Documentation: docs/chirps/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.chunked import (  # noqa: E402
    ChunkSpec,
    ProgressCallback,
    plan_chunks,
    run_chunked_download,
)


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# Year to download. One year per file.
YEAR: int = 2023

# Grid: "p05" for 0.05 degree or "p25" for 0.25 degree.
GRID: str = "p25"

OUTPUT_DIR: str = "./data/chirps"
OUTPUT_FILENAME: str | None = None  # None => auto-name from year and grid

# Chunked download settings (used by download_chunked() only).
YEARS: list[int] = [2023]    # Year range for chunked mode
MAX_RETRIES: int = 3
MERGE_OUTPUT: bool = True
# ==================================================================


CHIRPS_BASE: str = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf"


def download(
    year: int = YEAR,
    grid: str = GRID,
    output_dir: str = OUTPUT_DIR,
    output_filename: str | None = OUTPUT_FILENAME,
) -> Path:
    """Download one year of CHIRPS daily NetCDF.

    Args:
        year: Calendar year, e.g. 2023.
        grid: ``p05`` (0.05 degree) or ``p25`` (0.25 degree).
        output_dir: Directory to write to.
        output_filename: Optional override filename; defaults to
            ``chirps-v2.0.<YEAR>.days_<GRID>.nc``.

    Returns:
        Path to the downloaded NetCDF.
    """
    import requests

    filename = output_filename or f"chirps-v2.0.{year}.days_{grid}.nc"
    url = f"{CHIRPS_BASE}/{grid}/chirps-v2.0.{year}.days_{grid}.nc"

    out = Path(output_dir) / filename
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.exists() and out.stat().st_size > 0:
        return out

    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return out


def download_chunked(
    years: list[int] = YEARS,
    grid: str = GRID,
    output_dir: str = OUTPUT_DIR,
    output_filename: str | None = None,
    max_retries: int = MAX_RETRIES,
    merge_output: bool = MERGE_OUTPUT,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Download multiple years of CHIRPS with resume and retry.

    Each year is one chunk (CHIRPS already organises files by year).

    Args:
        years: List of calendar years to download.
        grid: ``p05`` or ``p25``.
        output_dir: Directory to write to.
        output_filename: Final merged filename (None for auto).
        max_retries: Maximum attempts per chunk.
        merge_output: Whether to merge years into one file.
        progress_callback: Optional callback for progress reporting.

    Returns:
        Path to the merged file (if merge_output) or the output directory.
    """
    year_strs = [str(y) for y in years]

    chunks = plan_chunks(
        years=year_strs,
        months=["01"],
        chunk_by="year",
        filename_template=f"chirps-v2.0.{{year}}.days_{grid}.nc",
    )

    def _download_one(chunk: ChunkSpec) -> Path:
        return download(
            year=int(chunk.years[0]),
            grid=grid,
            output_dir=output_dir,
        )

    merged_name = output_filename or f"chirps_{grid}_{years[0]}_{years[-1]}_merged.nc"

    return run_chunked_download(
        download_one=_download_one,
        chunks=chunks,
        output_dir=output_dir,
        dataset="chirps",
        chunk_by="year",
        max_retries=max_retries,
        merge_output=merge_output,
        merged_filename=merged_name,
        data_format="netcdf",
        progress_callback=progress_callback,
    )


if __name__ == "__main__":
    if "--chunked" in sys.argv:
        path = download_chunked()
    else:
        path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
