# GPWv4

Gridded Population of the World, Version 4, Revision 11: global
population density and count on a 30 arc-second grid, with aggregated
resolutions up to 1 degree.

Produced by CIESIN (Columbia University), distributed by NASA SEDAC.

> **Scope of this page.** A getting-started reference for GPWv4
> population density. For the full documentation see
> https://sedac.ciesin.columbia.edu/data/collection/gpw-v4 and the
> [GPWv4 documentation PDF](https://sedac.ciesin.columbia.edu/downloads/docs-repo/gpw-v4-rev11-documentation.pdf).

## When to use this

When you need a transparent, census-based population grid as an exposure
layer for climate risk analysis. GPWv4 is the standard choice for
overlaying population on climate hazard maps (heat, flood, drought) to
estimate affected populations. It uses uniform distribution within
administrative units with no ancillary modelling, making it a clean
baseline. For dasymetric alternatives (using land cover and nightlights
to redistribute population within units), see WorldPop or GHS-POP.

## At a glance

| Property | Value |
|---|---|
| Resolution | 30 arc-seconds (~1 km); also 2.5, 15, 30 arc-min and 1 degree |
| Coverage | Global |
| Temporal coverage | 2000, 2005, 2010, 2015, 2020 (five discrete snapshots) |
| Format | GeoTIFF, ASCII, NetCDF-4 |
| Access | NASA Earthdata login required (free) |
| CRS | WGS84 (EPSG:4326) |
| Licence | CC BY 4.0 |

## What this is

GPWv4 models human population distribution on a continuous global raster.
It uses proportional allocation from approximately 13.5 million national
and sub-national administrative units (2010 census round) to assign
population counts to grid cells. Population density is derived by
dividing count by land area.

The collection contains multiple products: population count, population
density, UN WPP-adjusted variants, basic demographics, data quality
indicators, and ancillary grids. For climate risk work, population
density at 2.5 arc-minute resolution is the typical starting point.

## Get data in 5 minutes

Requires a free [NASA Earthdata account](https://urs.earthdata.nasa.gov/users/new).
After registration, create a `~/.netrc` file (or `~/_netrc` on Windows):

```
machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD
```

Then:

```bash
pip install requests rioxarray rasterio xarray matplotlib cartopy numpy
python scripts/gpw_population_download.py
```

The default pulls population density for 2020 at 2.5 arc-minute
resolution (~tens of MB).

## Files available

All files served from SEDAC at
`https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/`.

| Product | Slug | Years |
|---|---|---|
| Population Count | `gpw-v4-population-count-rev11` | 2000-2020 |
| Population Density | `gpw-v4-population-density-rev11` | 2000-2020 |
| UN WPP-Adjusted Count | `gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals-rev11` | 2000-2020 |
| UN WPP-Adjusted Density | `gpw-v4-population-density-adjusted-to-2015-unwpp-country-totals-rev11` | 2000-2020 |
| Basic Demographics | `gpw-v4-basic-demographic-characteristics-rev11` | 2010 only |

Resolutions available: 30 arc-sec, 2.5 arc-min, 15 arc-min, 30 arc-min,
1 degree. All in GeoTIFF, ASCII, and NetCDF-4.

Filename pattern (GeoTIFF):
`gpw_v4_population_density_rev11_{year}_{resolution}.tif`
where resolution is `30_sec`, `2pt5_min`, `15_min`, `30_min`, or `1_deg`.

## Things to know

- **Uniform distribution.** Population is spread evenly within each
  administrative unit. Large rural areas may show inflated density where
  people actually cluster in villages.
- **Census timing.** Input data are from the 2010 census round
  (2005-2014). The 2020 layer is an extrapolation, not an observation.
- **Not a time series.** Five discrete snapshots, not continuous or
  interpolated data. Do not interpolate between years without
  understanding the methodology.
- **File sizes.** The 30 arc-second global GeoTIFF is several GB. Use
  2.5 arc-minute for most climate risk work.
- **GeoTIFF format.** Unlike most other datasets in this toolkit, GPWv4
  uses GeoTIFF as the primary format, requiring `rioxarray` and
  `rasterio` in addition to the standard stack.
- **NoData encoding.** GeoTIFFs use a large negative float as NoData
  (typically -3.4028235e+38). Ensure your reader respects this value.
- **Zip-compressed.** Downloads are zip files containing the GeoTIFF
  plus metadata files.

## Licence and attribution

CC BY 4.0. The Earthdata login is required to download, but the data
itself is openly licenced once obtained. Users must cite CIESIN/SEDAC
and the relevant DOI. Commercial use is permitted.

## Citation

> Center for International Earth Science Information Network - CIESIN -
> Columbia University. 2018. Gridded Population of the World, Version 4
> (GPWv4): Population Density, Revision 11. Palisades, New York: NASA
> Socioeconomic Data and Applications Center (SEDAC).
> https://doi.org/10.7927/H49C6VHW

> Doxsey-Whitfield, E., MacManus, K., Adamo, S. B., et al. (2015).
> Taking Advantage of the Improved Availability of Census Data: A First
> Look at the Gridded Population of the World, Version 4. Papers in
> Applied Geography, 1(3), 226-235.
> https://doi.org/10.1080/23754931.2015.1014272

## Further reading

- GPWv4 collection: https://sedac.ciesin.columbia.edu/data/collection/gpw-v4
- Population Density product: https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11
- Full documentation PDF: https://sedac.ciesin.columbia.edu/downloads/docs-repo/gpw-v4-rev11-documentation.pdf
- WorldPop (dasymetric alternative): https://www.worldpop.org/
- GHS-POP (dasymetric alternative): https://ghsl.jrc.ec.europa.eu/ghs_pop.php
