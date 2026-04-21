# HadCET

Hadley Centre Central England Temperature: monthly from 1659 and daily
from 1772. The longest instrumental temperature record in the world.

Produced by the Met Office Hadley Centre.

> **Scope of this page.** A getting-started reference for students and
> practitioners wanting to use HadCET in dissertations or analysis. The
> authoritative terms and caveats live at
> https://www.metoffice.gov.uk/hadobs/hadcet/.

## When to use this

When you need a long, homogenised temperature record for the UK. 365
years of monthly data makes it the best dataset for studying long-term
climate variability in England, from the Little Ice Age through to the
present. No grid, no spatial dimension, just a single time series, so
it downloads in seconds and is easy to work with.

## At a glance

| Property | Value |
|---|---|
| Type | Single scalar time series (not gridded) |
| Region | A triangular area of lowland central England (Bristol - Lancashire - London roughly) |
| Temporal resolution | Monthly and daily |
| Monthly coverage | 1659-01 to present |
| Daily coverage | 1772-01-01 to present (max/min from 1878) |
| Format | Plain text files, small (~30 kB monthly, ~3-5 MB daily) |
| Access | Direct HTTPS download, no authentication |
| Licence | UK Open Government Licence (commercial use with attribution) |

## What this is

HadCET is not a gridded dataset. It is a single homogenised temperature
record for a triangular area of lowland central England, constructed by
averaging observations from a small rotating set of representative
stations (currently Rothamsted, Malvern, and Stonyhurst). Historical
station changes are stitched together using homogenisation corrections
from Manley (1974) and Parker et al. (1992).

Use it when you need a long, validated, single-number record of UK
temperature evolution: climate change narratives, long-term trend
analysis, contextualising recent years against four centuries of
observation. Do not use it as a UK national average (use HadUK-Grid for
that) and do not treat it as raw station data (values are homogenised).

## Files available

All files are plain text, published at stable URLs on the Hadley Centre
server. Downloading them in full every time is fine; they are small.

| Variable | URL |
|---|---|
| Monthly mean | https://hadleyserver.metoffice.gov.uk/hadcet/data/meantemp_monthly_totals.txt |
| Monthly mean daily max | https://hadleyserver.metoffice.gov.uk/hadcet/data/maxtemp_monthly_totals.txt |
| Monthly mean daily min | https://hadleyserver.metoffice.gov.uk/hadcet/data/mintemp_monthly_totals.txt |
| Daily mean | https://hadleyserver.metoffice.gov.uk/hadcet/data/meantemp_daily_totals.txt |
| Daily max | https://hadleyserver.metoffice.gov.uk/hadcet/data/maxtemp_daily_totals.txt |
| Daily min | https://hadleyserver.metoffice.gov.uk/hadcet/data/mintemp_daily_totals.txt |

All values are degrees Celsius to 0.1 degC resolution. Missing values
are encoded as -99.9 or -99.99; check the file header.

## Get data in 5 minutes

No registration, no token, no account. Just run:

```bash
pip install pandas requests
python scripts/hadcet_download.py
```

The default pulls the monthly mean file, parses it into a tidy long-
format DataFrame, and saves it as a CSV. Edit the config block to switch
between monthly/daily and mean/max/min.

## Things to know

- **Homogenised, not raw.** HadCET incorporates corrections for station
  moves, instrument changes, exposure, and an urban-warming adjustment
  (typically -0.1 to -0.2 C on recent values to counter urbanisation at
  contributing sites). Do not use as a proxy for raw station data.
- **A geographic triangle, not a point or a country.** Good for
  long-term Central England trends; bad for UK-wide averages.
- **Pre-1722 uncertainty.** The earliest monthly values are least
  reliable and some are derived from non-instrumental evidence.
- **Provisional latest values.** The most recent month or day is
  provisional on first release and can be revised in the next update.
- **Urban-adjusted vs unadjusted.** Historically the Met Office has
  published both variants for daily max/min. The current published files
  are the urban-adjusted versions unless the header states otherwise.
- **Different missing-value sentinels.** -99.9 in some files, -99.99 in
  others. Always read the header.

## Licence and attribution

HadCET is published under the UK Open Government Licence with
attribution. Commercial use is permitted. Suggested attribution line:

> HadCET data were obtained from http://www.metoffice.gov.uk/hadobs/hadcet
> on [date] and are British Crown Copyright, Met Office, provided under
> the Open Government Licence.

Current terms: https://www.metoffice.gov.uk/hadobs/hadcet/terms_and_conditions.html

## Citation

Daily series:

> Parker, D. E., Legg, T. P., and Folland, C. K. (1992). A new daily
> Central England Temperature Series, 1772-1991. International Journal of
> Climatology, 12, 317-342. DOI: 10.1002/joc.3370120402

Monthly series extension:

> Manley, G. (1974). Central England temperature: monthly means 1659 to
> 1973. Quarterly Journal of the Royal Meteorological Society, 100,
> 389-405. DOI: 10.1002/qj.49710042511

## Further reading

- Met Office HadCET landing: https://www.metoffice.gov.uk/hadobs/hadcet/
- Data server: https://hadleyserver.metoffice.gov.uk/hadcet/
- HadUK-Grid (for UK-wide 1 km gridded data): https://www.metoffice.gov.uk/hadobs/hadukgrid/
