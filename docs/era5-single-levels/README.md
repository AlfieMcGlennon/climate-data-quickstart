# ERA5 single levels

Hourly reanalysis data for atmospheric, land-surface, and ocean-wave variables
on a single level (surface or near-surface), from 1940 to present, on a
0.25 degree global grid.

Produced by the Copernicus Climate Change Service (C3S) at ECMWF.

## What this dataset is

ERA5 is the fifth generation of ECMWF's global atmospheric reanalysis. A
reanalysis combines historical observations with a consistent forecast model
to produce a physically consistent estimate of the atmosphere's state on a
regular grid. "Single levels" refers to surface and near-surface variables
(temperature at 2 m, wind at 10 m, precipitation, radiation, soil moisture,
etc.) rather than variables on atmospheric pressure levels.

Use it when you need a long, global, physically consistent record of
surface and near-surface variables. The native product is hourly, but the
same data backs a wide range of temporal views: users routinely aggregate
hourly to daily means, daily min or max, monthly or annual statistics, or
compute custom indices (heatwave thresholds, frost days, growing degree
days). The ERA5 daily statistics dataset in this repo is a pre-computed
shortcut for the most common aggregates; everything else can be built from
the hourly data with `xarray.resample()` or `xarray.groupby()`.

Typical uses: climate baselines, forcing for land-surface and hydrological
models, validating regional models, bias-correcting projections, building
custom climate indices, and as the reference record for climate risk and
exposure analysis.

## Coverage

| Property | Value |
|---|---|
| Grid | Regular latitude-longitude |
| Resolution | 0.25 degrees (approximately 31 km) |
| Spatial coverage | Global, -90 to 90 latitude, 0 to 360 longitude |
| Temporal resolution | Hourly |
| Temporal coverage | 1940-01-01 to present |
| Update frequency | Daily |
| Latency | ERA5T approx 5 days behind real time, final ERA5 approx 2 to 3 months behind |
| Native archive | Reduced Gaussian N320 grid; the CDS pre-interpolates to regular lat/lon |
| CRS | Decimal degrees on a spherical Earth of radius 6367.47 km (as encoded in GRIB1) |

