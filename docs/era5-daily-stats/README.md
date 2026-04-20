# ERA5 daily statistics

Pre-computed daily aggregates of ERA5 single-levels variables, from 1940
to present, on a 0.25 degree global grid.

Produced by the Copernicus Climate Change Service (C3S) at ECMWF as a
server-side derived product over the underlying ERA5 hourly archive.

> **Scope of this page.** A getting-started reference for MSc/PhD students
> and early-career researchers. For the authoritative technical detail,
> see the ECMWF documentation linked throughout.

## At a glance

| Property | Value |
|---|---|
| Dataset ID | `derived-era5-single-levels-daily-statistics` |
| Statistics | daily_mean, daily_maximum, daily_minimum, daily_sum |
| Variables | Same 100+ as [ERA5 single levels](../era5-single-levels/README.md) |
| Horizontal resolution | 0.25 degrees (atmosphere), 0.5 degrees (waves) |
| Temporal resolution | Daily (24-hour aggregates, time-zone configurable) |
| Temporal coverage | 1940-01-01 to present |
| Latency | Inherits ERA5 (~5 days ERA5T, ~2-3 months final) |
| Licence | Licence to use Copernicus Products (commercial use allowed) |
| DOI | 10.24381/cds.4991cf48 |

## What this is

A thin server-side wrapper over ERA5 hourly data. Instead of downloading
24 hours of hourly data and calling `.resample(valid_time="1D").mean()`
yourself, the CDS does the aggregation during retrieval and returns
daily values. Roughly 24x smaller downloads.

Use it when you only need daily mean/min/max/sum and do not need hourly
detail. For custom aggregation windows (6-hour running means, growing-
season sums, non-integer-UTC bins), use the parent
[ERA5 single levels](../era5-single-levels/README.md) entry and resample
locally.

## Variables and statistics

Available statistics depend on variable type:

| Variable type | `daily_mean` | `daily_maximum` | `daily_minimum` | `daily_sum` |
|---|---|---|---|---|
| Instantaneous (e.g. `2m_temperature`) | yes | yes | yes | **no** |
| Accumulated / mean-rate (e.g. `total_precipitation`) | yes | yes | yes | yes |

The variable catalogue is the same as ERA5 single levels. See
[../era5-single-levels/variables.md](../era5-single-levels/variables.md)
for the full list.

## Get data in 5 minutes

1. Register for a free CDS account at https://cds.climate.copernicus.eu/
2. Accept the licence for this dataset in your CDS profile (separate from
   the main ERA5 licence).
3. Create `~/.cdsapirc` with your Personal Access Token. See the
   [ERA5 single levels docs](../era5-single-levels/README.md#get-data-in-5-minutes)
   for format and Windows-specific steps.
4. `pip install cdsapi xarray netcdf4`
5. Run `python scripts/era5_daily_stats_download.py`

The default pulls three days of daily-mean 2 metre temperature over the
UK.

## Things to know

- **Request-dict keys are different.** Compared to the main ERA5 entry,
  this dataset requires `daily_statistic`, `frequency`
  (`1_hourly`/`3_hourly`/`6_hourly` - controls the sub-daily sampling
  used in the aggregation), and `time_zone` (e.g. `utc+00:00`). No
  `time` key (the service handles hours internally). No `download_format`
  key: output is always NetCDF wrapped in a zip archive.
- **Accumulation timestamp is handled for you.** ERA5 hourly accumulations
  use an end-of-period convention (the 00:00 UTC value covers the
  preceding hour). The daily-stats service corrects for this internally
  so `daily_sum` over a UTC day matches what you would expect from
  "23:00 previous day to 23:00 current day". Saves users from a classic
  off-by-one bug.
- **`daily_sum` only makes sense for accumulated variables.** The CDS
  will reject or silently produce garbage for a `daily_sum` on
  `2m_temperature`.
- **Output is zipped.** The script unpacks it for you; if you are writing
  your own code, expect a `.zip` containing a single `.nc`.
- **Inherits all ERA5 known issues.** Biases, stream-boundary
  discontinuities, ERA5T vs ERA5 handling, ERA5.1 for 2000-2006 all
  apply. See the [ERA5 single levels](../era5-single-levels/README.md#known-issues)
  entry.
- **At the earliest dates (1940-early 1941)** only UTC or westward time
  zones (`utc-HH:00`) guarantee a complete 24-hour sampling window.

## Licence and attribution

Licence: Licence to use Copernicus Products. Commercial use is permitted
with attribution.

Full licence:
https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf

Attribution: state "Generated using Copernicus Climate Change Service
information [Year]" and cite both DOIs below plus the Hersbach et al.
2020 reference paper.

## Citation

Derived product:

> Copernicus Climate Change Service (C3S) (2024). ERA5 post-processed
> daily statistics on single levels from 1940 to present. Copernicus
> Climate Change Service (C3S) Climate Data Store (CDS).
> DOI: 10.24381/cds.4991cf48

Underlying hourly dataset:

> Hersbach, H., et al. (2023). ERA5 hourly data on single levels from
> 1940 to present. C3S CDS. DOI: 10.24381/cds.adbb2d47

Reference paper:

> Hersbach, H., et al. (2020). The ERA5 global reanalysis. Quarterly
> Journal of the Royal Meteorological Society, 146(730), 1999-2049.
> DOI: 10.1002/qj.3803

## Further reading

- CDS dataset page: https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics
- ECMWF daily-stats documentation: https://confluence.ecmwf.int/display/CKB/ERA5+family+post-processed+daily+statistics+documentation
- ERA5 single levels in this repo: [../era5-single-levels/README.md](../era5-single-levels/README.md)
