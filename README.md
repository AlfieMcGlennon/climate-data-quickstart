# Climate data quickstart

A curated, practical reference for climate and weather datasets. One
entry per dataset: a docs page you can read in ten minutes, a download
script you can copy, and a quickstart notebook that pulls a small
example end-to-end.

Aimed at MSc/PhD students, early-career climate scientists, and climate
risk analysts who want to get going on a real dataset without reading
the full provider documentation first.

## Datasets

| # | Dataset | Coverage | Access | Notebook |
|---|---|---|---|---|
| 1 | [ERA5 single levels](docs/era5-single-levels/README.md) | Global, hourly, 1940-present, 0.25 deg | CDS API | [notebook](notebooks/era5_single_levels_quickstart.ipynb) |
| 2 | [ERA5 pressure levels](docs/era5-pressure-levels/README.md) | Global, hourly, 37 pressure levels | CDS API | [notebook](notebooks/era5_pressure_levels_quickstart.ipynb) |
| 3 | [ERA5-Land](docs/era5-land/README.md) | Land-only, hourly, 0.1 deg, 1950-present | CDS API | [notebook](notebooks/era5_land_quickstart.ipynb) |
| 4 | [ERA5 daily statistics](docs/era5-daily-stats/README.md) | Pre-computed daily aggregates of ERA5 | CDS API | [notebook](notebooks/era5_daily_stats_quickstart.ipynb) |
| 5 | [Earth Data Hub](docs/earth-data-hub/README.md) | Streaming ERA5, CMIP6, DEM via Zarr | xarray + zarr | [notebook](notebooks/earth_data_hub_quickstart.ipynb) |
| 6 | [HadCET](docs/hadcet/README.md) | Central England, monthly since 1659 | Direct download | [notebook](notebooks/hadcet_quickstart.ipynb) |
| 7 | [HadCRUT5](docs/hadcrut5/README.md) | Global, monthly, 5 deg, 1850-present | Direct download | [notebook](notebooks/hadcrut5_quickstart.ipynb) |
| 8 | [CMIP6](docs/cmip6/README.md) | Multi-model climate projections, SSPs | CDS API | [notebook](notebooks/cmip6_quickstart.ipynb) |
| 9 | UKCP18 | UK high-resolution projections | CEDA | deferred (needs CEDA account) |
| 10 | [GloFAS historical](docs/glofas/README.md) | Global daily river discharge, 1979-present | CEMS EWDS | [notebook](notebooks/glofas_quickstart.ipynb) |
| 11 | [GHCNd](docs/ghcnd/README.md) | Daily station observations, ~100k stations | Direct download | [notebook](notebooks/ghcnd_quickstart.ipynb) |
| 12 | [E-OBS](docs/e-obs/README.md) | European gridded daily observations | CDS API | [notebook](notebooks/e_obs_quickstart.ipynb) |
| 13 | GPWv4 | Global gridded population | NASA Earthdata | deferred (needs Earthdata account) |
| 14 | [CHIRPS](docs/chirps/README.md) | Tropical-subtropical daily precipitation | Direct download | [notebook](notebooks/chirps_quickstart.ipynb) |

## Installation

```bash
git clone https://github.com/<your-user>/climate-data-quickstart.git
cd climate-data-quickstart
pip install -r requirements.txt
```

Some datasets need extra packages (for example `cfgrib` and `eccodes`
for GloFAS GRIB output, or `zarr` and `aiohttp` for Earth Data Hub).
Each dataset's docs page lists what you need.

## Credentials

Datasets fall into three access patterns:

- **Copernicus CDS** (ERA5 family, CMIP6, E-OBS): free account at
  https://cds.climate.copernicus.eu/, Personal Access Token saved to
  `~/.cdsapirc`.
- **Copernicus CEMS EWDS** (GloFAS): separate account at
  https://ewds.climate.copernicus.eu/, token via the `EWDS_KEY`
  environment variable.
- **Earth Data Hub** (streaming ERA5, CMIP6): free DestinE account at
  https://platform.destine.eu/, token in `~/.netrc` for
  `data.earthdatahub.destine.eu`.
- **Direct download** (HadCET, HadCRUT5, GHCNd, CHIRPS): no credentials
  needed.
- **CEDA** (UKCP18): free account at https://services.ceda.ac.uk/cedasite/register/info/;
  OAuth token for programmatic access. UKCP18 is deferred in this repo
  pending registration.
- **NASA Earthdata** (GPWv4): free account at https://urs.earthdata.nasa.gov/;
  credentials via `~/.netrc`. GPWv4 is deferred in this repo pending
  registration.

Each dataset's docs page walks through the steps for its pattern.

## Quickstart (5 minutes)

Pick a dataset and follow its README. For ERA5, the fastest path is:

1. Register at https://cds.climate.copernicus.eu/ and accept the ERA5
   licence in your profile.
2. Save your Personal Access Token to `~/.cdsapirc` per
   https://cds.climate.copernicus.eu/how-to-api.
3. `pip install -r requirements.txt`
4. Open `notebooks/era5_single_levels_quickstart.ipynb` and run every
   cell. Default config pulls one hour of 2 m temperature over the UK
   (~30 kB, under a minute).

## Project structure

```
climate-data-quickstart/
├── CLAUDE.md              # Project rules and style guide
├── PLAN.md                # Working plan, dataset queue, status
├── README.md              # This file
├── requirements.txt       # Core Python dependencies
├── common/                # Shared helpers (credentials, plotting)
├── docs/                  # Per-dataset README and variables.md
├── notebooks/             # Per-dataset quickstart .ipynb
├── scripts/               # Per-dataset download script
└── .claude/               # Agent definitions and skill (for Claude Code users)
```

## Scope note

This is a getting-started resource. Each dataset page points to the
authoritative primary documentation (ECMWF Confluence, Met Office Hadley
Centre, NOAA NCEI, and so on). If you are doing research-grade analysis
you should follow those links for the technical detail this repo keeps
short.

## Contributions

Issues and pull requests welcome. The style rules (British English, no
em dashes, no marketing speak, primary sources only) are in
[`CLAUDE.md`](CLAUDE.md).

## Licence of this repository

The code, scripts, and docs in this repository are released under the
MIT licence. The datasets themselves have their own licences; each
dataset's README notes the licence and attribution requirements.

See [LICENSE](LICENSE) for the full text.
