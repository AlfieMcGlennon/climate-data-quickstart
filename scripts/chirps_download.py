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


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# Year to download. One year per file.
YEAR: int = 2023

# Grid: "p05" for 0.05 degree or "p25" for 0.25 degree.
GRID: str = "p25"

OUTPUT_DIR: str = "./data/chirps"
OUTPUT_FILENAME: str | None = None  # None => auto-name from year and grid
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


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
