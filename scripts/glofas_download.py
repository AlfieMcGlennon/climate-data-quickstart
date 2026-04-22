"""Download GloFAS historical river discharge from the Copernicus CEMS EWDS.

Edit the USER CONFIGURATION block and run:

    python scripts/glofas_download.py

The default pulls one day of river discharge over a UK bounding box.

IMPORTANT: GloFAS is on the EWDS endpoint, not the main CDS. You need a
separate EWDS account and Personal Access Token. Save your key to
``~/.ewdsapirc`` (same format as .cdsapirc but for EWDS) or set the
``EWDS_KEY`` environment variable.

Documentation: docs/glofas/README.md
"""

from __future__ import annotations

import os
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


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# GloFAS system version. v4.0 is current and runs on a 0.05 degree grid
# with hydrological_model "lisflood". v3.1 and v2.1 use a 0.1 degree grid
# and "htessel_lisflood".
SYSTEM_VERSION: str = "version_4_0"
HYDROLOGICAL_MODEL: str = "lisflood"

# Product type: "consolidated" for the main reanalysis back-catalogue;
# "intermediate" for the near-real-time tail driven by ERA5T.
PRODUCT_TYPE: str = "consolidated"

VARIABLE: str = "river_discharge_in_the_last_24_hours"

# Request date. Use "h" prefix keys - this is a GloFAS convention.
HYEAR: list[str] = ["2020"]
HMONTH: list[str] = ["12"]
HDAY: list[str] = ["01"]

# Bounding box [north, west, south, east].
BBOX: list[float] = [60, -10, 50, 2]  # UK

DATA_FORMAT: str = "grib2"  # "grib2" (native, recommended) or "netcdf"
DOWNLOAD_FORMAT: str = "unarchived"

OUTPUT_DIR: str = "./data/glofas"
OUTPUT_FILENAME: str = "glofas_historical_test.grib"

# Chunked download settings (used by download_chunked() only).
CHUNK_BY: str = "year"       # "month" or "year"
MAX_RETRIES: int = 3
MERGE_OUTPUT: bool = True
# ==================================================================


EWDS_URL: str = "https://ewds.climate.copernicus.eu/api"


def download(
    system_version: str = SYSTEM_VERSION,
    hydrological_model: str = HYDROLOGICAL_MODEL,
    product_type: str = PRODUCT_TYPE,
    variable: str = VARIABLE,
    hyear: Iterable[str] = HYEAR,
    hmonth: Iterable[str] = HMONTH,
    hday: Iterable[str] = HDAY,
    bbox: list[float] = BBOX,
    data_format: str = DATA_FORMAT,
    download_format: str = DOWNLOAD_FORMAT,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download a GloFAS historical slice to disk.

    Args:
        system_version: ``version_4_0`` (latest), ``version_3_1``, or ``version_2_1``.
        hydrological_model: ``lisflood`` (v4.0) or ``htessel_lisflood`` (v3.1, v2.1).
        product_type: ``consolidated`` for back-catalogue; ``intermediate`` for NRT.
        variable: Typically ``river_discharge_in_the_last_24_hours``.
        hyear: Years as strings.
        hmonth: Months as zero-padded strings.
        hday: Days as zero-padded strings.
        bbox: ``[north, west, south, east]`` in degrees.
        data_format: ``grib2`` or ``netcdf``.
        download_format: ``unarchived`` or ``zip``.
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        Path to the downloaded file.

    Raises:
        RuntimeError: If no EWDS credentials are found.
    """
    from common.credentials import check_ewds_key

    ewds_key = check_ewds_key()

    import cdsapi

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    request = {
        "system_version": [system_version],
        "hydrological_model": [hydrological_model],
        "product_type": [product_type],
        "variable": [variable],
        "hyear": list(hyear),
        "hmonth": list(hmonth),
        "hday": list(hday),
        "data_format": data_format,
        "download_format": download_format,
        "area": bbox,
    }

    client = cdsapi.Client(url=EWDS_URL, key=ewds_key)
    client.retrieve("cems-glofas-historical", request).download(str(output_path))

    return output_path


def download_chunked(
    system_version: str = SYSTEM_VERSION,
    hydrological_model: str = HYDROLOGICAL_MODEL,
    product_type: str = PRODUCT_TYPE,
    variable: str = VARIABLE,
    hyear: Iterable[str] = HYEAR,
    hmonth: Iterable[str] = HMONTH,
    hday: Iterable[str] = HDAY,
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
    """Download GloFAS historical data in chunks with resume and retry.

    Args:
        system_version: GloFAS system version.
        hydrological_model: Model name.
        product_type: ``consolidated`` or ``intermediate``.
        variable: GloFAS variable name.
        hyear: Years as strings.
        hmonth: Months as zero-padded strings.
        hday: Days as zero-padded strings.
        bbox: ``[north, west, south, east]`` in degrees.
        data_format: ``grib2`` or ``netcdf``.
        download_format: ``unarchived`` or ``zip``.
        output_dir: Directory to write to.
        output_filename: Final merged filename.
        chunk_by: ``"month"`` or ``"year"``.
        max_retries: Maximum attempts per chunk.
        merge_output: Whether to merge chunks into one file.
        progress_callback: Optional callback for progress reporting.

    Returns:
        Path to the merged file (if merge_output) or the output directory.
    """
    ext = ".grib" if data_format == "grib2" else ".nc"
    template = "glofas_{year}_{month}" + ext

    chunks = plan_chunks(
        years=list(hyear),
        months=list(hmonth),
        chunk_by=chunk_by,
        filename_template=template,
    )

    def _download_one(chunk: ChunkSpec) -> Path:
        return download(
            system_version=system_version,
            hydrological_model=hydrological_model,
            product_type=product_type,
            variable=variable,
            hyear=chunk.years,
            hmonth=chunk.months,
            hday=hday,
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
        dataset="glofas",
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
