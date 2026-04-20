# ERA5-Land

Hourly land-surface reanalysis at 0.1 degree (~9 km) resolution, from 1950
to present.

Produced by the Copernicus Climate Change Service (C3S) at ECMWF.

> **Scope of this page.** A getting-started reference for MSc/PhD students
> and early-career researchers. For the authoritative technical detail,
> see the ECMWF documentation linked throughout. See also the
> [ERA5 single levels](../era5-single-levels/README.md) entry for
> lower-resolution but broader-coverage atmospheric variables.

## At a glance

| Property | Value |
|---|---|
| Variables | ~50 land-surface variables (temperatures, moisture, snow, fluxes) |
| Horizontal resolution | 0.1 degrees (approximately 9 km) |
| Temporal resolution | Hourly |
| Temporal coverage | 1950-01-01 to present |
| Coverage | Land only; oceans masked |
| Latency | ~2-3 months (final) |
| Licence | Licence to use Copernicus Products (commercial use allowed) |
| DOI | 10.24381/cds.e2161bac |

## What this is

A land-surface reanalysis derived from ERA5 atmospheric forcing,
downscaled to approximately 9 km by the H-TESSEL land-surface scheme.
Finer spatial detail than the parent ERA5 single levels (0.25 degrees),
but with a narrower set of variables (land-surface only) and a later
start year (1950 vs 1940).

Use it when you need higher-resolution land-surface data than ERA5
provides: regional hydrology, soil moisture, snow depth, catchment-scale
surface energy fluxes. For global ocean-atmosphere variables or dates
before 1950, use [ERA5 single levels](../era5-single-levels/README.md)
instead.

## Variables

| CDS API name | NetCDF name | Long name | Units |
|---|---|---|---|
| `2m_temperature` | `t2m` | 2 metre temperature | K |
| `2m_dewpoint_temperature` | `d2m` | 2 metre dewpoint temperature | K |
| `skin_temperature` | `skt` | Skin temperature (land surface) | K |
| `soil_temperature_level_1` | `stl1` | Soil temperature, 0-7 cm | K |
| `volumetric_soil_water_layer_1` | `swvl1` | Soil moisture, 0-7 cm | m3 m-3 |
| `snow_depth_water_equivalent` | `sd` | Snow water equivalent | m |
| `total_precipitation` | `tp` | Total precipitation | m |
| `surface_solar_radiation_downwards` | `ssrd` | Downward shortwave at surface | J m-2 |
| `surface_latent_heat_flux` | `slhf` | Latent heat flux | J m-2 |
| `surface_sensible_heat_flux` | `sshf` | Sensible heat flux | J m-2 |

The full ~50 variable list, grouped by category, is in
[variables.md](variables.md).

Variable naming conventions follow ERA5 single levels: CDS API names are
snake_case; NetCDF names rewrite leading-digit GRIB names (`2t` -> `t2m`).

## Get data in 5 minutes

1. Register for a free CDS account at https://cds.climate.copernicus.eu/
2. Accept the ERA5-Land licence in your CDS profile (separate from the
   single-levels and pressure-levels licences).
3. Create `~/.cdsapirc` with your Personal Access Token. See the
   [ERA5 single levels docs](../era5-single-levels/README.md#get-data-in-5-minutes)
   for the exact format and Windows-specific creation steps.
4. `pip install cdsapi xarray netcdf4`
5. Run `python scripts/era5_land_download.py`

The default config pulls one hour of 2 metre temperature over the UK.

## Things to know

- **Finer resolution, same physics.** ERA5-Land is derived from ERA5 - no
  independent data assimilation. Errors and biases in ERA5 propagate into
  ERA5-Land. It is a downscaling, not a reanalysis in its own right.
- **Potential evaporation redefinition (18 Nov 2021).** Before this date,
  `potential_evaporation` in ERA5-Land was reference-grass
  evapotranspiration (as in ERA5). After this date it is open-water (pan)
  evaporation. Do not compare `pev` across that boundary. Reference:
  https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation
- **Monthly accumulated data error (Sep 2022 to Feb 2024).** The monthly-
  means product contained incorrect accumulated values in this window;
  workaround is to use the monthly-by-hour-of-day product at 00:00 and
  re-aggregate.
- **Antarctic snow anomaly.** Unrealistically low snow depths over the
  eastern Antarctic ice sheet due to an outdated glacier mask. Not
  suitable for Antarctic snow analysis without correction.
- **MIR interpolation change (1 Jan 2020).** Small discontinuities in
  high-orography and coastal pixels.
- **Lapse-rate correction on temperature/humidity only.** Precipitation,
  radiation and wind are bilinearly interpolated from ERA5 without
  correction; artefacts over steep terrain are common.
- **No bounding-box limit beyond the global grid.** Use the standard
  `[north, west, south, east]` format.

## Licence and attribution

Licence: Licence to use Copernicus Products. Commercial use is permitted
with attribution.

Full licence:
https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf

Attribution: state "Generated using Copernicus Climate Change Service
information [Year]" and cite the DOI and Munoz-Sabater et al. 2021.

## Citation

Dataset:

> Munoz-Sabater, J. (2019). ERA5-Land hourly data from 1950 to present.
> Copernicus Climate Change Service (C3S) Climate Data Store (CDS).
> DOI: 10.24381/cds.e2161bac

Reference paper:

> Munoz-Sabater, J., Dutra, E., Agusti-Panareda, A., et al. (2021). ERA5-
> Land: a state-of-the-art global reanalysis dataset for land
> applications. Earth System Science Data, 13, 4349-4383.
> DOI: 10.5194/essd-13-4349-2021

## Further reading

- CDS dataset page: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land
- ECMWF ERA5-Land data documentation: https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation
- ERA5 single levels in this repo: [../era5-single-levels/README.md](../era5-single-levels/README.md)
