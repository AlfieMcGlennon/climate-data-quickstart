"""Open a slice of ARCO-ERA5 from Google Cloud Storage and save to NetCDF.

Edit the USER CONFIGURATION block below and run directly:

    python scripts/arco_era5_download.py

The defaults open the public Zarr store, subset one day of 2 metre
temperature over the UK, and save a small NetCDF file. No API key, no
queue, no registration needed.

Documentation: docs/arco-era5/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# Public Zarr store URL. The AR (analysis-ready) store contains 31
# surface variables and 7 pressure-level variables on 37 levels.
STORE_URL: str = (
    "gs://gcp-public-data-arco-era5/ar/"
    "full_37-1h-0p25deg-chunk-1.zarr-v3"
)

# Variable name as it appears in the AR store (not the CDS API name).
VARIABLE: str = "2m_temperature"

# Time range. ARCO-ERA5 is hourly, 1979-present.
TIME_START: str = "2023-07-01T00:00"
TIME_END: str = "2023-07-01T23:00"

# Bounding box in decimal degrees. Default: UK.
LAT_NORTH: float = 55
LAT_SOUTH: float = 49
LON_WEST: float = -8
LON_EAST: float = 2

# Where to save the materialised NetCDF.
OUTPUT_DIR: str = "./data/arco-era5"
OUTPUT_FILENAME: str = "arco_era5_test.nc"
# ==================================================================


def streaming_snippet(
    store_url: str = STORE_URL,
    variable: str = VARIABLE,
    time_start: str = TIME_START,
    time_end: str = TIME_END,
    lat_north: float = LAT_NORTH,
    lat_south: float = LAT_SOUTH,
    lon_west: float = LON_WEST,
    lon_east: float = LON_EAST,
) -> str:
    """Return a copy-pasteable code block for lazy access to ARCO-ERA5.

    Args:
        store_url: GCS Zarr store URL.
        variable: AR store variable name.
        time_start: ISO start time.
        time_end: ISO end time.
        lat_north: Northern bound in degrees.
        lat_south: Southern bound in degrees.
        lon_west: Western bound in degrees.
        lon_east: Eastern bound in degrees.

    Returns:
        A multi-line Python string the user can paste into their own script
        or notebook to open this slice lazily.
    """
    return f'''\
import xarray as xr

# Open the ARCO-ERA5 Zarr store lazily. Only coordinate metadata is
# fetched here. No API key or registration needed.
ds = xr.open_zarr(
    "{store_url}",
    chunks=None,
    storage_options=dict(token="anon"),
)

# Filter to the valid time range recorded in the store metadata
ds = ds.sel(time=slice(ds.attrs["valid_time_start"], ds.attrs["valid_time_stop"]))

# Subset to the region and time window. Still lazy at this point.
subset = ds["{variable}"].sel(
    time=slice("{time_start}", "{time_end}"),
    latitude=slice({lat_north}, {lat_south}),
    longitude=slice({lon_west}, {lon_east}),
)

# Materialise only the bytes for this slice
subset.load()
print(subset)

# Optional: save to NetCDF
# subset.to_netcdf("arco_era5_slice.nc")
'''


def download(
    store_url: str = STORE_URL,
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
    """Open ARCO-ERA5, subset a slice, and save it as NetCDF.

    No authentication needed. The GCS bucket is public.

    Args:
        store_url: Full Zarr store URL on GCS.
        variable: AR store variable name.
        time_start: ISO start time.
        time_end: ISO end time.
        lat_north: Northern latitude bound in degrees.
        lat_south: Southern latitude bound in degrees.
        lon_west: Western longitude bound in degrees.
        lon_east: Eastern longitude bound in degrees.
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        Path to the saved NetCDF file.
    """
    import xarray as xr

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open the Zarr store lazily. token="anon" tells gcsfs to skip
    # authentication since the bucket is public.
    ds = xr.open_zarr(
        store_url,
        chunks=None,
        storage_options=dict(token="anon"),
    )

    # Filter to the valid time range the store advertises
    ds = ds.sel(
        time=slice(ds.attrs["valid_time_start"], ds.attrs["valid_time_stop"])
    )

    # ARCO-ERA5 latitude runs 90 to -90 (descending), so slice(north, south)
    # works directly. Longitude is -180 to 180.
    subset = ds[variable].sel(
        time=slice(time_start, time_end),
        latitude=slice(lat_north, lat_south),
        longitude=slice(lon_west, lon_east),
    )

    # Materialise and save
    subset.load().to_netcdf(output_path)
    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Saved: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")

    print("\n--- Streaming snippet (copy-paste for lazy access) ---\n")
    print(streaming_snippet())
