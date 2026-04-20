"""Stream a slice of ERA5 data from Earth Data Hub using xarray + zarr.

Edit the USER CONFIGURATION block and run:

    python scripts/earth_data_hub_download.py

The defaults open ERA5 hourly single levels from EDH, subset 2 metre
temperature over a UK bounding box for one day, and save the result as a
small NetCDF. No large download, just streaming of the needed bytes.

Documentation: docs/earth-data-hub/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.credentials import check_edh_token  # noqa: E402


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# EDH Zarr dataset URL. See https://earthdatahub.destine.eu/catalogue for
# the full catalogue. The example below targets ERA5 single levels.
EDH_DATASET_URL: str = (
    "https://data.earthdatahub.destine.eu/era5/"
    "reanalysis-era5-single-levels-v0.zarr"
)

VARIABLE: str = "2m_temperature"

# Time range (use slices rather than exact values since EDH is a big store).
TIME_START: str = "2023-07-01T00:00"
TIME_END: str = "2023-07-01T23:00"

# Spatial bounding box. Note latitude slice order depends on dataset's
# axis direction; most ERA5 stores go from +90 to -90, so slice(north, south).
LAT_NORTH: float = 55
LAT_SOUTH: float = 49
LON_WEST: float = -8
LON_EAST: float = 2

OUTPUT_DIR: str = "./data/earth-data-hub"
OUTPUT_FILENAME: str = "era5_edh_test.nc"
# ==================================================================


def download() -> Path:
    """Stream a subset from Earth Data Hub and save it as NetCDF.

    Returns:
        Path to the saved NetCDF file.

    Raises:
        FileNotFoundError: If EDH credentials are not configured.
    """
    check_edh_token()

    import xarray as xr

    output_path = Path(OUTPUT_DIR) / OUTPUT_FILENAME
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open the Zarr store lazily. trust_env=True makes aiohttp pick up
    # credentials from ~/.netrc.
    ds = xr.open_dataset(
        EDH_DATASET_URL,
        engine="zarr",
        chunks={},
        storage_options={"client_kwargs": {"trust_env": True}},
    )

    # Subset to the region and time window we want. Nothing is downloaded yet;
    # the lazy slice defines the byte-ranges that will be fetched on compute.
    subset = ds[VARIABLE].sel(
        time=slice(TIME_START, TIME_END),
        latitude=slice(LAT_NORTH, LAT_SOUTH),
        longitude=slice(LON_WEST, LON_EAST),
    )

    # Materialise and save
    subset.load().to_netcdf(output_path)
    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
