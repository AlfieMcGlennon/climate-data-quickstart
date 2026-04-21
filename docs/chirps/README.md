# CHIRPS

Climate Hazards Group InfraRed Precipitation with Stations: quasi-global
(50 S to 50 N) daily rainfall on a 0.05 degree grid, 1981 to present.

Produced by UCSB Climate Hazards Center and USGS EROS.

> **Scope of this page.** A getting-started reference. For full details
> see https://www.chc.ucsb.edu/data/chirps and Funk et al. 2015.

## When to use this

When you need rainfall data in the tropics or subtropics, especially
Africa, and want the best available blend of satellite and station
observations. CHIRPS was built for drought monitoring and food security
analysis. Note that it covers 50S to 50N only, so it does not include
the UK or most of Europe.

## At a glance

| Property | Value |
|---|---|
| Resolution | 0.05 degrees (~5 km) or 0.25 degrees |
| Coverage | **50 S to 50 N only** (not truly global; excludes the UK and most of Europe) |
| Temporal resolution | Daily, pentadal, dekadal, monthly, seasonal, annual |
| Temporal coverage | 1981-01-01 to near-present |
| Format | NetCDF-4 or GeoTIFF |
| Access | Direct HTTPS, no authentication |
| Licence | Free and open; CHC requests citation of Funk et al. 2015 |

## What this is

A quasi-global land precipitation dataset that blends satellite infrared
cold-cloud-duration estimates with rain-gauge station data. Built for
drought monitoring, agricultural monitoring, and humanitarian early
warning, particularly in Africa, South Asia, Central America, and
tropical South America.

Use it when you need long-record rainfall data in the tropics and
subtropics: drought indices, growing-season analysis, flood risk scoping
in data-sparse regions. Not appropriate for the UK or any region
poleward of 50 degrees.

## Coverage warning

**CHIRPS is not truly global.** The dataset covers 50 S to 50 N only.
Everything poleward of those latitudes is outside the domain. This means
CHIRPS does not cover:

- The UK (mostly above 50 N; only the Channel Islands and the southern
  tip of Cornwall are at or below 50 N)
- Most of Europe
- Canada, Alaska, Russia
- Patagonia, Antarctica

For UK precipitation use [ERA5-Land](../era5-land/README.md), HadUK-Grid
(Met Office), or CEH-GEAR. The quickstart below defaults to East Africa
(Kenya/Ethiopia), which is a canonical CHIRPS use case.

## Get data in 5 minutes

No registration. Just:

```bash
pip install requests xarray netcdf4 matplotlib cartopy
python scripts/chirps_download.py
```

The default pulls one year of CHIRPS daily precipitation at 0.25 degrees
and opens it with xarray. A full year of global 0.05 degree daily data
is several GB; for a quickstart the 0.25 degree version is enough.

## Files available

All files served from `https://data.chc.ucsb.edu/products/CHIRPS-2.0/`:

| Product | Path |
|---|---|
| Global daily NetCDF (0.05 deg) | `global_daily/netcdf/p05/chirps-v2.0.<YYYY>.days_p05.nc` |
| Global daily NetCDF (0.25 deg) | `global_daily/netcdf/p25/chirps-v2.0.<YYYY>.days_p25.nc` |
| Global monthly NetCDF (full record) | `global_monthly/netcdf/chirps-v2.0.monthly.nc` |
| Global pentad NetCDF (full record) | `global_pentad/netcdf/chirps-v2.0.pentad.nc` |
| Daily GeoTIFF | `global_daily/tifs/p05/<year>/chirps-v2.0.<yyyy>.<mm>.<dd>.tif.gz` |
| Preliminary daily GeoTIFF | `prelim/global_daily/tifs/p05/<year>/...` |

Regional cut-outs (Africa, East Africa, Central America) also exist
under separate subdirectories if you need smaller files.

## Things to know

- **Preliminary vs final.** Preliminary is available faster (a few days
  lag) with fewer stations; final supersedes it after additional station
  data are incorporated (few weeks lag). For operational monitoring, use
  preliminary and accept possible revisions. For research, use final.
- **Not designed for extreme precipitation quantification.** CHIRPS
  targets monthly-to-seasonal drought monitoring. Short-duration
  extremes and return-period analyses should be cross-validated against
  gauges.
- **Satellite limitations.** Cold-cloud-duration retrievals can miss
  warm-rain and light events, especially over oceans and in cold-cloud-
  poor regimes. Land-only dataset; ocean values are not intended for use.
- **Station density varies.** Regions with sparse gauge networks (parts
  of central Africa, remote highlands) have larger uncertainty.
- **Arid regions.** Small absolute errors can be large in relative
  terms, which matters for drought indices.
- **Orography smoothing.** In areas of strong topographic gradient, the
  0.05 degree grid and the underlying IR signal still smooth real
  rainfall patterns.

## Licence and attribution

CHIRPS is effectively public domain. CHC requests citation of Funk et
al. 2015 and acknowledgement of CHC/USGS in any publication or product
derived from CHIRPS.

## Citation

> Funk, C., Peterson, P., Landsfeld, M., Pedreros, D., Verdin, J.,
> Shukla, S., Husak, G., Rowland, J., Harrison, L., Hoell, A., and
> Michaelsen, J. (2015). The climate hazards infrared precipitation
> with stations - a new environmental record for monitoring extremes.
> Scientific Data, 2, 150066. DOI: 10.1038/sdata.2015.66

## Further reading

- CHIRPS landing: https://www.chc.ucsb.edu/data/chirps
- Data server: https://data.chc.ucsb.edu/products/CHIRPS-2.0/
- FEWS NET (canonical CHIRPS user): https://fews.net/
- ERA5-Land for UK precipitation: [../era5-land/README.md](../era5-land/README.md)
