# CMIP6

Multi-model, multi-scenario climate projections from the Coupled Model
Intercomparison Project Phase 6.

Served on the Copernicus Climate Data Store as a curated subset of the
full ESGF archive.

> **Scope of this page.** A getting-started reference for MSc/PhD
> students who want to pull a single CMIP6 model run from the CDS. For
> research-grade ensemble work, `intake-esm` plus the Pangeo Google Cloud
> Zarr mirror or direct ESGF access (`esgf-pyclient`) are more
> appropriate. Background on the CMIP6 design is in Eyring et al. (2016).

## At a glance

| Property | Value |
|---|---|
| Dataset ID (CDS) | `projections-cmip6` |
| Models | ~56-60 on CDS (~100+ on ESGF) |
| Experiments | historical (1850-2014) plus SSPs (2015-2100) |
| Variables | ~55 on CDS, surface and pressure levels |
| Temporal resolution | monthly, daily, fixed |
| Horizontal resolution | varies by model, typically 80-250 km |
| Output | zipped NetCDF |
| Licence | CC BY 4.0 for most models (post-Oct 2022) |
| DOI (CDS) | 10.24381/cds.c866074c |

## What this is

CMIP6 is a coordinated set of global climate model simulations produced
under a common protocol so results can be compared across modelling
centres. The core use case for this repo is **projections of future
climate under different emission scenarios** (Shared Socioeconomic
Pathways), plus the paired historical simulation that anchors each
model against observations.

Use it when you need future climate projections at the global-to-
regional scale: plausible ranges of 21st-century warming, regional
precipitation change, sea-ice decline, etc. For reanalysis of observed
weather, use [ERA5](../era5-single-levels/README.md). For regional
high-resolution UK projections, see the UKCP18 entry (when credentials
available).

## Scenarios (SSP experiments)

Short meaning of the SSP codes used in the CDS request:

| Code | Radiative forcing at 2100 | Narrative |
|---|---|---|
| `ssp1_1_9` / `ssp1_2_6` | 1.9 / 2.6 W/m2 | Low emissions, Paris-compatible |
| `ssp2_4_5` | 4.5 W/m2 | Middle-of-the-road, moderate mitigation |
| `ssp3_7_0` | 7.0 W/m2 | Regional rivalry, weak mitigation |
| `ssp4_3_4` / `ssp4_6_0` | 3.4 / 6.0 W/m2 | Inequality pathways |
| `ssp5_3_4os` | 3.4 W/m2 (overshoot) | Fossil, then aggressive mitigation |
| `ssp5_8_5` | 8.5 W/m2 | Fossil-fuelled, high emissions (upper end) |

Plus `historical` (1850-2014) for the observed-forcings baseline.

## Common variables

CMIP6 uses short names from the CMIP6 MIP tables (CMOR). The CDS request
strings are the longer snake_case equivalents.

| CDS API name | CMIP6 short | Units |
|---|---|---|
| `near_surface_air_temperature` | `tas` | K |
| `daily_maximum_near_surface_air_temperature` | `tasmax` | K |
| `daily_minimum_near_surface_air_temperature` | `tasmin` | K |
| `precipitation` | `pr` | kg m-2 s-1 (multiply by 86400 for mm/day) |
| `sea_level_pressure` | `psl` | Pa |
| `sea_surface_temperature` | `tos` | degC (not K, unlike ERA5) |
| `near_surface_wind_speed` | `sfcWind` | m s-1 |
| `sea_ice_area_percentage_ocean_grid` | `siconc` | % |

When you open a downloaded file, the variable appears under the CMIP6
short name (`tas`), not the CDS request string.

## Get data in 5 minutes

