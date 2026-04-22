# E-OBS

European land-only gridded daily observational dataset, from station
interpolation, 1950 to near-present.

Produced by the ECA&D project at KNMI, distributed via the Copernicus
Climate Data Store.

> **Scope of this page.** A getting-started reference. Authoritative
> terms at https://www.ecad.eu/ and on the CDS dataset page.

## When to use this

When you need daily European observations on a grid. E-OBS interpolates
station data onto a regular grid, giving you something closer to ground
truth than ERA5 but with spatial coverage. Good for validating model
output against observations over Europe, or for studies that need
observed (not reanalysed) temperature and precipitation fields.

## At a glance

| Property | Value |
|---|---|
| Resolution | 0.1 degrees (~11 km) or 0.25 degrees |
| Coverage | Europe land only, 25N-71.5N, 25W-45E |
| Temporal resolution | Daily |
| Temporal coverage | 1950-01-01 to near-present |
| Variables | Mean/max/min temperature, precipitation, MSLP, humidity, radiation, wind speed |
| Products | Ensemble mean + 100-member ensemble (for temperature and precipitation) |
| Version | Versioned (e.g. v29.0e); bumps refresh the archive with more stations |
| Dataset ID (CDS) | `insitu-gridded-observations-europe` |
| Licence | ECA&D data policy (free for research, commercial use requires permission) |

## What this is

The observational counterpart to ERA5 over Europe. Station records from
the ECA&D network are quality-controlled and interpolated onto a
regular grid. Use it when you need validated observations to compare
against reanalyses or regional climate models.

Not a reanalysis, not a model product: values come from actual stations.
For sub-daily work, use ERA5 or station data directly. For UK-only
analysis, Met Office HadUK-Grid uses a denser UK station network.

## Variables

| CDS API name | ECA&D short | Units |
|---|---|---|
| `mean_temperature` | TG | degC |
| `maximum_temperature` | TX | degC |
| `minimum_temperature` | TN | degC |
| `precipitation_amount` | RR | mm per day |
| `mean_sea_level_pressure` | PP | hPa |
| `relative_humidity` | HU | % |
| `global_radiation` | QQ | W m-2 |
| `wind_speed` | FG | m s-1 |

## Get data in 5 minutes

1. Register for a free CDS account at https://cds.climate.copernicus.eu/
2. Sign in, go to the E-OBS dataset page, and accept the licence in the
   download form.
3. Click your name (top right) and copy your **Personal Access Token**.
4. Create `~/.cdsapirc` (on Windows: `C:\Users\<you>\.cdsapirc`) with:
   ```
   url: https://cds.climate.copernicus.eu/api
   key: YOUR_TOKEN
   ```
   If you already have this file from another CDS dataset, skip this step.
5. `pip install cdsapi xarray netcdf4`
6. Run `python scripts/e_obs_download.py`

The default pulls the ensemble-mean daily mean temperature at 0.1 degree
resolution for the latest version. Files are large (~1 GB per variable
for the full period); the script unzips the CDS response.

## Things to know

- **Whole-period files.** E-OBS is not time-slicable in the request. The
  CDS returns the entire 1950-present history in a single file per
  variable, per version. Subset with xarray after download.
- **Version matters.** Versions bump when more stations are added or
  interpolation is retuned; the same day/cell can differ between
  versions. Pin the version (e.g. `29.0e`) in reproducible work and
  archive a local copy of the files used.
- **Interpolation smooths extremes.** Daily maxima on the grid are
  systematically lower, and daily minima systematically higher, than at
  the underlying stations. Area-average metrics are more robust than
  single-cell extremes.
- **Station density varies.** Eastern Europe, the Balkans, Iberia, and
  high-elevation regions have lower station density and larger
  interpolation uncertainty.
- **Ensemble for uncertainty.** Use the 100-member ensemble (via
  `product_type: "ensemble_members"` or `ensemble_spread`) if you need
  uncertainty propagation; the mean field is enough for most quickstart
  use.
- **Output is zipped NetCDF.** Unzip before opening with xarray (the
  script handles this).

## Licence and attribution

Under the ECA&D data policy: free for research and education with
attribution. Commercial use and redistribution require prior permission
from ECA&D/KNMI.

Acknowledge ECA&D, cite Cornes et al. (2018), and state the exact E-OBS
version used.

Check current terms:
- https://www.ecad.eu/documents/ECAD_datapolicy.pdf
- The licence tab on the CDS dataset page

## Citation

> Cornes, R. C., van der Schrier, G., van den Besselaar, E. J. M., and
> Jones, P. D. (2018): An Ensemble Version of the E-OBS Temperature and
> Precipitation Data Sets. Journal of Geophysical Research: Atmospheres,
> 123, 9391-9409. DOI: 10.1029/2017JD028200

Plus the version used, for example "E-OBS v29.0e, obtained from the
Copernicus Climate Data Store, dataset `insitu-gridded-observations-europe`".

## Further reading

- CDS dataset page: https://cds.climate.copernicus.eu/datasets/insitu-gridded-observations-europe
- ECA&D project: https://www.ecad.eu/
- HadUK-Grid (UK-focused alternative): https://www.metoffice.gov.uk/hadobs/hadukgrid/
- ERA5 single levels in this repo: [../era5-single-levels/README.md](../era5-single-levels/README.md)
