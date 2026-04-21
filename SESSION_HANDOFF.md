# Session handoff: climate-data-quickstart

Read this first if you are a new Claude Code session picking up work on
this repo. Last updated 2026-04-21.

## One-line summary

A curated reference repo for 17 climate and weather datasets (docs,
download scripts, quickstart notebooks) plus a local-only Streamlit
desktop app with interactive explorer, streaming preview, and ESGF
multi-model comparison.

## Who this is for

MSc/PhD climate students, early-career climate scientists, and climate
risk analysts. User (Alfie) is building it as a portfolio piece and a
useful resource. British English throughout. See `CLAUDE.md` for the
full style and source rules.

## Current state

### Datasets shipped: 17

Each has `docs/{slug}/README.md`, `scripts/{slug}_download.py`,
`notebooks/{slug}_quickstart.ipynb` (except EDH explorer which is
app-only).

| Category | Datasets |
|----------|----------|
| ERA5 | single levels, pressure levels, land, daily statistics |
| Streaming | Earth Data Hub, ARCO-ERA5, EDH catalogue explorer |
| Models | CMIP6 (CDS), ESGF CMIP6 (full archive), C3S seasonal |
| Observations | HadCET, HadCRUT5, GHCNd, E-OBS, CHIRPS |
| Forecast | ECMWF Open Data, GloFAS |

Two more are deferred: UKCP18 (needs CEDA account), GPWv4 (needs NASA
Earthdata account).

### Streamlit app

The app (`app/main.py`) is fully functional with:

- **Home page** (`app/dataset_pages/home.py`): 17 dataset cards with
  access-method badges, search-by-topic, 3-step quick-start guide,
  clickable cards that navigate to the download form
- **Download mode**: per-dataset forms with shared widgets (bbox presets,
  year range, output dir). Category pills + radio for dataset selection.
- **Explore mode** (`app/dataset_pages/explore.py`): load any
  NetCDF/GRIB/CSV, see data quality metrics, interactive maps, time
  series, code snippets
- **Streaming**: EDH and ARCO-ERA5 have "Stream & preview" + "Show code"
  buttons. Preview loads a Zarr slice without downloading a file.
- **ESGF CMIP6** (`app/dataset_pages/esgf_cmip6.py`): three modes -
  single model download, ensemble members (r1-rN of one model), and
  multi-model comparison. Post-download panel has time series tab and
  spatial maps tab.
- **Credential panel**: sidebar shows green badges for configured
  credentials, expandable setup instructions for missing ones
- **Navigation**: full-width sidebar buttons (Home / Explore / Download)
  with active state highlighting
- **Theme**: custom `.streamlit/config.toml` with dark sidebar,
  Inter font, JetBrains Mono code font

### Packaging

- `setup.bat` / `setup.sh` - one-time venv creation + pip install
- `run_app.bat` / `run_app.sh` - launch the app
- `environment.yml` - conda alternative
- `requirements.txt` - 20 packages including `ecmwf-opendata`,
  `nc-time-axis`, `gcsfs` (all verified installed and working)
- `README.md` - updated for 17 datasets, quick-start front and centre

### What is NOT committed

As of this handoff, there is a large amount of uncommitted work in the
working tree. Run `git status` to see the full list. Key changes:

- 5 new dataset modules in `app/dataset_pages/` (arco_era5, c3s_seasonal,
  ecmwf_open_data, esgf_cmip6, edh_explorer)
- `app/dataset_pages/home.py` (new landing page with cards and search)
- `app/dataset_pages/explore.py` (new file explorer)
- Significant modifications to `app/main.py`, `app/forms.py`,
  `app/credentials.py`, and all existing dataset page modules
- `.streamlit/config.toml` (custom theme)
- New docs, scripts, notebooks for the 5 new datasets
- Updated `requirements.txt`, `environment.yml`, `setup.bat`, `setup.sh`
- Updated `README.md`, `PLAN.md`, this file

## Repo layout

