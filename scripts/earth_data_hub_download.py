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


def download(
    edh_dataset_url: str = EDH_DATASET_URL,
    variable: str = VARIABLE,
    time_start: str = TIME_START,
    time_end: str = TIME_END,
    lat_north: float = LAT_NORTH,
    lat_south: float = LAT_SOUTH,
    lon_west: float = LON_WEST,
    lon_east: float = LON_EAST,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Stream a subset from Earth Data Hub and save it as NetCDF.

    Args:
        edh_dataset_url: Full Zarr URL for the EDH dataset.
        variable: Variable to pull.
        time_start, time_end: ISO date strings.
        lat_north, lat_south, lon_west, lon_east: Spatial bounds in degrees.
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        Path to the saved NetCDF file.

    Raises:
        FileNotFoundError: If EDH credentials are not configured.
    """
    check_edh_token()

    import xarray as xr

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open the Zarr store lazily. trust_env=True makes aiohttp pick up
    # credentials from ~/.netrc.
    ds = xr.open_dataset(
        edh_dataset_url,
        engine="zarr",
        chunks={},
        storage_options={"client_kwargs": {"trust_env": True}},
    )

    # Normalise longitude to -180..180 if the store uses 0..360, then
    # sortby to guarantee the .sel slice works regardless of axis
    # direction.
    if float(ds["longitude"].max()) > 180:
        ds = ds.assign_coords(longitude=(((ds["longitude"] + 180) % 360) - 180))
    ds = ds.sortby("latitude").sortby("longitude")

    # Detect the time dimension name. EDH ERA5 stores use 'valid_time'
    # (matching the current CDS NetCDF convention); older stores used
    # 'time'. Use ds.sizes (keys) which is the documented public way to
    # access dimension names in modern xarray.
    dim_names = tuple(ds.sizes)
    if "valid_time" in dim_names:
        time_dim = "valid_time"
    elif "time" in dim_names:
        time_dim = "time"
    else:
        raise RuntimeError(
            f"Could not find a time dimension. Available dims: {dim_names}"
        )

    # Subset to the region and time window we want. Nothing is downloaded yet;
    # the lazy slice defines the byte-ranges that will be fetched on compute.
    indexers = {
        time_dim: slice(time_start, time_end),
        "latitude": slice(lat_south, lat_north),
        "longitude": slice(lon_west, lon_east),
    }
    subset = ds[variable].sel(indexers)

    # Materialise and save
    subset.load().to_netcdf(output_path)
    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
