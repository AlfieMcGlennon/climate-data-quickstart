"""Download GloFAS historical river discharge from the Copernicus CEMS EWDS.

Edit the USER CONFIGURATION block and run:

    python scripts/glofas_download.py

The default pulls one day of river discharge over a UK bounding box.

IMPORTANT: GloFAS is on the EWDS endpoint, not the main CDS. You need a
separate EWDS account and Personal Access Token. Set ``EWDS_KEY`` as an
environment variable before running.

Documentation: docs/glofas/README.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


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
        RuntimeError: If ``EWDS_KEY`` environment variable is not set.
    """
    ewds_key = os.environ.get("EWDS_KEY")
    if not ewds_key:
        raise RuntimeError(
            "EWDS_KEY environment variable not set.\n"
            "GloFAS is on the Copernicus CEMS Early Warning Data Store (EWDS), "
            "which is a separate platform from the main CDS.\n"
            "Register at https://ewds.climate.copernicus.eu/, accept the "
            "GloFAS licence, copy your Personal Access Token, and export it:\n"
            "  export EWDS_KEY=<your-token>"
        )

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


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
