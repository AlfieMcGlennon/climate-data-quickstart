# ECMWF Open Data (IFS forecasts)

Free operational IFS forecast data from ECMWF, published under CC-BY-4.0.
Global, 0.25 degree resolution, out to 10 days (240 h) for 00z/12z runs
and 3.75 days (90 h) for 06z/18z runs.

> **Scope of this page.** A getting-started reference for downloading your
> first IFS forecast fields. For the full parameter catalogue and data
> model, see the ECMWF Open Data documentation linked at the bottom.

## When to use this

When you need real-time weather forecast fields rather than historical
data. This gives you the same IFS model output that professional
meteorologists use, published within hours of each model run. No
registration, no queue, no cost. Good for operational dashboards,
forecast verification studies, or simply answering "what is the weather
going to be this week."

## What this is

ECMWF publishes a subset of its operational Integrated Forecasting System
(IFS) output as open data. These are real-time deterministic and ensemble
forecasts, not reanalysis. The archive is rolling: only the most recent
two to three days of runs are available at any time. There is no
historical archive.

Use it when you need current global weather forecasts at 0.25 degree
resolution without authentication or payment. Typical uses: forecast
verification, event monitoring, teaching, and prototyping downstream
forecast products.

## Coverage

| Property | Value |
|---|---|
| Grid | Regular latitude-longitude, 0.25 degrees (~31 km) |
| Spatial coverage | Global |
| Runs per day | 4 (00z, 06z, 12z, 18z) |
| Forecast steps (00z/12z) | 0-144 h every 3 h, then 150-240 h every 6 h |
| Forecast steps (06z/18z) | 0-90 h every 3 h |
| Archive depth | Rolling, most recent ~12 runs (2-3 days) |
| Format | GRIB2 only |
| Models available | IFS HRES, AIFS (single), AIFS (ensemble) |

## Variables

The open data subset exposes the most commonly used surface and
pressure-level fields. The ten most used surface variables are below. The
full list is on the ECMWF Open Data documentation page.

| Short name | Long name | Units |
|---|---|---|
| `2t` | 2 metre temperature | K |
| `10u` | 10 metre U wind component | m s-1 |
| `10v` | 10 metre V wind component | m s-1 |
| `msl` | Mean sea level pressure | Pa |
| `tp` | Total precipitation | m |
| `sp` | Surface pressure | Pa |
| `tcc` | Total cloud cover | 0-1 |
| `2d` | 2 metre dewpoint temperature | K |
| `tcwv` | Total column water vapour | kg m-2 |
| `cape` | Convective available potential energy | J kg-1 |

Variables use GRIB short names throughout. These are the names you pass
to the `param` argument and the names that appear inside the GRIB file
when opened with cfgrib.

## Access

### 1. Install

```bash
pip install ecmwf-opendata cfgrib eccodes xarray matplotlib cartopy
```

No registration or API key is needed.

### 2. Retrieve a forecast field

```python
from ecmwf.opendata import Client

client = Client()
client.retrieve(
    step=24,
    type="fc",
    param=["2t", "msl"],
    target="forecast.grib2",
)
```

This fetches the latest available 00z/12z deterministic forecast at
T+24 h for 2 metre temperature and mean sea level pressure.

### 3. Open in xarray

GRIB files need the cfgrib engine:

```python
import xarray as xr

ds = xr.open_dataset("forecast.grib2", engine="cfgrib")
```

If the file contains multiple GRIB messages with different step types or
levels, cfgrib may need filtering. See the notebook for a working example.

### Key parameters

| Parameter | Values | Notes |
|---|---|---|
| `date` | `YYYYMMDD` or `0` | `0` means latest available run |
| `time` | `0`, `6`, `12`, `18` | Forecast initialisation hour |
| `step` | Integer hours | Lead time; range depends on run time |
| `type` | `fc`, `cf`, `pf` | HRES forecast, control forecast, perturbed members |
| `stream` | `oper`, `scda`, `enfo` | `oper` for 00z/12z, `scda` for 06z/18z, `enfo` for ensemble |
| `param` | GRIB short name(s) | e.g. `["2t", "msl"]` |
| `model` | `ifs`, `aifs-single`, `aifs-ens` | IFS HRES or AIFS variants |

### 4. Run the download script

```bash
python scripts/ecmwf_open_data_download.py
```

The default config fetches the latest 00z/12z deterministic forecast of
2 metre temperature at T+24 h. Edit the config block at the top of the
script to change variables, steps, or forecast type.

## Gotchas

- **GRIB only.** There is no NetCDF option. You need `cfgrib` and
  `eccodes` installed to open files in xarray.
- **Rolling archive, no history.** Only the most recent 2-3 days of runs
  are available. If you need yesterday's forecast, grab it today.
- **Accumulated precipitation.** `tp` is accumulated from step 0. To get
  precipitation for a specific period, difference the steps (e.g.
  `tp[step=27] - tp[step=24]` for the 24-27 h window).
- **Connection limit.** ECMWF may throttle aggressive parallel
  downloading. [VERIFY] The exact limit is not publicly documented.
- **No authentication, but rate-limited.** No API key is needed, but
  aggressive parallel downloading may be throttled.

## Licence and attribution

Licence: Creative Commons Attribution 4.0 International (CC-BY-4.0).

Attribution: "Contains modified Copernicus data [year], published by
ECMWF under CC-BY-4.0." Commercial use is permitted.

Full terms: https://www.ecmwf.int/en/terms-use

## Further reading

- ECMWF Open Data documentation: https://www.ecmwf.int/en/forecasts/datasets/open-data
- `ecmwf-opendata` Python package: https://github.com/ecmwf/ecmwf-opendata
- ECMWF parameter database (short name lookup): https://codes.ecmwf.int/grib/param-db/
- ECMWF forecast charts (visual verification): https://charts.ecmwf.int/
- Open data real-time data access: https://data.ecmwf.int/forecasts/
