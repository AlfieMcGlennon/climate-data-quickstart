# GloFAS historical

Daily global river discharge reanalysis from 1979 to near real time, at
0.1 degree (v3.1) or 0.05 degree (v4.0) resolution.

Produced by the Copernicus Emergency Management Service (CEMS), jointly
by JRC and ECMWF, by driving the LISFLOOD hydrological model with ERA5
forcing.

> **Scope of this page.** A getting-started reference for students and
> practitioners. For deep technical detail see Harrigan et al. 2020 and
> https://www.globalfloods.eu/.

## When to use this

When you need river discharge rather than precipitation or temperature.
GloFAS is the only global gridded discharge reanalysis, so it is the
starting point for any flood risk analysis, hydrological baseline study,
or catchment-scale water balance where you need a long consistent record
of streamflow.

## At a glance

| Property | Value |
|---|---|
| Variable (primary) | `river_discharge_in_the_last_24_hours` (m3/s) |
| Horizontal resolution | 0.05 degrees (v4.0) or 0.1 degrees (v3.1, v2.1) |
| Temporal resolution | Daily |
| Temporal coverage | 1979-01-01 to near real time |
| Coverage | Global land, excluding Antarctica |
| Endpoint | **CEMS Early Warning Data Store (EWDS)**, not the main CDS |
| Dataset ID | `cems-glofas-historical` |
| Licence | Licence to use Copernicus Products (commercial use allowed) |
| DOI | 10.24381/cds.a4fdd6b9 |

## What this is

A global daily river discharge dataset. The LISFLOOD hydrological and
channel-routing model is driven by ERA5 surface and subsurface runoff
to produce discharge (m3/s) at every river pixel on a global grid. It
is the reference hydrological reanalysis underlying the GloFAS
operational flood forecasting system.

Use it when you need consistent historical daily river flow at
catchment scale globally: flood risk work, hydrological model
validation, trends in seasonal flow regimes, water-resource scoping.
Not appropriate for sub-kilometre tributaries or heavily regulated
urban drainage.

## Important: EWDS endpoint, not CDS

GloFAS lives on the Copernicus CEMS Early Warning Data Store (EWDS),
which is a separate platform from the main Climate Data Store (CDS).
You need:

- A **separate EWDS account**: https://ewds.climate.copernicus.eu/
- A **separate Personal Access Token** from your EWDS profile
- The EWDS API URL: `https://ewds.climate.copernicus.eu/api`

A standard CDS account does not grant EWDS access. The same `cdsapi`
Python client works against both, but you must point it at the EWDS
URL and key explicitly.

## Get data in 5 minutes

1. Register at https://ewds.climate.copernicus.eu/
2. Accept the GloFAS dataset licence in your EWDS profile.
3. Generate a Personal Access Token from your EWDS profile page.
4. Set the token as an environment variable (recommended so it is not
   committed to git):
   ```bash
   export EWDS_KEY="<your-ewds-token>"
   ```
5. `pip install cdsapi xarray netcdf4 cfgrib eccodes`
6. Run `python scripts/glofas_download.py`

The default pulls one day of river discharge over a UK bounding box as a
minimal test.

## Things to know

- **Version matters.** v4.0 (0.05 deg) uses `hydrological_model: "lisflood"`.
  v3.1 and v2.1 (0.1 deg) use `htessel_lisflood`. Discharge time series
  are not directly comparable across versions; pick one and stay with it
  in any given analysis.
- **Product type.** `consolidated` for the main reanalysis back-catalogue;
  `intermediate` for the near-real-time tail still driven by ERA5T.
  `intermediate` is superseded by `consolidated` once final ERA5 forcing
  is available.
- **`h` prefix on date keys.** Request keys are `hyear`, `hmonth`, `hday`
  (hydrological year/month/day), not `year`/`month`/`day` as in ERA5.
- **Spin-up caveat.** LISFLOOD requires spin-up for deep groundwater to
  equilibrate. The first 1-2 years (1979-1980) may show residual spin-up
  behaviour in deep-groundwater catchments. Safest to start analyses at
  1981 or later.
- **Regulated rivers are less accurate.** The model represents ~460 lakes
  and ~670 reservoirs explicitly, but smaller reservoirs, diversions,
  and irrigation withdrawals are not resolved. Heavily managed basins
  (US West, Canadian Prairies, much of Asia) have larger bias.
- **Urban and small streams.** Even the v4.0 0.05 degree grid cannot
  resolve sub-kilometre tributaries. Skill rises with catchment size.
- **Calibration coverage is uneven.** LISFLOOD is calibrated against ~2000
  gauged stations globally. Ungauged regions (much of Africa, central
  Asia, parts of South America) inherit parameters via regionalisation
  and have higher uncertainty.
- **ERA5 forcing issues propagate.** Known ERA5 snow-assimilation errors
  (central Asia late 2021, Alps mid-late 2024) can distort GloFAS runoff
  and discharge over those regions and periods.

## Licence and attribution

Licence: Licence to use Copernicus Products, with additional Copernicus
Emergency Management Service terms. Commercial use permitted with
attribution.

Attribution: cite the dataset DOI and the Harrigan et al. 2020 reference
paper. State that the product is "derived from Copernicus Emergency
Management Service information".

## Citation

Dataset:

> Copernicus Emergency Management Service (CEMS): River discharge and
> related historical data from the Global Flood Awareness System.
> Copernicus CEMS Early Warning Data Store (EWDS).
> DOI: 10.24381/cds.a4fdd6b9

Reference paper:

> Harrigan, S., Zsoter, E., Alfieri, L., Prudhomme, C., Salamon, P.,
> Wetterhall, F., Barnard, C., Cloke, H., and Pappenberger, F. (2020):
> GloFAS-ERA5 operational global river discharge reanalysis 1979 to
> present. Earth System Science Data, 12, 2043-2060.
> DOI: 10.5194/essd-12-2043-2020

## Further reading

- EWDS dataset page: https://ewds.climate.copernicus.eu/datasets/cems-glofas-historical
- GloFAS portal: https://www.globalfloods.eu/
- Operational flood dashboard: https://global-flood.emergency.copernicus.eu/
- ERA5 single levels in this repo: [../era5-single-levels/README.md](../era5-single-levels/README.md)
- LISFLOOD model documentation: https://ec-jrc.github.io/lisflood-model/
