# ARCO-ERA5 (Google Cloud)

Analysis-Ready, Cloud-Optimized ERA5 reanalysis data, hosted on Google Cloud
Storage as a public Zarr store. No download queue, no API key, no registration.
Open it with xarray and start working.

> **Scope of this page.** A getting-started reference for researchers new to
> cloud-native climate data access. It covers what ARCO-ERA5 contains, how to
> open it, and where it differs from the standard CDS ERA5 product. For the
> full technical specification, see the primary sources linked at the bottom.

## When to use this

When you want ERA5 without any registration, API key, or download queue.
Just open the Zarr store with xarray and start slicing. Good for
teaching, quick prototyping, or any situation where you want to skip
the CDS setup entirely. The trade-off is that only a subset of ERA5
variables are available, and you need a reasonable internet connection
since the data streams on the fly.

## What this dataset is

ARCO-ERA5 is a cloud-optimised copy of a large subset of ERA5, maintained by
Google Research. The same underlying reanalysis data that the Copernicus
Climate Data Store serves as downloadable files is here stored as Zarr arrays
on Google Cloud Storage. You open the store with `xarray.open_zarr()`, subset
lazily, and only the bytes you need travel over the network.

The project is described in Carver & Merose (2023) and the
[google-research/arco-era5](https://github.com/google-research/arco-era5)
repository.

## Coverage

| Property | Value |
|---|---|
| Grid | Regular latitude-longitude |
| Resolution | 0.25 degrees (approximately 31 km) |
| Spatial coverage | Global |
| Temporal resolution | Hourly |
| Temporal coverage | 1979 to present |
| Variables | 31 surface-level + 7 pressure-level variables on 37 levels |
| Format | Zarr, chunked for efficient cloud reads |
| Storage | `gs://gcp-public-data-arco-era5/` (public, no auth) |

ARCO-ERA5 does not include the full ERA5 variable catalogue. Wave variables,
ensemble members, and the back extension (pre-1979) are absent. For those,
use the CDS directly (see `docs/era5-single-levels/` in this repo).

## Variables

The AR (analysis-ready) store uses descriptive variable names that differ from
both the CDS API names and the GRIB short names. The ten most commonly used
surface variables are listed below. Variable names are taken from the store
metadata; inspect `ds.data_vars` after opening to confirm the exact names
available in the version you access.

| AR store name | Description | Units |
|---|---|---|
| `2m_temperature` | 2 metre temperature | K |
| `10m_u_component_of_wind` | 10 metre U wind component | m s-1 |
| `10m_v_component_of_wind` | 10 metre V wind component | m s-1 |
| `mean_sea_level_pressure` | Mean sea level pressure | Pa |
| `surface_pressure` | Surface pressure | Pa |
| `total_precipitation` | Total precipitation | m |
| `sea_surface_temperature` | Sea surface temperature | K |
| `2m_dewpoint_temperature` | 2 metre dewpoint temperature | K |
| `total_cloud_cover` | Total cloud cover | 0-1 |
| `surface_net_solar_radiation` | Surface net solar radiation | J m-2 |

Pressure-level variables (temperature, geopotential, specific humidity,
u/v/w wind, vertical velocity) are available on all 37 model levels within
the same store.

## Access

### 1. Install

```bash
pip install xarray zarr gcsfs matplotlib cartopy
```

Optional: `pip install dask` if you want parallel reads for large slices.

### 2. Open the store

No registration, no API key, no queue. The bucket is public.

```python
import xarray as xr

ds = xr.open_zarr(
    "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3",
    chunks=None,
    storage_options=dict(token="anon"),
)

# Filter to the valid time range recorded in the store metadata
ds = ds.sel(
    time=slice(ds.attrs["valid_time_start"], ds.attrs["valid_time_stop"])
)
```

Setting `chunks=None` loads coordinate metadata eagerly but keeps data
variables lazy (backed by the Zarr store). Replace with `chunks={}` if you
want Dask-backed arrays for parallel computation.

### 3. Subset and use

```python
t2m = ds["2m_temperature"].sel(
    time="2023-07-01T12:00",
    latitude=slice(55, 49),
    longitude=slice(-8, 2),
)
t2m.load()  # fetches only the bytes for this slice
```

### 4. Save to NetCDF (optional)

```python
t2m.to_netcdf("arco_era5_slice.nc")
```

## How it differs from CDS ERA5

| | CDS ERA5 | ARCO-ERA5 |
|---|---|---|
| Access | API key + queue | Public Zarr, no auth |
| Wait time | Minutes to hours | Instant (lazy open) |
| Variables | 250+ surface variables | ~31 surface + 7 on 37 pressure levels |
| Temporal range | 1940-present (with back extension) | 1979-present |
| Wave variables | Yes | No |
| Ensemble members | Yes (ERA5 EDA) | No |
| Output format | NetCDF or GRIB file | Zarr (in-memory xarray, optional NetCDF export) |
| Egress cost | Free | Free within GCP; potential egress charges outside GCP |

Use ARCO-ERA5 when you want fast, interactive access to common variables
without managing credentials or waiting in a queue. Use CDS ERA5 when you
need the full variable catalogue, wave data, ensemble members, or pre-1979
coverage.

## Gotchas

- **Latitude order.** Stored descending (90 to -90). Use `ds.sortby("latitude")` if your workflow expects ascending order.
- **Egress outside GCP.** Reading from outside Google Cloud incurs standard GCP egress charges. For large volumes, run your analysis in a GCP VM in `us-central1`. See https://github.com/google-research/arco-era5#data-access.
- **No daily or monthly aggregates.** Only hourly instantaneous fields. Aggregate with `xarray.resample()`.
- **Variable naming.** AR store names (`2m_temperature`) differ from CDS API names and GRIB short names. The surface geopotential variable may appear as `zs` rather than `z`.
- **Throttling.** Google may throttle after approximately 200 GB of egress in a session. Subset aggressively.

## Licence and citation

ARCO-ERA5 redistributes Copernicus ERA5 data. The underlying licence is
CC-BY-4.0 (transitioned from the Copernicus Products licence in July 2025).
Derived products must credit both Copernicus and the ARCO-ERA5 project.

Dataset reference:

> Carver, R. W. and Merose, A. (2023): ARCO-ERA5: An Analysis-Ready
> Cloud-Optimized Reanalysis Dataset. 4th Workshop on Leveraging AI in
> the Exploitation of Satellite Earth Observation & Numerical Weather
> Prediction Data, ICLR 2023.

Original ERA5 citation:

> Hersbach, H., Bell, B., Berrisford, P., et al. (2020). The ERA5 global
> reanalysis. Quarterly Journal of the Royal Meteorological Society,
> 146(730), 1999-2049. DOI: 10.1002/qj.3803

## Further reading

- GitHub repository: https://github.com/google-research/arco-era5
- GCS bucket listing: https://console.cloud.google.com/storage/browser/gcp-public-data-arco-era5
- Carver & Merose 2023 paper: https://arxiv.org/abs/2301.12808
- CDS ERA5 (full product): see `docs/era5-single-levels/` in this repo
- Earth Data Hub (alternative streaming access): see `docs/earth-data-hub/` in this repo
