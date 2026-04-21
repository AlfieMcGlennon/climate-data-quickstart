# ESGF CMIP6

Direct access to the full CMIP6 archive through the Earth System Grid
Federation: all models, all experiments, all ensemble members, all
variables. No CDS account required.

> **Scope of this page.** A getting-started reference for downloading
> CMIP6 data directly from ESGF. For the simpler CDS route (curated
> subset, fewer models), see [../cmip6/README.md](../cmip6/README.md).
> For the full ESGF documentation, see https://esgf.github.io/.

## When to use this

When you need the full CMIP6 archive rather than the curated CDS subset.
ESGF gives you access to every model, every experiment, every ensemble
member, and every variable. Use it for multi-model comparisons, ensemble
spread analysis, or when you need a specific model or experiment that
the CDS does not carry. No account needed, just HTTP downloads.

## At a glance

| Property | Value |
|---|---|
| Archive | Full CMIP6 output (~100+ models, all MIPs) |
| Access | HTTP download, OPeNDAP, wget scripts, Pangeo cloud mirror |
| Search API | REST (Solr) at `https://esgf-data.dkrz.de/esg-search/search` |
| Auth | None for most CMIP6 HTTP downloads |
| File format | NetCDF-4, one variable per file, CF-compliant |
| Licence | CC BY 4.0 (post-October 2022) |
| Python tools | `requests` (recommended), `intake-esgf`, `esgpull` |

## What ESGF is

The Earth System Grid Federation is a distributed data infrastructure.
Climate modelling centres publish output to local data nodes (DKRZ,
CEDA, IPSL, NCI, and others), which are indexed by federated search
nodes. You search the index, then download files from whichever data
node holds them.

ESGF gives you the complete CMIP6 archive. The CDS hosts a curated
subset of roughly 60 models and common variables. If you need ensemble
members beyond the defaults, MIP tables outside `Amon`/`day`, or
experiments like DAMIP, HighResMIP, or PMIP, ESGF is the route.

**Infrastructure note (mid-2025).** ESGF is transitioning to a new
backend ("ESGF-NG") with Globus authentication. The LLNL node
(`esgf-node.llnl.gov`) shut down on 29 July 2025. The DKRZ, CEDA,
and IPSL Solr-based index nodes remain operational. Code in this repo
targets DKRZ. Check https://esgf.github.io/nodes.html for current
node status.

## Search facets

Every CMIP6 file is tagged with metadata facets. The key ones:

| Facet | What it controls | Example |
|---|---|---|
| `source_id` | Model | `CESM2`, `UKESM1-0-LL` |
| `experiment_id` | Experiment | `historical`, `ssp245` |
| `variable_id` | Variable (CMOR short name) | `tas`, `pr` |
| `table_id` | Frequency and realm | `Amon`, `day`, `Omon` |
| `variant_label` | Ensemble member (ripf) | `r1i1p1f1` |
| `grid_label` | Grid type | `gn` (native), `gr` (regridded) |
| `activity_id` | MIP that defined the experiment | `CMIP`, `ScenarioMIP` |

Full controlled vocabularies: https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html

## Common variables

| variable_id | Long name | Units | Typical table_id |
|---|---|---|---|
| `tas` | Near-surface air temperature | K | Amon, day |
| `tasmax` | Daily maximum near-surface air temperature | K | day |
| `tasmin` | Daily minimum near-surface air temperature | K | day |
| `pr` | Precipitation | kg m-2 s-1 | Amon, day |
| `psl` | Sea level pressure | Pa | Amon, day |
| `hurs` | Near-surface relative humidity | % | Amon, day |
| `sfcWind` | Near-surface wind speed | m s-1 | Amon, day |
| `rsds` | Surface downwelling shortwave radiation | W m-2 | Amon, day |
| `tos` | Sea surface temperature | degC | Omon |
| `clt` | Total cloud cover | % | Amon |

Full variable browser: https://clipc-services.ceda.ac.uk/dreq/mipVars.html

## Key experiments

| experiment_id | Period | Description |
|---|---|---|
| `historical` | 1850-2014 | Observed forcings baseline |
| `ssp126` | 2015-2100 | Low emissions (2.6 W/m2) |
| `ssp245` | 2015-2100 | Middle of road (4.5 W/m2) |
| `ssp370` | 2015-2100 | High emissions (7.0 W/m2) |
| `ssp585` | 2015-2100 | Very high emissions (8.5 W/m2) |
| `piControl` | Centuries | Pre-industrial control |
| `abrupt-4xCO2` | Variable | Abrupt 4x CO2 increase |
| `amip` | 1979-2014 | Atmosphere-only with observed SSTs |

Full list: https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html

## Widely used models

| source_id | Institution | Approx. resolution |
|---|---|---|
| `ACCESS-CM2` | CSIRO-ARCCSS (Australia) | ~250 km |
| `CanESM5` | CCCma (Canada) | ~250 km |
| `CESM2` | NCAR (USA) | ~100 km |
| `EC-Earth3` | EC-Earth Consortium | ~100 km |
| `GFDL-ESM4` | NOAA GFDL (USA) | ~100 km |
| `IPSL-CM6A-LR` | IPSL (France) | ~250 km |
| `MIROC6` | MIROC (Japan) | ~250 km |
| `MPI-ESM1-2-LR` | MPI-M (Germany) | ~250 km |
| `MRI-ESM2-0` | MRI (Japan) | ~100 km |
| `UKESM1-0-LL` | MOHC/NERC (UK) | ~250 km |

Note: UKESM1-0-LL, HadGEM3-GC31-LL, and CNRM-CM6-1 use `r1i1p1f2` as
their flagship member, not `r1i1p1f1`.

## Get data in 5 minutes

