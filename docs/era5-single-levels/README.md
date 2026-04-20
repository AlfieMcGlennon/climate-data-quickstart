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

Use it when you need a long, global, physically consistent record of weather
at hourly resolution. Typical uses: climate baselines, forcing for land-surface
models, validating regional models, bias-correcting projections.

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

The 1940-1958 segment is a back-extension and is documented as less reliable
than the main 1959-present stream, especially before the satellite era.

## Variables

ERA5 single levels contains more than 250 variables. The ten most commonly
used are listed below. The full categorised list is in
[variables.md](variables.md).

| CDS API name | Long name | GRIB short name | Units |
|---|---|---|---|
| `2m_temperature` | 2 metre temperature | `2t` | K |
| `2m_dewpoint_temperature` | 2 metre dewpoint temperature | `2d` | K |
| `10m_u_component_of_wind` | 10 metre U wind component | `10u` | m s-1 |
| `10m_v_component_of_wind` | 10 metre V wind component | `10v` | m s-1 |
| `mean_sea_level_pressure` | Mean sea level pressure | `msl` | Pa |
| `surface_pressure` | Surface pressure | `sp` | Pa |
| `total_precipitation` | Total precipitation | `tp` | m |
| `sea_surface_temperature` | Sea surface temperature | `sst` | K |
| `surface_solar_radiation_downwards` | Surface solar radiation downwards | `ssrd` | J m-2 |
| `total_cloud_cover` | Total cloud cover | `tcc` | 0-1 |

### Naming quirk

The CDS API accepts human-readable snake_case names (`2m_temperature`) but the
underlying GRIB records use short names (`2t`). When opening a downloaded file
with `xarray` or `cfgrib`, variables appear under the short names, not the
request names. This repo uses CDS API names in scripts and short names when
reading the file, and documents both.

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

### Queue behaviour

Requests are queued server-side. A small single-day request usually completes
within minutes. Large multi-decade or multi-variable requests can take hours.
Queue position is visible at https://cds.climate.copernicus.eu/requests.

### Output formats

GRIB is the default and fastest format. NetCDF4 is also supported via
`data_format: "netcdf"` but is marked as experimental by the CDS and large
requests may be split into multiple files.

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
- **Back extension (1940-1958).** Less reliable than the main stream,
  particularly before the satellite era. [VERIFY]

## Licence and attribution

Licence: Licence to use Copernicus Products (the "Copernicus licence"). [VERIFY:
the CDS page references this licence; CC-BY-4.0 is sometimes cited as
effectively compatible.]

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
- ECMWF ERA5 data documentation: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
- How to set up the CDS API: https://cds.climate.copernicus.eu/how-to-api
- Splitting long requests: https://confluence.ecmwf.int/display/CKB/Climate+Data+Store+%28CDS%29+documentation