The ECMWF-encoded spherical Earth is not identical to WGS84 (EPSG:4326). Most
tooling reprojects transparently and the difference is sub-kilometre, which is
smaller than the 31 km grid cell and safe to ignore for typical use. If you are
co-registering ERA5 with high-resolution observation networks or point-measured
coordinates where sub-kilometre accuracy matters, be aware of the flag and
consult the ECMWF spatial reference note
(https://confluence.ecmwf.int/display/CKB/ERA5%3A+What+is+the+spatial+reference).

The 1940-1958 segment comes from the back extension; see [Known issues](#known-issues)
below for the caveats that apply to pre-1959 analysis.

## Variables

ERA5 single levels contains more than 250 variables. The ten most commonly
used are listed below. The full categorised list with descriptions is in
[variables.md](variables.md).

| CDS API name | Long name | GRIB short name | NetCDF name | Units |
|---|---|---|---|---|
| `2m_temperature` | 2 metre temperature | `2t` | `t2m` | K |
| `2m_dewpoint_temperature` | 2 metre dewpoint temperature | `2d` | `d2m` | K |
| `10m_u_component_of_wind` | 10 metre U wind component | `10u` | `u10` | m s-1 |
| `10m_v_component_of_wind` | 10 metre V wind component | `10v` | `v10` | m s-1 |
| `mean_sea_level_pressure` | Mean sea level pressure | `msl` | `msl` | Pa |
| `surface_pressure` | Surface pressure | `sp` | `sp` | Pa |
| `total_precipitation` | Total precipitation | `tp` | `tp` | m |
| `sea_surface_temperature` | Sea surface temperature | `sst` | `sst` | K |
| `surface_solar_radiation_downwards` | Surface solar radiation downwards | `ssrd` | `ssrd` | J m-2 |
| `total_cloud_cover` | Total cloud cover | `tcc` | `tcc` | 0-1 |

### Naming quirk

There are three names for every ERA5 variable and they are not
interchangeable:

- **CDS API name** (snake_case, e.g. `2m_temperature`) - what you pass to
  `cdsapi.Client().retrieve()` in the `variable` list.
- **GRIB short name** (e.g. `2t`) - the name stored inside GRIB records,
  per the ECMWF parameter database. GRIB files opened with `cfgrib` use
  these.
- **NetCDF name** (e.g. `t2m`) - what appears as a data variable when the
  CDS returns NetCDF. The rewrite from GRIB to NetCDF avoids leading digits
  because CF conventions and some tools dislike them, so `2t` becomes
  `t2m`, `10u` becomes `u10`, and so on. For names that do not start with a
  digit (`msl`, `sp`, `tp`, `sst`, `tcc`), GRIB and NetCDF names match.

This repo's scripts and notebooks request data by CDS API name and open it
by NetCDF name, because that is the default `data_format` and the format
most users start with.

## Access

### 1. Register

Create a free account on the Copernicus Climate Data Store:
https://cds.climate.copernicus.eu/

### 2. Accept the dataset licence

Log in, go to your profile, and accept the "Licence to use Copernicus Products"
for the ERA5 single levels dataset. You must do this before API requests will
succeed.

### 3. Create `~/.cdsapirc`

Copy your Personal Access Token from the "Your profile" page. Create a file at
`~/.cdsapirc` with two lines:

```
url: https://cds.climate.copernicus.eu/api
key: <your-personal-access-token>
```

On Windows the equivalent path is `%USERPROFILE%\.cdsapirc`.

### 4. Install the Python client

```bash
pip install cdsapi xarray netcdf4
```

### 5. Run the download script

```bash
python scripts/era5_single_levels_download.py
```

The default config pulls one hour of 2 metre temperature over the UK as a
minimal test. Edit the config block at the top of the script to change
variables, dates, or region.

### Queue behaviour and rate limits

Requests are queued server-side. A small single-day request usually completes
within minutes. Large multi-decade or multi-variable requests can take hours.
Queue position is visible at https://cds.climate.copernicus.eu/requests.

The CDS shares a finite pool of processing slots across the web form, the API,
and the Toolbox. The practical guidance from ECMWF is:

- Keep parallel submissions modest. A small number of simultaneous requests
  from one account is fine; many at once will be throttled.
- Prefer many small, well-scoped requests over a few very large ones. Large
  heavy requests are deprioritised in the queue, so splitting into chunks
  (month by month, variable by variable) usually finishes sooner overall.
- Concurrency limits and size caps are adjusted by ECMWF according to system
  load, not published as fixed numbers.

For bulk historical work, particularly at institutional scale, ECMWF points
advanced users to direct MARS access rather than a separate CDS tier. Before
submitting a multi-year multi-variable pull, it is also often faster to ask
around: a colleague or research group may already have the relevant ERA5
slice on shared storage. See
https://confluence.ecmwf.int/display/CKB/Climate+Data+Store+%28CDS%29+documentation
and
https://confluence.ecmwf.int/display/CKB/Common+Error+Messages+for+CDS+Requests
for the authoritative guidance.

### Request size and splitting

The CDS enforces a cap on the volume of data and number of fields per
request. The exact number changes with system load and is not published. The
cap is applied at submission time, so if a request is too large the API
returns an error and asks you to split.

A quick way to feel out the current cap: open the dataset on the CDS website,
tick variables, years, months and hours in the download form, and watch the
estimated item count at the bottom. Add and remove items until it reports a
manageable size, then replicate those fields in your API request. ECMWF's
detailed guidance on splitting long requests is at
https://confluence.ecmwf.int/display/CKB/Common+Error+Messages+for+CDS+Requests.

The recommended principle is to loop over smaller temporal chunks (e.g., one
month at a time) rather than submitting one monolithic request. This is
faster overall because small requests are not deprioritised in the queue.

### Output formats

GRIB is the default and fastest format; it is the native archive format. NetCDF4
is also supported via `data_format: "netcdf"` but is marked as experimental by
the CDS and large requests may be split into multiple files.

### Efficient time-series retrieval

The CDS also publishes a sibling entry specifically for point time-series
retrievals:
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries

Use it when you want decades of hourly data for one or a few grid points.
It is a time-chunked repackaging of the same underlying ERA5 data, accessed
through the same `cdsapi` client (dataset id `reanalysis-era5-single-levels-timeseries`),
with NetCDF or CSV output. Compared to the standard single-levels endpoint it
is considerably faster for point queries but does not support bounding-box
retrieval and exposes only a curated subset of the most common variables. For
maps, spatial slabs, or any variable outside the curated subset, use the
standard dataset covered in this entry.

## ERA5 versus ERA5T

The CDS returns two production streams for recent data:

- **ERA5T** (preliminary): available approximately 5 days behind real time,
  updated daily.
- **ERA5** (final): available approximately 2 to 3 months behind real time
  after quality control completes.

Records are distinguished via the `expver` dimension: `expver=1` is final ERA5,
`expver=5` is ERA5T. When both cover the same period, downstream code must
select or merge them explicitly. Small revisions can appear at the
ERA5/ERA5T boundary when final ERA5 supersedes preliminary values.

## Known issues

- **Lower-stratosphere cold bias 2000-2006.** ERA5.1 was produced as a
  correction for this period.
- **Stream-boundary artefacts.** ERA5 was produced as multiple parallel streams
  that were spliced together. Deeper soil layers and upper atmospheric levels
  spin up more slowly; analyses of long-term trends across stream boundaries
  should account for this.
- **Snow assimilation errors.** September to December 2021 over central Asia.
  July to November 2024 over the Alps. Incorrect observations were assimilated
  in these windows.
- **Back extension (1940-1978).** The back-extension covers 1940-1978 and is
  produced as a separate stream from the main 1979-onwards ERA5. Key caveats:
  - The earlier *preliminary* back extension (also covering 1950-1978)
    suffered from unrealistically intense tropical cyclones and was withdrawn
    on 15 August 2023. Any legacy file labelled "preliminary" should not be
    used; the current final back extension supersedes it.
  - Users combining the back extension with the main stream should expect
    small discontinuities around the 1979 join.
  - Forecast parameters are missing between 00 and 06 UTC on 1 January 1940
    (except step 0), because the first ERA5 forecast was initialised at
    06 UTC that day.
  - Observational input is much sparser before the satellite era (pre-1979),
    and particularly before the radiosonde network matured around 1958.
    Analysis increments are small and the fields are closer to the
    free-running model climate, with reduced trustworthiness in the Southern
    Hemisphere, the tropics, and over oceans.
  - A known regional bias affects surface air temperature over Australia
    prior to about 1970: ERA5 (and JRA-55) show notably higher anomalies
    than GISTEMP and ACORN-SAT.

  Full caveats are documented at
  https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
  and https://confluence.ecmwf.int/display/CKB/The+family+of+ERA5+datasets.

## Licence and attribution

Licence: Licence to use Copernicus Products. This is the licence name listed
on the CDS dataset page and the one you accept when the dataset is added to
your CDS profile.

Full licence text:
https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf

Attribution: derived products must state "Generated using Copernicus Climate
Change Service information [Year]" and cite the DOI and the Hersbach et al.
2020 reference paper. Commercial use is permitted under the licence terms.

## Citation

Dataset:

> Copernicus Climate Change Service (C3S) (2023): ERA5 hourly data on single
> levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate
> Data Store (CDS). DOI: 10.24381/cds.adbb2d47

Reference paper:

> Hersbach, H., Bell, B., Berrisford, P., et al. (2020). The ERA5 global
> reanalysis. Quarterly Journal of the Royal Meteorological Society, 146(730),
> 1999-2049. DOI: 10.1002/qj.3803

## Further reading

- CDS dataset page: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- Time-series sibling dataset: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries
- ECMWF ERA5 data documentation: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
- The ERA5 family overview: https://confluence.ecmwf.int/display/CKB/The+family+of+ERA5+datasets
- ECMWF spatial reference: https://confluence.ecmwf.int/display/CKB/ERA5%3A+What+is+the+spatial+reference
- How to set up the CDS API: https://cds.climate.copernicus.eu/how-to-api
- CDS documentation: https://confluence.ecmwf.int/display/CKB/Climate+Data+Store+%28CDS%29+documentation
- Common CDS errors and splitting requests: https://confluence.ecmwf.int/display/CKB/Common+Error+Messages+for+CDS+Requests
