# C3S seasonal forecasts

Multi-model ensemble seasonal forecasts from the Copernicus Climate Change
Service (C3S). Nine contributing centres produce probabilistic predictions
1 to 6 months ahead on a global 1 x 1 degree grid.

> **Scope of this page.** A getting-started reference for downloading and
> interpreting C3S seasonal forecast data. It does not replace the ECMWF
> primary documentation. For full system specifications, licence details for
> individual centres, and known data issues, follow the links throughout.

## When to use this

When you want to look further ahead than a weather forecast. Seasonal
forecasts predict shifts in temperature and precipitation patterns over
the coming 1 to 6 months, not specific days. Useful for agriculture,
energy demand planning, drought early warning, and any application where
knowing "will next season be wetter or drier than normal" is valuable.

## What this dataset is

Seasonal forecasts predict the state of the atmosphere, ocean, and land
surface one to six months into the future. Unlike weather forecasts, they
do not predict specific days. Instead, they predict shifts in the
statistical distribution of weather over a full calendar month (for
example, "January 2024 is likely to be warmer than average over north-west
Europe").

The C3S multi-system seasonal forecast service combines output from nine
operational centres. Each centre runs its own coupled atmosphere-ocean
model, initialised from recent observations, and produces an ensemble of
forecasts (multiple runs with slightly different starting conditions). The
spread across ensemble members quantifies forecast uncertainty.

Two products are available on the CDS:

- **Monthly statistics** (`seasonal-monthly-single-levels`): monthly means
  per ensemble member, on a 1 x 1 degree grid. This is the recommended
  starting point and the product used in this repo's quickstart.
- **Original fields** (`seasonal-original-single-levels`): 6-hourly fields
  at each centre's native resolution. Much larger, for specialist use.

Hindcasts (re-forecasts over the 1993-2016 period, initialised from
reanalysis) are available alongside real-time forecasts. They are essential
for bias correction and skill assessment.

## Coverage

| Property | Value |
|---|---|
| Grid | Regular latitude-longitude, 1 x 1 degree (monthly product) |
| Spatial coverage | Global |
| Temporal coverage | Real-time forecasts from 2017 onward; hindcasts 1993-2016 |
| Lead times | 1 to 6 months (leadtime_month 1-6) |
| Initialisation | Monthly (one forecast per calendar month per centre) |
| Update frequency | Monthly, typically available within 2 weeks of the initialisation date |

## Variables

The ten most commonly used variables for the monthly product are listed
below. The full variable catalogue is on the
[CDS dataset page](https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels).

| CDS API name | Long name | Units |
|---|---|---|
| `2m_temperature` | 2 metre temperature | K |
| `total_precipitation` | Total precipitation | m |
| `mean_sea_level_pressure` | Mean sea level pressure | Pa |
| `sea_surface_temperature` | Sea surface temperature | K |
| `10m_u_component_of_wind` | 10 metre U wind component | m s-1 |
| `10m_v_component_of_wind` | 10 metre V wind component | m s-1 |
| `maximum_2m_temperature_in_the_last_24_hours` | Maximum 2 m temperature in 24 h | K |
| `minimum_2m_temperature_in_the_last_24_hours` | Minimum 2 m temperature in 24 h | K |
| `total_cloud_cover` | Total cloud cover | 0-1 |
| `sea_ice_cover` | Sea ice cover | 0-1 |

## Contributing centres

Each centre has its own model system, ensemble size, and system version
number. The system number is required in API requests.

| Centre | `originating_centre` | `system` | Ensemble size (real-time) |
|---|---|---|---|
| ECMWF | `ecmwf` | `51` | 51 |
| UK Met Office | `ukmo` | `610` | 42 |
| Meteo-France | `meteo_france` | `8` | 51 |
| DWD | `dwd` | `22` | 50 |
| CMCC | `cmcc` | `35` | 50 |
| NCEP | `ncep` | `2` | 28 |
| JMA | `jma` | `3` | 51 |
| ECCC | `eccc` | `3` | 20 |
| LUMI (CSC) | `csc` | `1` | [VERIFY] (new addition, not yet confirmed) |

System numbers change when centres upgrade their models. The values above
are current as of early 2025. Check the
[CDS dataset documentation](https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels)
for the latest.

## Access

C3S seasonal forecasts use the same CDS API credentials as ERA5 (Pattern A
in this repo). If you already have `~/.cdsapirc` configured for ERA5, no
additional setup is needed.

### 1. Register and configure credentials

Follow the same steps as for ERA5: register at
https://cds.climate.copernicus.eu/, save your Personal Access Token to
`~/.cdsapirc`. See [`docs/era5-single-levels/README.md`](../era5-single-levels/README.md)
for the full walkthrough.

### 2. Accept both licences

This dataset requires you to accept **two** licences on the CDS website:

1. **Licence to use Copernicus Products** (the standard C3S licence)
2. **Additional licence for non-European seasonal forecast centres**

Both must be accepted before API requests will succeed. Go to the dataset
page, click "Terms of use", and accept each one.

### 3. Install dependencies

```bash
pip install cdsapi xarray cfgrib eccodes matplotlib cartopy numpy
```

GRIB format is strongly recommended for this dataset. `cfgrib` and
`eccodes` are needed to open GRIB files in xarray.

### 4. Run the download script

```bash
python scripts/c3s_seasonal_download.py
```

The default config pulls ECMWF system 51, 2 metre temperature, monthly
mean, January 2024 initialisation, all six lead times, over a European
region. Output is GRIB format.

### Example API call

```python
import cdsapi
c = cdsapi.Client()
c.retrieve(
    'seasonal-monthly-single-levels',
    {
        'format': 'grib',
        'originating_centre': 'ecmwf',
        'system': '51',
        'variable': '2m_temperature',
        'product_type': 'monthly_mean',
        'year': '2024',
        'month': '01',
        'leadtime_month': ['1', '2', '3', '4', '5', '6'],
        'area': [72, -12, 35, 30],
    },
    'c3s_seasonal_test.grib')
```

## Gotchas

- **Two licences required.** Both must be accepted on the CDS website or
  API requests return a licence error. See
  [dataset terms](https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels).
- **Use GRIB, not NetCDF.** NetCDF output is experimental for this dataset
  and can produce corrupted or incomplete files. GRIB is the reliable path.
- **System numbers are centre-specific.** Passing the wrong system number
  for a centre returns an empty or errored result. Check the dataset
  documentation when switching centres.
- **JMA uses a 1.25 degree grid.** All other centres use 1 degree. If you
  are comparing across centres, regrid first.
- **Requests can be slow.** Data is served from tape archive. Follow the
  [ECMWF efficiency guidance](https://confluence.ecmwf.int/display/CKB/Climate+Data+Store+%28CDS%29+documentation)
  and keep requests small.

## Licence and citation

Licence: Licence to use Copernicus Products, plus the additional licence
for non-European contributions. Both listed on the
[dataset terms page](https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels).

Dataset citation:

> Copernicus Climate Change Service (C3S) (2018): C3S seasonal forecast
> monthly statistics on single levels. Copernicus Climate Change Service
> (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.68dd14c3

## Further reading

- CDS dataset page (monthly): https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels
- CDS dataset page (original fields): https://cds.climate.copernicus.eu/datasets/seasonal-original-single-levels
- C3S seasonal forecasts documentation: https://confluence.ecmwf.int/display/CKB/Seasonal+forecasts+and+the+Copernicus+Climate+Change+Service
- How to set up the CDS API: https://cds.climate.copernicus.eu/how-to-api
- Seasonal forecast user guide: https://confluence.ecmwf.int/display/CKB/Description+of+the+C3S+seasonal+multi-system
