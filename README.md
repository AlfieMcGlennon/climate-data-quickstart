# Climate data quickstart

A local desktop app and script library for downloading, streaming, and
exploring climate and weather datasets. Pick a dataset from a form, fill
in a few fields, click Download. No code required for the app; scripts
and notebooks are there if you want to see how it works or build your
own pipeline.

Built for MSc/PhD students, early-career climate scientists, and anyone
who has spent too long reading provider docs before pulling their first
file.

## Quick start

You need Python 3.10+ installed. That is the only prerequisite.

**Windows:**

```
git clone https://github.com/your-username/climate-data-quickstart.git
cd climate-data-quickstart
setup.bat
```

**macOS / Linux:**

```bash
git clone https://github.com/your-username/climate-data-quickstart.git
cd climate-data-quickstart
chmod +x setup.sh && ./setup.sh
```

**Conda users:**

```bash
conda env create -f environment.yml
conda activate climate-data-quickstart
streamlit run app/main.py
```

Setup creates a `.venv/`, installs everything, and takes 2-3 minutes.
Then launch the app:

- Windows: double-click `run_app.bat`
- macOS/Linux: `./run_app.sh`

Your browser opens at `http://localhost:8501`. Pick a dataset, configure
a small request, click Download.

## Datasets

19 datasets across five categories:

| # | Dataset | Coverage | Access | Docs |
|---|---------|----------|--------|------|
| 1 | ERA5 single levels | Global, hourly, 0.25 deg, 1940-present | CDS API | [docs](docs/era5-single-levels/README.md) |
| 2 | ERA5 pressure levels | Global, hourly, 37 pressure levels | CDS API | [docs](docs/era5-pressure-levels/README.md) |
| 3 | ERA5-Land | Land-only, hourly, 0.1 deg, 1950-present | CDS API | [docs](docs/era5-land/README.md) |
| 4 | ERA5 daily statistics | Pre-computed daily mean/max/min | CDS API | [docs](docs/era5-daily-stats/README.md) |
| 5 | Earth Data Hub | Stream ERA5/CMIP6 via Zarr, no queue | Zarr | [docs](docs/earth-data-hub/README.md) |
| 6 | ARCO-ERA5 | ERA5 on Google Cloud, no API key needed | Zarr | [docs](docs/arco-era5/README.md) |
| 7 | EDH catalogue explorer | Browse ERA5 + CMIP6 models from EDH | Zarr | - |
| 8 | CMIP6 (CDS) | Curated subset of climate projections | CDS API | [docs](docs/cmip6/README.md) |
| 9 | ESGF CMIP6 | Full archive, every model and experiment | Direct HTTP | [docs](docs/esgf-cmip6/README.md) |
| 10 | C3S seasonal | Multi-system forecasts, up to 6 months ahead | CDS API | [docs](docs/c3s-seasonal/README.md) |
| 11 | HadCET | Central England temperature, 1659-present | Direct HTTP | [docs](docs/hadcet/README.md) |
| 12 | HadCRUT5 | Global temperature anomalies, 1850-present | Direct HTTP | [docs](docs/hadcrut5/README.md) |
| 13 | GHCNd | 100,000+ weather stations, daily records | Direct HTTP | [docs](docs/ghcnd/README.md) |
| 14 | E-OBS | European gridded daily observations | CDS API | [docs](docs/e-obs/README.md) |
| 15 | CHIRPS | Satellite-station rainfall blend, tropics | Direct HTTP | [docs](docs/chirps/README.md) |
| 16 | ECMWF Open Data | Real-time IFS/AIFS, four times daily | Direct HTTP | [docs](docs/ecmwf-open-data/README.md) |
| 17 | GloFAS | Global river discharge reanalysis | EWDS API | [docs](docs/glofas/README.md) |
| 18 | GPWv4 population | Global gridded population density, census-based | NASA Earthdata | [docs](docs/gpw-population/README.md) |
| 19 | UKCP18 | UK climate projections, 12 km regional, to 2080 | CEDA | [docs](docs/ukcp18/README.md) |

