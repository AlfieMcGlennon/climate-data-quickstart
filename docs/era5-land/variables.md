# ERA5-Land: variable list

Approximately 50 land-surface variables, grouped by category. For full
units and GRIB parameter IDs, consult the ECMWF parameter database:
https://codes.ecmwf.int/grib/param-db/

Soil layers: 0-7 cm, 7-28 cm, 28-100 cm, 100-289 cm (same as ERA5).

## Temperature

| CDS API name | NetCDF | Units |
|---|---|---|
| `2m_temperature` | `t2m` | K |
| `2m_dewpoint_temperature` | `d2m` | K |
| `skin_temperature` | `skt` | K |
| `soil_temperature_level_1` | `stl1` | K |
| `soil_temperature_level_2` | `stl2` | K |
| `soil_temperature_level_3` | `stl3` | K |
| `soil_temperature_level_4` | `stl4` | K |
| `temperature_of_snow_layer` | `tsn` | K |
| `lake_mix_layer_temperature` | `lmlt` | K |
| `lake_bottom_temperature` | `lblt` | K |
| `lake_total_layer_temperature` | `ltlt` | K |
| `lake_ice_temperature` | `lict` | K |

## Moisture and evaporation

| CDS API name | NetCDF | Units |
|---|---|---|
| `total_evaporation` | `e` | m water equivalent |
| `evaporation_from_bare_soil` | `evabs` | m |
| `evaporation_from_the_top_of_canopy` | `evatc` | m |
| `evaporation_from_open_water_surfaces_excluding_oceans` | `evaow` | m |
| `evaporation_from_vegetation_transpiration` | `evavt` | m |
| `potential_evaporation` | `pev` | m (definition changed 18 Nov 2021, see docs) |

## Soil moisture

| CDS API name | NetCDF | Units |
|---|---|---|
| `volumetric_soil_water_layer_1` | `swvl1` | m3 m-3 |
| `volumetric_soil_water_layer_2` | `swvl2` | m3 m-3 |
| `volumetric_soil_water_layer_3` | `swvl3` | m3 m-3 |
| `volumetric_soil_water_layer_4` | `swvl4` | m3 m-3 |
| `skin_reservoir_content` | `src` | m water equivalent |

## Snow

| CDS API name | NetCDF | Units |
|---|---|---|
| `snow_depth` | `sde` | m |
| `snow_depth_water_equivalent` | `sd` | m water equivalent |
| `snow_cover` | `snowc` | % |
| `snow_albedo` | `asn` | 0-1 |
| `snow_density` | `rsn` | kg m-3 |
| `snowfall` | `sf` | m water equivalent |
| `snowmelt` | `smlt` | m water equivalent |
| `snow_evaporation` | `es` | m water equivalent |

## Surface fluxes and radiation

All accumulated over the accumulation window; positive values are downward
to surface (IFS convention).

| CDS API name | NetCDF | Units |
|---|---|---|
| `surface_sensible_heat_flux` | `sshf` | J m-2 |
| `surface_latent_heat_flux` | `slhf` | J m-2 |
| `surface_solar_radiation_downwards` | `ssrd` | J m-2 |
| `surface_thermal_radiation_downwards` | `strd` | J m-2 |
| `surface_net_solar_radiation` | `ssr` | J m-2 |
| `surface_net_thermal_radiation` | `str` | J m-2 |
| `forecast_albedo` | `fal` | 0-1 |

## Wind and pressure

| CDS API name | NetCDF | Units |
|---|---|---|
| `10m_u_component_of_wind` | `u10` | m s-1 |
| `10m_v_component_of_wind` | `v10` | m s-1 |
| `surface_pressure` | `sp` | Pa |

## Precipitation and runoff

| CDS API name | NetCDF | Units |
|---|---|---|
| `total_precipitation` | `tp` | m |
| `runoff` | `ro` | m |
| `surface_runoff` | `sro` | m |
| `sub_surface_runoff` | `ssro` | m |

## Lakes

| CDS API name | NetCDF | Units |
|---|---|---|
| `lake_mix_layer_depth` | `lmld` | m |
| `lake_shape_factor` | `lshf` | dimensionless |
| `lake_ice_depth` | `licd` | m |

## Vegetation

| CDS API name | NetCDF | Units |
|---|---|---|
| `leaf_area_index_low_vegetation` | `lai_lv` | m2 m-2 |
| `leaf_area_index_high_vegetation` | `lai_hv` | m2 m-2 |