```
climate-data-quickstart/
  CLAUDE.md                    # Style rules, access patterns, notebook standard
  PLAN.md                      # Working plan with dataset queue and status
  SESSION_HANDOFF.md           # This file
  README.md                    # Public README with quick-start
  requirements.txt / environment.yml
  setup.bat / setup.sh         # One-time setup
  run_app.bat / run_app.sh     # Launch app

  app/
    main.py                    # Streamlit entry point, sidebar, routing
    credentials.py             # Credential status checks (UI-friendly)
    forms.py                   # Shared widgets, result panel, interactive plots
    runner.py                  # Dispatcher to scripts/*_download
    dataset_pages/
      __init__.py              # DATASETS registry, CATEGORIES, DATASET_INFO
      home.py                  # Landing page with cards and search
      explore.py               # File explorer for existing downloads
      era5_single_levels.py    # ... one module per dataset
      esgf_cmip6.py            # Has render_mode_selector() for outside-form radio
      ...

  scripts/                     # Per-dataset download scripts
  notebooks/                   # Per-dataset quickstart notebooks
  docs/                        # Per-dataset README + variables.md
  common/                      # Shared helpers (credentials, plotting)

  .streamlit/config.toml       # Custom theme
  .claude/agents/              # researcher.md, tester.md, reviewer.md
  .claude/skills/              # dataset-pipeline orchestration skill
  .research/                   # Research briefs (gitignored)
```

## Architecture notes

### Layered design

```
Streamlit app  ->  scripts/*_download.download()  ->  cdsapi / requests / xarray
     ^
notebooks/*.ipynb  (same download() functions, interactive)
```

The app is additive. Scripts and notebooks work independently.

### Five access patterns

- CDS API (`cdsapi`, `~/.cdsapirc`): ERA5 family, CMIP6, E-OBS, C3S
- Direct HTTP (`requests`): HadCET, HadCRUT5, GHCNd, CHIRPS, ESGF
- ECMWF client (`ecmwf.opendata`): ECMWF Open Data
- Zarr streaming (`xarray` + `fsspec`/`gcsfs`): EDH, ARCO-ERA5
- EWDS API (`cdsapi` EWDS endpoint): GloFAS

### ESGF multi-model / ensemble

`_build_multi_model_ts()` in `main.py` handles both multi-model and
single-model ensemble runs. It detects which case based on the number
of unique model names in the downloaded files, then labels the
concatenation dimension as "model" or "member" accordingly.

### Credential checks

`app/credentials.py` checks file existence and netrc entries only. It
never reads credential strings. The sidebar renders green badges for
configured credentials and expandable instructions for missing ones.

### Platform: Windows

User is on Windows 11 with Python 3.12. Bash in Claude Code is
MSYS-style. The netrc file is `~/_netrc` on Windows (File Explorer
does not allow leading-dot filenames). Both `~/.netrc` and `~/_netrc`
are checked.

## Credential status

- CDS: configured (`~/.cdsapirc`)
- EDH: configured (`~/_netrc`)
- NASA Earthdata: NOT configured
- CEDA: NOT configured
- EWDS (GloFAS): NOT configured

## What is next

1. **Commit** the large batch of uncommitted work
2. **Smoke test** on a fresh clone (setup.bat, run_app.bat, click through)
3. **Editorial pass** on docs (user's own voice per dataset)
4. **LinkedIn post** framing: "built this for myself, sharing in case useful"
5. **Tutorial section** possibly (user mentioned, not decided)
6. UKCP18 and GPWv4 when credentials available

## Key user preferences

- British English, no em dashes, no banned words, sentence-case headings
- Plan first, then build. Major decisions in PLAN.md.
- Primary sources only for technical claims. `[VERIFY]` for uncertain facts.
- Short, direct communication. No filler.
- Prefers back-and-forth planning before building
- User is on Windows, works with ERA5/CDS/HPC, has adjacent "quantum
  pipeline" project using Earth Data Hub
- Persistent memory at:
  `C:\Users\alfie\.claude\projects\C--climate-data-climate-data-quickstart\memory\`
