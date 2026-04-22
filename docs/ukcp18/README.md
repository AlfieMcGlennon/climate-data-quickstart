# UKCP18

UK Climate Projections 2018: the UK's national set of climate change
projections through the 21st century, from the Met Office Hadley Centre.

Hosted on the CEDA Archive.

> **Scope of this page.** A getting-started reference for the UKCP18
> regional (12 km) projections. For full documentation see the
> [UKCP18 guidance hub](https://www.metoffice.gov.uk/research/approach/collaboration/ukcp/using-ukcp/guidance)
> and the [CEDA archive](https://data.ceda.ac.uk/badc/ukcp18/).

## When to use this

When you need future climate projections specifically for the UK at high
spatial resolution. UKCP18 is the standard dataset for UK climate impact
assessments, adaptation planning, and policy work. The regional 12 km
strand gives daily fields over a European domain; the local 2.2 km
strand resolves convective processes over the British Isles. For global
projections or multi-scenario analysis, note that only the probabilistic
strand covers multiple RCPs; the higher-resolution strands are RCP8.5
only.

## At a glance

| Property | Value |
|---|---|
| Resolution | 25 km (probabilistic), 60 km (global), 12 km (regional), 2.2 km (local) |
| Coverage | UK and European domain (regional); British Isles (local); global (60 km) |
| Temporal coverage | 1900-2100 (varies by strand) |
| Format | NetCDF |
| Access | CEDA account with bearer token |
| Scenarios | RCP8.5 (regional/local/global); RCP2.6/4.5/6.0/8.5 (probabilistic) |
| Licence | Open Government Licence v3.0 |

## What this is

UKCP18 comprises multiple projection strands:

- **Probabilistic (25 km)** - 3,000 realisations, multiple RCPs,
  anomalies on the OSGB grid. Period: 1961-2100.
- **Global (60 km)** - 28 simulations (15 PPE + 13 CMIP5), RCP8.5
  only. Period: 1900-2100.
- **Regional (12 km)** - 12 PPE members downscaled with HadREM3-GA705,
  RCP8.5 only. Period: 1980-2080. This is the recommended starting
  point for the quickstart.
- **Local (2.2 km)** - 12 PPE members, convection-permitting, three
  20-year time slices. RCP8.5 only.
- **Marine** - sea level rise, storm surge, shelf-sea physics.

The quickstart focuses on the regional 12 km strand (monthly mean
temperature, ensemble member 01) as a practical entry point.

## Get data in 5 minutes

Requires a free [CEDA account](https://services.ceda.ac.uk/cedasite/register/info/).

Set up your token (either method):

```bash
# Option 1: environment variable
export CEDA_TOKEN="your_bearer_token_here"

# Option 2: save to file
echo "your_bearer_token_here" > ~/.ceda_token
```

Generate a token at the [CEDA token API](https://services.ceda.ac.uk/api/token/create/)
or the [web token page](https://services.ceda.ac.uk/cedasite/mytokens/).

Then:

```bash
pip install requests xarray netcdf4 matplotlib cartopy numpy
python scripts/ukcp18_download.py
```

The default pulls monthly mean temperature from the regional 12 km
product for ensemble member 01.

## CEDA archive structure

The data root is `https://data.ceda.ac.uk/badc/ukcp18/data/` with
top-level directories:

| Directory | Content |
|---|---|
| `land-prob/` | Probabilistic projections (25 km OSGB) |
| `land-gcm/` | Global 60 km projections |
| `land-rcm/` | Regional 12 km projections |
| `land-cpm/` | Local 2.2 km convection-permitting |

Within each: `{domain}/{resolution}/{scenario}/{ensemble_member}/{variable}/{frequency}/{version}/`

File naming: `{var}_{scenario}_{collection}_{domain}_{resolution}_{member}_{frequency}_{period}.nc`

Example: `tas_rcp85_land-rcm_uk_12km_01_mon_19801201-20801130.nc`

## Key variables (regional 12 km)

| Variable | Description | Units |
|---|---|---|
| `tas` | Mean air temperature at 1.5 m | degC |
| `tasmin` | Minimum air temperature at 1.5 m | degC |
| `tasmax` | Maximum air temperature at 1.5 m | degC |
| `pr` | Precipitation rate | mm/day |
| `psl` | Mean sea level pressure | hPa |
| `hurs` | Relative humidity at 1.5 m | % |
| `sfcWind` | Wind speed at 10 m | m/s |
| `clt` | Total cloud cover | % |

Full variable vocabulary:
https://github.com/ukcp-data/UKCP18_CVs/blob/master/UKCP18_CVs/UKCP18_variable.json

## Things to know

- **RCP8.5 only at high resolution.** The regional (12 km) and local
  (2.2 km) strands only run RCP8.5. Only the probabilistic strand
  covers multiple scenarios.
- **Raw model output.** Not bias-corrected. Contains systematic biases
  relative to observations. Consider bias correction for impact
  assessments. See
  [Sheridan et al. 2025](https://essd.copernicus.org/articles/17/2113/2025/)
  for a bias-corrected version.
- **Rotated-pole grid.** The native RCM/CPM grids use a rotated-pole
  coordinate system. The UK-regridded versions on OSGB are easier to
  work with. The quickstart uses the OSGB-regridded version.
- **CPM is time slices only.** The 2.2 km data covers three 20-year
  windows (1981-2000, 2021-2040, 2061-2080), not a continuous series.
- **Large archive.** The full UKCP18 archive is approximately 117 TB.
  Target specific variables, members, and periods.
- **Token expiry.** CEDA bearer tokens are valid for 3 days.
  Regenerate before bulk downloads.

## Licence and attribution

Open Government Licence v3.0. Attribution required: "Contains Met Office
data, Crown Copyright. Used under the Open Government Licence v3.0."

## Citation

> Lowe JA, Bernie D, Bett PE, et al. (2018). UKCP18 Science Overview
> Report. Met Office Hadley Centre, Exeter.
> https://www.metoffice.gov.uk/pub/data/weather/uk/ukcp18/science-reports/UKCP18-Overview-report.pdf

## Further reading

- Met Office UKCP landing: https://www.metoffice.gov.uk/research/approach/collaboration/ukcp
- UKCP18 user interface: https://ukclimateprojections-ui.metoffice.gov.uk/
- CEDA archive: https://data.ceda.ac.uk/badc/ukcp18/
- CEDA catalogue record: https://catalogue.ceda.ac.uk/uuid/c700e47ca45d4c43b213fe879863d589/
- Guidance and caveats: https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/research/ukcp/ukcp18-guidance---caveats-and-limitations.pdf