1. Register for a free CDS account at https://cds.climate.copernicus.eu/
2. Accept the CMIP6 licence in your CDS profile (separate from ERA5).
3. Create `~/.cdsapirc` with your Personal Access Token. See the
   [ERA5 single levels docs](../era5-single-levels/README.md#get-data-in-5-minutes)
   for the format.
4. `pip install cdsapi xarray netcdf4`
5. Run `python scripts/cmip6_download.py`

The default pulls one model (MPI-ESM1-2-LR), one scenario (SSP5-8.5),
monthly `near_surface_air_temperature` over a UK bounding box for 2050.

## Things to know

- **One model, one scenario by default.** Asking for "all models" x "all
  scenarios" x "all variables" is a huge request. For a quickstart, stay
  minimal; scale up when you know what you need.
- **Ensemble member (variant label).** A string like `r1i1p1f1`
  (realisation-initialisation-physics-forcing). `r1i1p1f1` is the usual
  flagship but UKESM1-0-LL, HadGEM3-GC31-LL, CNRM-CM6-1 and others use
  `r1i1p1f2` or similar because their forcing implementation differs.
  When a request silently drops a model, this is often why.
- **Calendars differ per model.** Some use 360-day years, some 365-day
  no-leap, some proleptic Gregorian. Use xarray's `cftime` handling or
  `xr.convert_calendar` when comparing models. Naive `pd.date_range`
  will silently mismatch.
- **Grids differ per model.** Atmospheric grids are regridded on
  delivery for most variables, but ocean variables often use curvilinear
  native grids. Multi-model analysis requires regridding (xESMF or CDO).
- **Unit conventions follow CMIP6/CF, not ECMWF.** Precipitation is a
  flux in kg m-2 s-1, not accumulated metres. SST is degC, not K. Always
  read the `units` attribute before plotting.
- **SSP naming: `ssp5_8_5` not `ssp585`.** The CDS form uses underscored
  numbers; other tools and papers use the short form.
- **CDS is a subset of ESGF.** Variables outside the `Amon`/`day` tables,
  ensemble members beyond the defaults, or MIPs beyond ScenarioMIP (e.g.
  DAMIP, HighResMIP) need ESGF directly. Consider `esgf-pyclient` or
  `intake-esm` for that.
- **"Hot models" caveat.** A subset of CMIP6 models has higher climate
  sensitivity than assessed-likely ranges in IPCC AR6. For impact work,
  screen or weight the ensemble rather than take an unweighted mean.

## Licence and attribution

Licence: CC BY 4.0 for most models (transitioned October 2022); a few
older downloads may carry stricter terms. Check each file's global
attributes or the CMIP6 Citation Service.

Attribution: cite the per-model DOI from the Citation Service, plus the
CMIP6 framework paper (Eyring et al. 2016). For CDS access, also cite
the CDS dataset DOI.

Suggested acknowledgement text:

> We acknowledge the World Climate Research Programme, which, through
> its Working Group on Coupled Modelling, coordinated and promoted CMIP6.
> We thank the climate modelling groups for producing and making
> available their model output, the Earth System Grid Federation (ESGF)
> for archiving the data and providing access, and the multiple funding
> agencies that support CMIP6 and ESGF.

## Citation

CMIP6 framework:

> Eyring, V., et al. (2016). Overview of the Coupled Model
> Intercomparison Project Phase 6 (CMIP6) experimental design and
> organization. Geoscientific Model Development, 9, 1937-1958.
> DOI: 10.5194/gmd-9-1937-2016

ScenarioMIP (SSP experiments):

> O'Neill, B. C., et al. (2016). The Scenario Model Intercomparison
> Project (ScenarioMIP) for CMIP6. Geoscientific Model Development, 9,
> 3461-3482. DOI: 10.5194/gmd-9-3461-2016

CDS dataset:

> Copernicus Climate Change Service (C3S) Climate Data Store (CDS).
> CMIP6 climate projections. DOI: 10.24381/cds.c866074c

Per-model citations: use the CMIP6 Citation Service at
https://cera-www.dkrz.de/WDCC/ui/cerasearch/cmip6

## Further reading

- CDS dataset page: https://cds.climate.copernicus.eu/datasets/projections-cmip6
- CMIP6 project home: https://pcmdi.llnl.gov/CMIP6/
- CMIP6 Guide for Data Users: https://pcmdi.llnl.gov/CMIP6/Guide/dataUsers.html
- CMIP6 Terms of Use: https://pcmdi.llnl.gov/CMIP6/TermsOfUse/TermsOfUse6-1.html
- Citation Service: https://cera-www.dkrz.de/WDCC/ui/cerasearch/cmip6
- For research-grade ensemble access: https://intake-esm.readthedocs.io/
