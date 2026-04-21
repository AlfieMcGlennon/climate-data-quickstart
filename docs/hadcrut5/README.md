# HadCRUT5

Global monthly near-surface temperature anomalies on a 5 degree grid, from
1850 to present.

Produced by the Met Office Hadley Centre and the Climatic Research Unit
(UEA), combining CRUTEM5 land air temperature with HadSST4 sea surface
temperature.

> **Scope of this page.** A getting-started reference for MSc/PhD
> students. Authoritative terms and full caveats at
> https://www.metoffice.gov.uk/hadobs/hadcrut5/.

## When to use this

The standard reference dataset for global warming. If you need to show
how global mean temperature has changed since the 1850s, this is the
dataset that the IPCC and most climate publications use. The 5 degree
grid is coarse, but the record goes back to 1850 and the uncertainty
estimates are well-characterised.

## At a glance

| Property | Value |
|---|---|
| Resolution | 5 degree lat/lon (~555 km cells at the equator) |
| Spatial coverage | Global, 36 x 72 grid cells |
| Temporal resolution | Monthly |
| Temporal coverage | 1850-01 to present |
| Quantity | Temperature anomaly (degC) relative to 1961-1990 climatology |
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

Files live under `https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.<VERSION>/`.
The current sub-version at writing is `5.1.0.0`; pin it in reproducible
pipelines. Check the HadCRUT5 landing page for the latest version.

Files are split by whether they are infilled (under `analysis/`) or
non-infilled (under `non-infilled/`), with per-region summary time series
under `.../diagnostics/`.

| Product | Path (relative to `/data/HadCRUT.5.1.0.0/`) |
|---|---|
| Ensemble mean, infilled (recommended for maps) | `analysis/HadCRUT.5.1.0.0.analysis.anomalies.ensemble_mean.nc` |
| Ensemble mean, non-infilled (gaps where obs sparse) | `non-infilled/HadCRUT.5.1.0.0.noninfilled.anomalies.ensemble_mean.nc` |
| Global monthly time series, infilled (NetCDF) | `analysis/diagnostics/HadCRUT.5.1.0.0.analysis.summary_series.global.monthly.nc` |
| Global annual time series, infilled (NetCDF) | `analysis/diagnostics/HadCRUT.5.1.0.0.analysis.summary_series.global.annual.nc` |

Ensemble-mean NetCDFs are about 30 to 40 MB. 200-member ensemble files
exist but are not listed on the default download page; contact the Met
Office if you need them.

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

> HadCRUT.5.1.0.0 data were obtained from
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
