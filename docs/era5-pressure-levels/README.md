# ERA5 pressure levels

Hourly reanalysis data on 37 atmospheric pressure levels, from 1940 to
present, on a 0.25 degree global grid.

Produced by the Copernicus Climate Change Service (C3S) at ECMWF.

> **Scope of this page.** A getting-started reference for MSc/PhD students
> and early-career researchers. For the authoritative technical detail,
> see the ECMWF documentation linked throughout. See also the
> [ERA5 single levels](../era5-single-levels/README.md) entry for surface
> and near-surface variables.

## At a glance

| Property | Value |
|---|---|
| Variables | 16 (temperature, winds, humidity, geopotential, etc.) |
| Vertical levels | 37 pressure levels, 1 to 1000 hPa |
| Horizontal resolution | 0.25 degrees (approximately 31 km) |
| Temporal resolution | Hourly |
| Temporal coverage | 1940-01-01 to present |
| Latency | ~5 days (ERA5T) or ~2-3 months (final ERA5) |
| Licence | Licence to use Copernicus Products (commercial use allowed) |
| DOI | 10.24381/cds.bd0915c6 |

## What this is

Pressure-level output from the ERA5 reanalysis: atmospheric variables such
as temperature, wind components, humidity, and geopotential, interpolated
from the native 137 model levels onto 37 standard pressure surfaces.

Use it when you need upper-air variables (for example, 500 hPa
geopotential height for synoptic analysis, 850 hPa temperature for
atmospheric rivers work, stratospheric ozone at 10 hPa). For surface and
near-surface variables, use [ERA5 single levels](../era5-single-levels/README.md)
instead.

## Pressure levels

All 16 variables are available on all 37 pressure levels. Levels are
specified as strings in the `pressure_level` field of the request:

```
1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 125, 150, 175, 200, 225, 250,
300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 775, 800, 825, 850,
875, 900, 925, 950, 975, 1000
```

Stratospheric work typically uses 1-100 hPa; upper troposphere 200-400
hPa; lower troposphere 500-1000 hPa; boundary-layer proxies use 850 or
925 hPa.

## Variables

| CDS API name | Long name | Short name | Units |
|---|---|---|---|
| `geopotential` | Geopotential | `z` | m2 s-2 |
| `temperature` | Temperature | `t` | K |
| `u_component_of_wind` | U (eastward) wind | `u` | m s-1 |
| `v_component_of_wind` | V (northward) wind | `v` | m s-1 |
| `specific_humidity` | Specific humidity | `q` | kg kg-1 |
| `relative_humidity` | Relative humidity | `r` | % |
| `vertical_velocity` | Vertical velocity | `w` | Pa s-1 |
| `divergence` | Horizontal divergence | `d` | s-1 |
| `vorticity` | Relative vorticity | `vo` | s-1 |
| `ozone_mass_mixing_ratio` | Ozone mass mixing ratio | `o3` | kg kg-1 |

Six more variables exist (`fraction_of_cloud_cover`,
`potential_vorticity`, `specific_cloud_ice_water_content`,
`specific_cloud_liquid_water_content`, `specific_rain_water_content`,
`specific_snow_water_content`). The full list is in [variables.md](variables.md).

Unlike ERA5 single levels, pressure-level GRIB short names do not start
with digits, so the NetCDF variable name equals the GRIB short name.

To convert `geopotential` to geopotential height in metres, divide by the
standard gravitational acceleration (9.80665 m s-2): `z_in_metres = z / 9.80665`.

## Get data in 5 minutes

1. Register for a free CDS account at https://cds.climate.copernicus.eu/
2. Accept the ERA5 pressure-levels licence in your CDS profile (this is a
   separate licence acceptance from the single-levels dataset).
3. Create `~/.cdsapirc` with your Personal Access Token. See the
   [ERA5 single levels docs](../era5-single-levels/README.md#get-data-in-5-minutes)
   for the exact format and Windows-specific creation steps.
4. `pip install cdsapi xarray netcdf4`
5. Run `python scripts/era5_pressure_levels_download.py`

The default config pulls one hour of 500 hPa temperature over the UK as a
minimal test.

## Things to know

- **All 37 levels are available for every variable.** You are not
  restricted to a subset of levels per variable.
- **Sub-surface extrapolation.** Pressure levels that lie below the model
  orography (for example 1000 hPa over the Tibetan Plateau) contain
  extrapolated values, not physical measurements. Geopotential,
  temperature, and humidity below the surface are mathematical
  continuations produced by ECMWF's standard extrapolation scheme.
- **No accumulated fields.** Unlike single levels, pressure levels only
  contain instantaneous analysis fields. No `step`, no mean-rate, no
  accumulation-timestamp gotchas.
- **Request-size cap multiplies by levels.** A pressure-level request hits
  the CDS per-request cap faster than the equivalent single-levels
  request. Split by year or by level set for large pulls. See the
  [single-levels docs](../era5-single-levels/README.md#queue-behaviour-and-rate-limits)
  for the queue and splitting guidance.
- **ERA5.1 matters for 2000-2006 stratospheric work.** ERA5.1 corrects a
  cold bias in the lower stratosphere and upper troposphere that is
  particularly visible on pressure levels above 100 hPa. Users analysing
  the 2000-2006 window at stratospheric levels should switch to the
  ERA5.1 CDS dataset.
- **ERA5T vs ERA5** (`expver="0001"` vs `"0005"`) applies here too. See
  the [single-levels docs](../era5-single-levels/README.md#era5-versus-era5t)
  for the selection and merging pattern.

## Licence and attribution

Licence: Licence to use Copernicus Products. Commercial use is permitted
with attribution.

Full licence:
https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=terms

Attribution: state "Generated using Copernicus Climate Change Service
information [Year]" and cite the DOI and Hersbach et al. 2020.

## Citation

Dataset:

> Hersbach, H., Bell, B., Berrisford, P., et al. (2023): ERA5 hourly data
> on pressure levels from 1940 to present. Copernicus Climate Change
> Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.bd0915c6

Reference paper:

> Hersbach, H., et al. (2020). The ERA5 global reanalysis. Quarterly
> Journal of the Royal Meteorological Society, 146(730), 1999-2049.
> DOI: 10.1002/qj.3803

## Further reading

- CDS dataset page: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels
- ECMWF ERA5 data documentation: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
- ERA5 single levels in this repo: [../era5-single-levels/README.md](../era5-single-levels/README.md)
- ERA5 model levels on MARS: for raw native-level fields, consult ECMWF Confluence