## What the app does

- **Download** any of the 19 datasets with a form instead of writing API calls
- **Stream** ERA5 and CMIP6 data lazily via Zarr (no queue, no file download)
- **Explore** any NetCDF, GRIB, or CSV file with interactive maps and time series
- **Compare** CMIP6 models side by side or plot ensemble member spread from ESGF
- **Search** datasets by topic (temperature, wind, precipitation, flood, Europe, forecast)
- **Learn** with interactive recipes: England's 350-year temperature record, global warming trends, colourmap and projection comparisons

Everything runs locally. The app never reads or stores your API keys -
it uses the same credential files as the command-line scripts
(`~/.cdsapirc`, `~/.netrc`).

## Credentials

Some datasets are open (HadCET, CHIRPS, ARCO-ERA5, ESGF, ECMWF Open Data).
The rest need a free API key. The app shows which credentials you have and
which are missing in the sidebar.

| Provider | Datasets | Where to register | Key file |
|----------|----------|-------------------|----------|
| Copernicus CDS | ERA5 (all), CMIP6, E-OBS, C3S seasonal | [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/) | `~/.cdsapirc` |
| Copernicus EWDS | GloFAS | [ewds.climate.copernicus.eu](https://ewds.climate.copernicus.eu/) | `EWDS_KEY` env var |
| Earth Data Hub | EDH, EDH explorer | [platform.destine.eu](https://platform.destine.eu/) | `~/.netrc` |
| NASA Earthdata | GPWv4 population | [urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov/) | `~/.netrc` |
| CEDA | UKCP18 | [services.ceda.ac.uk](https://services.ceda.ac.uk/cedasite/register/info/) | `~/.ceda_token` or `CEDA_TOKEN` env var |
| None needed | HadCET, HadCRUT5, GHCNd, CHIRPS, ARCO-ERA5, ECMWF Open Data, ESGF CMIP6 | - | - |

Each dataset's docs page has step-by-step credential setup instructions.

## Scripts only (no app)

If you just want the download scripts and notebooks:

```bash
pip install -r requirements.txt
python scripts/era5_single_levels_download.py
```

Each script has a config block at the top you can edit. Each notebook
runs top-to-bottom after you set the config block and have the right
credentials.

## Project structure

```
climate-data-quickstart/
  setup.bat / setup.sh       # One-time setup (creates .venv, installs deps)
  run_app.bat / run_app.sh   # Launch the Streamlit app
  requirements.txt           # Python dependencies (pip)
  environment.yml            # Python dependencies (conda)
  app/                       # Streamlit app source
  scripts/                   # Per-dataset download scripts
  notebooks/                 # Per-dataset quickstart notebooks
  docs/                      # Per-dataset documentation
  common/                    # Shared helpers
```

## Troubleshooting

**Cartopy fails to install (macOS/Linux).** Cartopy needs the GEOS and
PROJ C libraries. If `pip install` fails with compilation errors, use
conda instead:

```bash
conda env create -f environment.yml
conda activate climate-data-quickstart
streamlit run app/main.py
```

**CDS request hangs.** Copernicus CDS requests are queued server-side
and can take minutes to hours during busy periods. The app shows a
status message while waiting. Check queue status at
https://cds.climate.copernicus.eu/live/queue.

**GRIB files won't open.** Make sure `cfgrib` and `eccodes` are
installed. On conda: `conda install -c conda-forge cfgrib eccodes`.
On pip: `pip install cfgrib eccodes`. The `eccodes` pip package needs
the ecCodes C library installed separately on some systems.

## Safety

The app binds only to `localhost`. The underlying libraries (`cdsapi`,
`requests` with `~/.netrc`, xarray with Zarr) read your credentials
directly from the standard files exactly as they would from a script.
Nothing is sent anywhere except the data provider's API.

## Licence

The code in this repository is released under the MIT licence. The
datasets themselves have their own licences; each dataset's README
notes the licence and attribution requirements. See [LICENSE](LICENSE).
