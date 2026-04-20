# HadCRUT5

Global monthly near-surface temperature anomalies on a 5 degree grid, from
1850 to present.

Produced by the Met Office Hadley Centre and the Climatic Research Unit
(UEA), combining CRUTEM5 land air temperature with HadSST4 sea surface
temperature.

> **Scope of this page.** A getting-started reference for MSc/PhD
> students. Authoritative terms and full caveats at
> https://www.metoffice.gov.uk/hadobs/hadcrut5/.

## At a glance

| Property | Value |
|---|---|
| Resolution | 5 degree lat/lon (~555 km cells at the equator) |
| Coverage | Global, 36 x 72 grid cells |
| Temporal resolution | Monthly |
| Coverage | 1850-01 to present |
| Quantity | Temperature anomaly relative to 1961-1990 climatology |
| Products | Ensemble mean (infilled + non-infilled), 200-member ensemble |
| Format | NetCDF, plus CSV summary time series |
| Access | Direct HTTPS download, no authentication |
| Licence | UK Open Government Licence (commercial use with attribution) |

## What this is

A global gridded dataset of temperature **anomalies** (not absolute
temperatures). Anomalies are departures from the 1961-1990 climatology.
Values are blended between land (CRUTEM5) and ocean (HadSST4) data. A
200-member ensemble represents observational, coverage, and bias-
correction uncertainty.

Two analyses are served:

- **Non-infilled**: grid cells without sufficient underlying observations
  are missing. Honest about coverage, biased downward in global means
  because polar and 19th-century cells are excluded.
- **Infilled**: a Gaussian-process method fills data-sparse regions
  (polar regions, 19th century) conditioned on observations and ensemble
  covariance. Best for maps and simple global-mean analyses.

Use it when you need the authoritative long-term record of global
temperature change: climate change narratives, trend analysis, comparing
recent warming against the pre-industrial baseline. For hourly or daily
data, use ERA5. For regional UK analysis, use HadUK-Grid (not in this
repo).

## Files available

Files live under https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/.
The current sub-version at writing is `5.0.2.0`; pin it in reproducible
pipelines.

| Product | URL |
|---|---|
| Ensemble mean, non-infilled | `.../analysis/HadCRUT.5.0.2.0.analysis.anomalies.ensemble_mean.nc` |
| Ensemble mean, infilled | `.../analysis/HadCRUT.5.0.2.0.analysis.anomalies.ensemble_mean.infilled.nc` |
| Ensemble members (200 x non-infilled) | `.../analysis/HadCRUT.5.0.2.0.analysis.anomalies.<N>.nc` (N=1..200) |
| Ensemble members (200 x infilled) | `.../analysis/HadCRUT.5.0.2.0.analysis.anomalies.<N>.infilled.nc` |
| Global monthly time series (CSV) | `.../analysis/diagnostics/HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv` |
| Global annual time series (CSV) | `.../analysis/diagnostics/HadCRUT.5.0.2.0.analysis.summary_series.global.annual.csv` |

Ensemble-mean files are a few tens of MB. Full 200-member ensembles are a
few GB each.

## Get data in 5 minutes

No registration. Just:

```bash
pip install requests xarray netcdf4 matplotlib
python scripts/hadcrut5_download.py
```

The default pulls the infilled ensemble-mean NetCDF and prints a global
summary.

## Things to know

- **Anomalies, not absolute temperatures.** Values are departures from
  1961-1990 climatology. To recover absolute temperature, add a separate
  climatology (CRU TS 1961-1990 or ERA5); the sum inherits additional
  uncertainty.
- **Different baseline from other datasets.** HadCRUT5 uses 1961-1990.
  NOAA uses 1901-2000, NASA GISS uses 1951-1980, ERA5 often uses
  1991-2020. Rebaseline before comparing.
- **5 degree grid means ~500 km cells.** Not suitable for local or
  city-scale analysis. Use HadUK-Grid or ERA5 for regional work.
- **Use the ensemble for uncertainty.** The 200 members capture
  bias-correction, homogenisation, and sampling uncertainty. Trend work
  should propagate the ensemble, not just use the ensemble mean.
- **Infilled values are not observed.** In data-void regions the infilled
  product fills with statistical imputation. Carry the associated
  uncertainty; do not treat infilled cells as if observed.
- **Sub-version bumps happen.** The patch level changes when inputs are
  reissued. Pin the sub-version string in reproducible code.

## Licence and attribution

Published by the Met Office Hadley Centre and CRU UEA under the UK Open
Government Licence. Commercial use is permitted with attribution.
Suggested line:

> HadCRUT.5.0.2.0 data were obtained from
> https://www.metoffice.gov.uk/hadobs/hadcrut5 on [date] and are British
> Crown Copyright, Met Office, and (c) Climatic Research Unit, University
> of East Anglia, provided under the Open Government Licence.

Current terms: https://www.metoffice.gov.uk/hadobs/hadcrut5/terms_and_conditions.html

## Citation

> Morice, C. P., Kennedy, J. J., Rayner, N. A., Winn, J. P., Hogan, E.,
> Killick, R. E., Dunn, R. J. H., Osborn, T. J., Jones, P. D., and
> Simpson, I. R. (2021). An updated assessment of near-surface
> temperature change from 1850: the HadCRUT5 data set. Journal of
> Geophysical Research: Atmospheres, 126, e2019JD032361.
> DOI: 10.1029/2019JD032361

## Further reading

- Landing page: https://www.metoffice.gov.uk/hadobs/hadcrut5/
- Current data directory: https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/
- HadCET (Central England, long single-station record): [../hadcet/README.md](../hadcet/README.md)
