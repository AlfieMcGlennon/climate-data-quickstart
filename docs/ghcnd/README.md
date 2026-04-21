# GHCNd

Global Historical Climatology Network - daily: ~100,000 weather
stations, daily observations, from the 18th century to present.

Operated by NOAA NCEI.

> **Scope of this page.** A getting-started reference. For the full data
> specification see https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
> and Menne et al. 2012.

## When to use this

When you need actual observed values at a specific location rather than
gridded estimates. Station data is the ground truth that reanalyses and
satellite products are validated against. Useful for site-specific
studies, model validation, or when you need long records from a
particular airport, city, or research station.

## At a glance

| Property | Value |
|---|---|
| Type | Station-based (not gridded) |
| Stations | ~100,000 worldwide; ~40,000 currently reporting |
| Core variables | TMAX, TMIN, PRCP, SNOW, SNWD |
| Temporal resolution | Daily |
| Temporal coverage | 1763 onwards (1950+ for substantive global coverage) |
| Format | Fixed-width ASCII (`.dly`) or gzipped CSV by year |
| Access | Direct HTTPS, no authentication |
| Licence | US public domain |

## What this is

The world's largest integrated database of daily in-situ weather
observations. Core elements are daily max/min temperature, precipitation,
snowfall, and snow depth. Many stations also report wind, sunshine,
humidity, and weather-type flags.

Use it when you need actual station observations (not reanalysis) for:
trend analysis at specific locations, validating gridded products,
historical extremes, long-term climate records. For gridded analysis,
use E-OBS (Europe) or HadUK-Grid (UK).

## Station IDs

Each 11-character ID encodes country, network, and station code:

```
UK M  00003772
|  |  |
|  |  +-- station within network (airport WMO code 03772 = Heathrow)
|  +----- network (M = WMO, E = ECA&D, 1 = US Coop, etc.)
+-------- country (UK, US, GM, AS, ...)
```

Example UK airport stations (verify against `ghcnd-stations.txt` at
fetch time):

| Name | Station ID |
|---|---|
| London Heathrow | `UKM00003772` |
| London Gatwick | `UKM00003776` |
| Manchester Airport | `UKM00003334` |
| Edinburgh Gogarbank | `UKM00003166` |
| Belfast Aldergrove | `UKM00003917` |
| Lerwick (Shetland) | `UKM00003005` |

## Core variables

| Element | Description | Raw units (in file) |
|---|---|---|
| `TMAX` | Maximum temperature | tenths of deg C (divide by 10) |
| `TMIN` | Minimum temperature | tenths of deg C (divide by 10) |
| `TAVG` | Average temperature (when reported) | tenths of deg C |
| `PRCP` | Precipitation, 24-hour total | tenths of mm (divide by 10) |
| `SNOW` | Snowfall | mm |
| `SNWD` | Snow depth | mm |

**Units trap:** temperature and precipitation are stored in **tenths**.
Divide by 10 to get natural units. Missing values are `-9999`.

## Get data in 5 minutes

No registration. Just:

```bash
pip install pandas requests matplotlib
python scripts/ghcnd_download.py
```

The default downloads Heathrow's `.dly` file, parses it, and saves a
tidy long-format CSV with TMAX, TMIN, and PRCP scaled to natural units.

## Files available

All served over plain HTTPS from `https://www.ncei.noaa.gov/pub/data/ghcn/daily/`:

- **Per-station** `.dly` files (recommended for a quickstart):
  `.../all/{STATION_ID}.dly`
- **Annual CSV** files (all stations, one year at a time):
  `.../by_year/{YYYY}.csv.gz`
- **Full archive tarball** (several GB):
  `.../ghcnd_all.tar.gz`
- **Station metadata**: `.../ghcnd-stations.txt`
- **Element inventory**: `.../ghcnd-inventory.txt` (which variables each
  station reports and the date range)

## Things to know

- **Filter on QFLAG.** Every observation has a quality flag. A blank
  flag means the value passed all quality-control checks. Any non-blank
  value indicates a failed check. Drop non-blank QFLAG before analysis.
- **Not homogenised.** GHCNd is raw (quality-controlled) observations.
  Apparent trends at a single station can be artefacts of siting,
  instrument, or observation-time changes. For homogenised monthly
  temperatures use GHCN-M v4.
- **Station-specific element coverage.** Not every station reports all
  elements. Check `ghcnd-inventory.txt` before assuming.
- **Duplicate stations across networks.** The same physical site may
  appear under multiple IDs (WMO `UKM...` and ECA&D `UKE...`). Pick one
  for a given analysis.
- **Daily windows differ.** The "daily" window is defined by the source
  network and may be morning-to-morning, evening-to-evening, or calendar
  day. Matters when comparing against reanalyses.
- **Trace precipitation** is recorded as `VALUE=0` with `MFLAG=T`.
  Treating as true zero is usually fine.

## Licence and attribution

US Federal Government work; **public domain** in the United States. No
restrictions on redistribution, modification, or commercial use. NCEI
requests (not legally requires) citation of the dataset and Menne et al.
2012.

Some contributing networks (e.g. ECA&D) apply their own terms to the
underlying data; for most climate-monitoring use this is not a practical
constraint.

## Citation

Reference paper:

> Menne, M. J., Durre, I., Vose, R. S., Gleason, B. E., and Houston, T. G.
> (2012): An Overview of the Global Historical Climatology Network-Daily
> Database. Journal of Atmospheric and Oceanic Technology, 29, 897-910.
> DOI: 10.1175/JTECH-D-11-00103.1

Dataset:

> Menne, M. J., et al. Global Historical Climatology Network - Daily
> (GHCN-Daily), Version 3. NOAA National Climatic Data Center.
> DOI: 10.7289/V5D21VHZ

## Further reading

- Product landing: https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily
- File format readme: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
- Data root: https://www.ncei.noaa.gov/pub/data/ghcn/daily/
- Homogenised monthly (GHCN-M): https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-monthly
