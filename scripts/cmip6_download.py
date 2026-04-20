"""Download CMIP6 climate projections from the Copernicus CDS.

Edit the USER CONFIGURATION block and run:

    python scripts/cmip6_download.py

The default pulls one model (MPI-ESM1-2-LR), one scenario (SSP5-8.5),
monthly 2 m air temperature over a UK bounding box for 2050. Output is
a zip of NetCDF; this script unpacks it and leaves a single merged .nc
using xarray.open_mfdataset.

Documentation: docs/cmip6/README.md
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
# One model per request is the simplest starting point. See the CDS
# dataset page for the full list of ~56-60 available models.
MODEL: str = "mpi_esm1_2_lr"

# Scenario. See README for meanings. "historical" for 1850-2014.
EXPERIMENT: str = "ssp5_8_5"

# Variable: CDS snake_case name. Maps to a CMIP6 short name inside the file
# (e.g. "near_surface_air_temperature" -> "tas").
VARIABLE: str = "near_surface_air_temperature"

TEMPORAL_RESOLUTION: str = "monthly"  # "monthly", "daily", or "fixed"

# Year range. Historical: 1850-2014. SSPs: 2015-2100 (some to 2300).
YEARS: list[str] = ["2050"]
MONTHS: list[str] = [f"{m:02d}" for m in range(1, 13)]

# Bounding box [north, west, south, east].
BBOX: list[float] = [61, -8, 49, 2]  # UK

OUTPUT_DIR: str = "./data/cmip6"
OUTPUT_FILENAME: str = "cmip6_test.nc"
# ==================================================================


def download(
    model: str = MODEL,
    experiment: str = EXPERIMENT,
    variable: str = VARIABLE,
    temporal_resolution: str = TEMPORAL_RESOLUTION,
    years: Iterable[str] = YEARS,
    months: Iterable[str] = MONTHS,
    bbox: list[float] = BBOX,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download a CMIP6 slice and merge the returned NetCDF files.

    The CDS returns CMIP6 requests as a zip containing one or more NetCDF
    files. This function extracts them all and merges into a single NetCDF
    at ``output_dir/output_filename`` using xarray.

    Args:
        model: CDS model name (e.g. ``mpi_esm1_2_lr``).
        experiment: CDS experiment string (``historical``, ``ssp5_8_5``, etc.).
        variable: CDS variable name (snake_case).
        temporal_resolution: ``monthly``, ``daily``, or ``fixed``.
        years: Years as strings.
        months: Months as zero-padded strings.
        bbox: ``[north, west, south, east]`` in degrees.
        output_dir: Directory to write to.
        output_filename: Output filename (merged NetCDF).

    Returns:
        Path to the merged NetCDF.

    Raises:
        FileNotFoundError: If ``~/.cdsapirc`` is missing.
    """
    check_cds_credentials()

    import cdsapi
    import xarray as xr

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir_path / (output_filename + ".zip")
    extract_dir = output_dir_path / "_extracted"
    nc_path = output_dir_path / output_filename

    request = {
        "temporal_resolution": temporal_resolution,
        "experiment": experiment,
        "variable": variable,
        "model": model,
        "year": list(years),
        "month": list(months),
        "area": bbox,
        "data_format": "netcdf",
        "download_format": "zip",
    }

    client = cdsapi.Client()
    client.retrieve("projections-cmip6", request).download(str(zip_path))

    # Unpack and merge the NetCDF files inside the zip
    extract_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)

    nc_files = list(extract_dir.glob("*.nc"))
    if not nc_files:
        raise RuntimeError(f"No NetCDF files in {zip_path}")

    if len(nc_files) == 1:
        nc_files[0].rename(nc_path)
    else:
        ds = xr.open_mfdataset(nc_files, combine="by_coords")
        ds.to_netcdf(nc_path)
        ds.close()

    # Clean up extract dir and zip
    for f in extract_dir.glob("*"):
        f.unlink()
    extract_dir.rmdir()
    zip_path.unlink()

    return nc_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
