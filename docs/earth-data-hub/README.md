# Earth Data Hub

Streaming access to ERA5, ERA5-Land, CMIP6 and other climate datasets
published as cloud-optimised Zarr stores. Part of the Destination Earth
programme, operated by ECMWF and collaborators.

> **Scope of this page.** A getting-started reference for MSc/PhD students
> and early-career researchers who have already used the CDS-based
> datasets in this repo and want to try the streaming alternative. For
> the authoritative platform documentation, see
> https://earthdatahub.destine.eu/getting-started.

## When to use this

When you want ERA5 data without waiting in the CDS queue. EDH streams
the bytes you actually need over the network, so there is no file to
download, no queue, and you can work with the data lazily in xarray.
Particularly useful for interactive exploration or when you need a small
slice of a large dataset and the CDS queue is hours long.

## At a glance

| Property | Value |
|---|---|
| Access paradigm | Streaming via Zarr + xarray over HTTPS |
| Python client | Standard xarray + zarr (no EDH-specific SDK) |
| Auth | DestinE personal access token via `~/.netrc` or URL |
| Catalogue | https://earthdatahub.destine.eu/catalogue |
| Base URL | `https://data.earthdatahub.destine.eu/` |
| Quota | 500,000 requests per user per month |
| Cost | Free after registration |

## Why this matters

Everything up to this point (ERA5 single levels, pressure levels, ERA5-
Land, daily statistics) uses the Copernicus Climate Data Store. You
submit a request; the CDS queues it, processes, serves you a file; you
download the whole file; you open it with xarray.

Earth Data Hub flips that. The same underlying data is stored as
cloud-optimised Zarr. You open the store with xarray, lazily slice by
time, variable and region, and only the bytes you actually need stream
over the wire. No queue, no file download, no five-minute wait for a
small time series.

When it suits your workflow, EDH is dramatically faster than CDS. When it
does not, stick with CDS: the two are complementary, not substitutes.

## Available datasets

EDH is **selective**, not a full CDS mirror. As of writing, the
catalogue includes:

- ERA5 single levels (hourly, 1940-present)
- ERA5 single levels monthly means
- ERA5 pressure levels (hourly)
- ERA5-Land (hourly, 1950-present)
- ERA5-Land daily (EDH-derived daily aggregate)
- Curated CMIP6 models and SSP scenarios (CESM2, CMCC-CM2-SR5, EC-Earth3-CC, IPSL-CM6A-LR, MPI-ESM1-2-HR, NorESM2-MM)
- Copernicus DEM (Global 90 m)
- Climate DT (Destination Earth Climate Adaptation Digital Twin output)

Check https://earthdatahub.destine.eu/catalogue for the live list.
Many CDS datasets (seasonal forecasts, CAMS, Copernicus Marine) are not
on EDH.

## Get data in 5 minutes

1. Register for a free account at https://platform.destine.eu/
2. Sign in to Earth Data Hub, go to your profile settings, and create a
   **Personal Access Token**. Copy it.
3. Add the token to your netrc file. On **Windows**, open
   `C:\Users\<you>\_netrc` and add:
   ```
   machine data.earthdatahub.destine.eu
       login your-destine-username
       password YOUR_PERSONAL_ACCESS_TOKEN
   ```
   On **Linux/macOS**, add the same block to `~/.netrc` and run
   `chmod 600 ~/.netrc`. If you already have entries for other services
   (e.g. NASA Earthdata), add this block below them.
4. `pip install xarray zarr fsspec aiohttp netcdf4`
5. Run `python scripts/earth_data_hub_download.py`

The default pulls 2 metre temperature from ERA5 over a UK bounding box
for 2023, demonstrating the streaming pattern against a live public
dataset.

## When to use EDH versus CDS

| Use EDH for | Use CDS for |
|---|---|
| Point time series (decades of hourly for one grid cell) | First-time users; CDS has broader tutorial coverage |
| Fast prototyping, notebooks | Large dense spatial slabs (whole-cube downloads) |
| Long-record single-variable workflows | Variables or datasets not on EDH |
| Lazy xarray indexing, partial loads | Workflows that need GRIB natively |
| Repeated experiments on the same dataset | When the 500k-request monthly quota is a concern |

## Things to know

- **No EDH-specific Python SDK.** The access path is standard
  `xarray.open_dataset(url, engine="zarr", chunks={})`. You do not need
  `earthkit-data`, `polytope-client`, or any DestinE-specific library for
  basic use.
- **`chunks={}` is important.** Passing `chunks={}` to `open_dataset`
  defers the read until you call `.compute()` or reduce the array.
  Without it, xarray eagerly loads the full dataset as a single chunk,
  which defeats the purpose of streaming.
- **Quota: 500,000 requests per user per month.** Heavy per-chunk
  lookups on small-chunked datasets can burn through this faster than
  expected. Subset aggressively before calling `.load()`.
- **Authoritative for what it mirrors.** EDH republishes the same
  underlying ERA5 data that CDS serves, just in a different encoding. The
  EDH-produced derived products (for example `era5-land-daily`) are
  produced by the EDH team and are not canonical CDS publications; cite
  them accordingly.
- **Catalogue is actively expanding.** Pin dataset paths in production
  code and check the catalogue browser for the latest additions.
- **Public vs private datasets.** A public `test-dataset-v0.zarr` is
  available for smoke-testing without authentication; real datasets
  require the `.netrc` entry.

## Licence and attribution

The underlying data licence is inherited from each dataset's source.
For ERA5 and ERA5-Land, that is the Copernicus Products licence (as of
02 July 2025, this transitioned to CC-BY-4.0 for Copernicus products;
check the dataset page for the current terms).

Attribution (for ERA5 derivatives served via EDH):

> Generated using Copernicus Climate Change Service information [Year]

Or for modified derivatives:

> Contains modified Copernicus Climate Change Service information [Year]

Acknowledge the Destination Earth platform where appropriate:

> Created in the framework of the European Union Destination Earth
> initiative.

## Citation

Cite the underlying dataset. For ERA5:

> Hersbach, H., et al. (2020). The ERA5 global reanalysis. Quarterly
> Journal of the Royal Meteorological Society, 146(730), 1999-2049.
> DOI: 10.1002/qj.3803

For ERA5-Land:

> Munoz-Sabater, J., et al. (2021). ERA5-Land: a state-of-the-art global
> reanalysis dataset for land applications. Earth System Science Data,
> 13, 4349-4383. DOI: 10.5194/essd-13-4349-2021

For CMIP6 models: cite the originating modelling centre and the CMIP6
framework paper per WCRP guidance.

A canonical citation for the EDH platform itself was not found in
primary sources; acknowledge "Earth Data Hub / Destination Earth" in
prose.

## Further reading

- EDH homepage: https://earthdatahub.destine.eu/
- Getting started: https://earthdatahub.destine.eu/getting-started
- Catalogue: https://earthdatahub.destine.eu/catalogue
- DestinE platform: https://platform.destine.eu/
- ERA5 via CDS in this repo: [../era5-single-levels/README.md](../era5-single-levels/README.md)
