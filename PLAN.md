# Climate data toolkit: working plan

Living document. Update as we go.

## Current phase

**v1.1 complete.** 17 datasets shipped across five categories. Streamlit
desktop app fully functional with home page, dataset search, interactive
explorer, streaming preview, and ESGF multi-model/ensemble comparison.
Packaging (setup scripts, requirements, environment.yml, README) updated
and ready for distribution.

Two datasets remain deferred: UKCP18 (needs CEDA account) and GPWv4
(needs NASA Earthdata account).

## Operating decisions (from kick-off Q&A, 2026-04-19)

1. **Template build** - Autonomous end-to-end build of ERA5 Single Levels with
   self-review loops at each stage (research brief, docs, script, notebook, test,
   review). User reviews the finished template before the pipeline runs on the
   other 13.

2. **Failure handling** - Auto-retry with fixes: up to 3 test-fix cycles and 2
   review cycles per dataset. After max retries, log the failure, mark dataset
   as "needs human review" in this file, and continue to the next dataset. The
   pipeline does not block on a single failure.

3. **Commits** - One commit per dataset after it passes review. Standardised
   commit message: `Add {dataset-slug}: {short description}`. Clean history,
   easy to revert individual datasets.

4. **Earth Data Hub fallback** - If user cannot locate reference code from the
   quantum pipeline project, the researcher agent works EDH like any other
   dataset from official docs. Pipeline does not block.

## Dataset queue

| # | Slug | Name | Access | Status |
|---|------|------|--------|--------|
| 1 | era5-single-levels | ERA5 single levels | CDS API | shipped |
| 2 | era5-pressure-levels | ERA5 pressure levels | CDS API | shipped |
| 3 | era5-land | ERA5-Land | CDS API | shipped |
| 4 | era5-daily-stats | ERA5 daily statistics | CDS API | shipped |
| 5 | earth-data-hub | Earth Data Hub | Zarr streaming | shipped |
| 6 | hadcet | HadCET | Direct HTTP | shipped |
| 7 | hadcrut5 | HadCRUT5 | Direct HTTP | shipped |
| 8 | cmip6 | CMIP6 (CDS) | CDS API | shipped |
| 9 | ukcp18 | UKCP18 | CEDA | built: awaiting CEDA credentials for testing |
| 10 | glofas | GloFAS historical | EWDS API | shipped |
| 11 | ghcnd | GHCNd | Direct HTTP | shipped |
| 12 | e-obs | E-OBS | CDS API | shipped |
| 13 | gpw-population | GPWv4 | NASA Earthdata | built: awaiting Earthdata credentials for testing |
| 14 | chirps | CHIRPS | Direct HTTP | shipped |
| 15 | arco-era5 | ARCO-ERA5 | Cloud Zarr (GCS) | shipped (v1.1) |
| 16 | ecmwf-open-data | ECMWF Open Data | Direct HTTP | shipped (v1.1) |
| 17 | c3s-seasonal | C3S seasonal | CDS API | shipped (v1.1) |
| 18 | esgf-cmip6 | ESGF CMIP6 (full archive) | Direct HTTP | shipped (v1.1) |
| 19 | edh-explorer | EDH catalogue explorer | Zarr streaming | shipped (v1.1) |

## App features (Streamlit desktop)

The app at `app/main.py` provides a full GUI for all 17 datasets:

- **Home page** with dataset cards, search-by-topic, 3-step quick-start guide
- **Download mode** with per-dataset forms, bbox presets, time range pickers
- **Explore mode** to open any NetCDF/GRIB/CSV and get interactive maps, time
  series, data quality metrics, and reproducible code snippets
- **Streaming preview** for EDH and ARCO-ERA5 (load a Zarr slice without
  downloading)
- **ESGF CMIP6** with three modes: single model, ensemble members (r1-rN of
  one model), and multi-model comparison
- **Credential panel** in sidebar showing configured/missing credentials with
  setup instructions
- **Navigation** via full-width sidebar buttons (Home / Explore / Download)
- **Category pills** for organising datasets into ERA5, Streaming, Models,
  Observations, Forecast
- Custom Streamlit theme (`.streamlit/config.toml`) with dark sidebar

## Access patterns

### Pattern A: Copernicus CDS API
- Used for: ERA5 (all), CMIP6, E-OBS, C3S seasonal
- Python package: `cdsapi`
- Credentials: `~/.cdsapirc`

### Pattern B: Direct download
- Used for: HadCET, HadCRUT5, GHCNd, CHIRPS, ECMWF Open Data, ESGF CMIP6
- Python package: `requests`, `ecmwf.opendata` (ECMWF Open Data)
- Credentials: none (all open access)

### Pattern C: Custom Python API
- Used for: Earth Data Hub, EDH explorer
- Python package: `xarray` + `zarr` + `fsspec`
- Credentials: netrc entry for `data.earthdatahub.destine.eu`

### Pattern D: Cloud-native Zarr
- Used for: ARCO-ERA5
- Python package: `xarray` + `zarr` + `gcsfs`
- Credentials: none (public GCS bucket)

### Pattern E: EWDS API
- Used for: GloFAS
- Python package: `cdsapi` (EWDS endpoint)
- Credentials: `EWDS_KEY` environment variable

## Packaging

- `setup.bat` / `setup.sh` - creates `.venv/`, installs from `requirements.txt`
- `run_app.bat` / `run_app.sh` - activates venv, launches Streamlit
- `environment.yml` - conda alternative (cartopy installs more reliably via conda)
- `requirements.txt` - all pip dependencies pinned to minimum compatible versions
- User only needs Python 3.10+ installed; everything else is handled by setup

## Known blockers

1. **CEDA account** - register at https://services.ceda.ac.uk/cedasite/register/info/
   before UKCP18 can be built
2. **NASA Earthdata account** - register at https://urs.earthdata.nasa.gov/
   before GPWv4 can be built

## Quality gates

Before a dataset is considered "done":
- All `[VERIFY]` tags resolved or explicitly deferred to human review
- Reviewer agent score of 7 or higher
- Test log shows clean script run and clean notebook run
- Variable names identical across docs, script, and notebook
- Licence stated with attribution requirements
- Dataset added to root README.md overview table

## What is next

- Commit all uncommitted work (significant app improvements, 5 new datasets,
  packaging updates all sitting in working tree)
- End-to-end smoke test on a fresh clone
- Editorial pass on docs (user's own voice, "when I reach for this" lines)
- LinkedIn post framing: "built this for myself, sharing in case useful"
- Consider a tutorial/walkthrough section in the app or docs
- UKCP18 and GPWv4 artefacts built; run download tests once credentials are configured
