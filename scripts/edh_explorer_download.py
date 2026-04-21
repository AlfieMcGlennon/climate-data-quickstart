"""Stream a slice from the Earth Data Hub catalogue and save to NetCDF.

This script backs the EDH catalogue explorer page in the app. It accepts
the same kwargs as the basic earth_data_hub_download.py but adds a
``family`` parameter (ignored at download time, used by the app for
snippet generation).

    python scripts/edh_explorer_download.py

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
EDH_DATASET_URL: str = (
    "https://data.earthdatahub.destine.eu/era5/"
    "reanalysis-era5-single-levels-v0.zarr"
)
VARIABLE: str = "t2m"
TIME_START: str = "2023-07-01T00:00"
TIME_END: str = "2023-07-01T23:00"
LAT_NORTH: float = 55
LAT_SOUTH: float = 49
LON_WEST: float = -8
LON_EAST: float = 2
OUTPUT_DIR: str = "./data/edh-explorer"
OUTPUT_FILENAME: str = "edh_explorer_download.nc"
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
    **kwargs: object,
) -> Path:
    """Stream a subset from EDH and save it as NetCDF.

    Extra kwargs (family, model, scenario, frequency) are accepted and
    ignored so the app runner can pass its full config dict through.

    Args:
        edh_dataset_url: Full Zarr URL for the EDH dataset.
        variable: Variable name (GRIB short name for ERA5, CMIP6 ID for CMIP6).
        time_start, time_end: ISO date strings.
        lat_north, lat_south, lon_west, lon_east: Spatial bounds in degrees.
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        Path to the saved NetCDF file.
    """
    check_edh_token()

    import xarray as xr

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ds = xr.open_dataset(
        edh_dataset_url,
        engine="zarr",
        chunks={},
        storage_options={"client_kwargs": {"trust_env": True}},
    )

    if float(ds["longitude"].max()) > 180:
        ds = ds.assign_coords(longitude=(((ds["longitude"] + 180) % 360) - 180))
    ds = ds.sortby("latitude").sortby("longitude")

    dim_names = tuple(ds.sizes)
    if "valid_time" in dim_names:
        time_dim = "valid_time"
    elif "time" in dim_names:
        time_dim = "time"
    else:
        raise RuntimeError(
            f"Could not find a time dimension. Available dims: {dim_names}"
        )

    lat_dim = "latitude" if "latitude" in dim_names else "lat"
    lon_dim = "longitude" if "longitude" in dim_names else "lon"

    indexers = {
        time_dim: slice(time_start, time_end),
        lat_dim: slice(lat_south, lat_north),
        lon_dim: slice(lon_west, lon_east),
    }
    subset = ds[variable].sel(indexers)
    subset.load().to_netcdf(output_path)
    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