No registration required for CMIP6 HTTP downloads from most data nodes.

```bash
pip install requests xarray netcdf4 matplotlib cartopy
python scripts/esgf_cmip6_download.py
```

The default searches ESGF for monthly `tas` from MPI-ESM1-2-LR
historical, downloads one file, and opens it with xarray. Edit the
config block at the top of the script to change model, experiment, or
variable.

## How search and download works

The download script uses the ESGF REST API directly with `requests`.
The pattern is: search for file URLs, then download via HTTP.

**Search** (returns JSON with file metadata and download URLs):

```
https://esgf-data.dkrz.de/esg-search/search?project=CMIP6
  &source_id=CESM2&experiment_id=historical&variable_id=tas
  &table_id=Amon&variant_label=r1i1p1f1&latest=true
  &replica=false&type=File&format=application/solr+json
```

**Download** (plain HTTP, no auth):

```
https://esgf.ceda.ac.uk/thredds/fileServer/.../tas_Amon_CESM2_historical_r1i1p1f1_gn_185001-201412.nc
```

The search response includes a `url` field for each file, a list of
pipe-separated triples (`url|mime_type|service`). Parse for
`HTTPServer` to get download URLs or `OPENDAP` for streaming access.

Always pass `latest=true` and `replica=false` to get the most recent,
non-replicated version.

## File naming convention

```
{variable_id}_{table_id}_{source_id}_{experiment_id}_{variant_label}_{grid_label}_{dates}.nc
```

Example: `tas_Amon_CESM2_historical_r1i1p1f1_gn_185001-201412.nc`

Fixed fields (`fx` table) have no date range. One variable per file.

## Alternative access routes

- **OPeNDAP.** Stream subsets without downloading the full file. Use
  the `OPENDAP` URL from search results with
  `xr.open_dataset(url, chunks={"time": 120})`. Not all data nodes
  have reliable OPeNDAP.
- **Pangeo cloud mirror.** A large subset of CMIP6 as Zarr on Google
  Cloud Storage, searchable via `intake-esm`. No download, no auth,
  very fast for analysis. Not complete.
  Catalogue: https://storage.googleapis.com/cmip6/pangeo-cmip6.csv
- **intake-esgf.** Modern Python client under active development.
  Handles search, download, caching, and loading into xarray.
  https://github.com/esgf2-us/intake-esgf
- **esgpull.** CLI and Python API for managing local ESGF data stores.
  Good for bulk downloads. https://github.com/ESGF/esgf-download

Avoid `esgf-pyclient` (`pyesgf`) for new projects. It still works for
search but is fragile and not actively maintained.

## Things to know

- **Calendars differ per model.** 360-day, 365-day no-leap, proleptic Gregorian. Use xarray's `cftime` handling; `pd.date_range` will silently mismatch. See https://docs.xarray.dev/en/stable/weather-climate.html#non-standard-calendars.
- **Grids differ per model.** Native grids can be rectilinear, cubed-sphere, or tripolar. Multi-model analysis requires regridding (xESMF or CDO).
- **Retracted datasets.** Some CMIP6 output has been retracted. Always use `latest=true` and check the errata service: https://es-doc.github.io/esdoc-errata-client/.
- **"Hot models" caveat.** A subset of CMIP6 models has climate sensitivity above the IPCC AR6 assessed-likely range. Screen or weight the ensemble for impact work.
- **Data node downtime.** Individual nodes go offline. If a download fails, re-search with `distrib=true` to find replicas on other nodes.
- **ESGF-NG transition.** Code that hard-codes `esgf-node.llnl.gov` will break. Target DKRZ or use tools that handle node selection. See https://esgf.github.io/nodes.html.

## Licence and attribution

Licence: CC BY 4.0 for all CMIP6 models (transitioned October 2022).
Terms of use: https://pcmdi.llnl.gov/CMIP6/TermsOfUse/TermsOfUse6-2.html

Attribution: cite the per-model DOI from the CMIP6 Citation Service,
plus the framework paper (Eyring et al. 2016). Include the standard
acknowledgement:

> We acknowledge the World Climate Research Programme, which, through
> its Working Group on Coupled Modelling, coordinated and promoted
> CMIP6. We thank the climate modelling groups for producing and making
> available their model output, the Earth System Grid Federation (ESGF)
> for archiving the data and providing access, and the multiple funding
> agencies that support CMIP6 and ESGF.

## Citation

CMIP6 framework:

> Eyring, V., et al. (2016). Overview of the Coupled Model
> Intercomparison Project Phase 6 (CMIP6) experimental design and
> organization. Geoscientific Model Development, 9, 1937-1958.
> DOI: 10.5194/gmd-9-1937-2016

Per-model citations: https://cera-www.dkrz.de/WDCC/ui/cerasearch/cmip6

## Further reading

- ESGF home: https://esgf.github.io/
- ESGF Search REST API: https://esgf.github.io/esg-search/ESGF_Search_RESTful_API.html
- CMIP6 data users guide: https://pcmdi.llnl.gov/CMIP6/Guide/dataUsers.html
- CMIP6 controlled vocabularies: https://wcrp-cmip.github.io/CMIP6_CVs/docs/CMIP6_experiment_id.html
- Variable browser: https://clipc-services.ceda.ac.uk/dreq/mipVars.html
- CMIP6 errata service: https://es-doc.github.io/esdoc-errata-client/
- CMIP6 via CDS in this repo: [../cmip6/README.md](../cmip6/README.md)
- Quickstart notebook: [../../notebooks/esgf_cmip6_quickstart.ipynb](../../notebooks/esgf_cmip6_quickstart.ipynb)
- Download script: [../../scripts/esgf_cmip6_download.py](../../scripts/esgf_cmip6_download.py)
