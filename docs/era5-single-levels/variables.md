# ERA5 single levels: full variable list

Variables are grouped by the categories used in the CDS download form. Each
entry shows the CDS API name (snake_case, what you pass to
`cdsapi.Client().retrieve()` in the `variable` list) and a short description.

For authoritative units, the GRIB parameter ID, and the full mathematical
definition, consult the ECMWF parameter database:
https://codes.ecmwf.int/grib/param-db/

Units given here are the conventional ERA5 units as reported on the CDS
overview page. "Accumulated" values reset at the start of each forecast
accumulation window (typically every 6 or 12 hours for ERA5); for hourly
outputs in the CDS, the value is the accumulation over the preceding hour
unless otherwise noted.

## Temperature and pressure

| CDS API name | Description | Units |
|---|---|---|
| `2m_temperature` | Air temperature at 2 metres above the surface of land, sea or inland water | K |
| `2m_dewpoint_temperature` | Dewpoint at 2 metres; a measure of near-surface humidity | K |
| `mean_sea_level_pressure` | Atmospheric pressure reduced to mean sea level | Pa |
| `surface_pressure` | Pressure at the surface of land, sea or inland water (unreduced) | Pa |
| `sea_surface_temperature` | Temperature of sea water near the surface | K |
| `skin_temperature` | Temperature at the radiating surface (bare soil, vegetation canopy, sea, or ice) | K |
| `maximum_2m_temperature_since_previous_post_processing` | Maximum 2 m temperature over the preceding accumulation window | K |
| `minimum_2m_temperature_since_previous_post_processing` | Minimum 2 m temperature over the preceding accumulation window | K |
| `ice_temperature_layer_1` | Sea-ice temperature, top layer (layer structure from the LIM2 sea-ice scheme; layer thicknesses are not published in the public ERA5 Confluence pages, consult the IFS documentation) | K |
| `ice_temperature_layer_2` | Sea-ice temperature, layer 2 | K |
| `ice_temperature_layer_3` | Sea-ice temperature, layer 3 | K |
| `ice_temperature_layer_4` | Sea-ice temperature, layer 4 (bottom) | K |

## Wind

| CDS API name | Description | Units |
|---|---|---|
| `10m_u_component_of_wind` | Eastward (zonal) wind at 10 m above the surface | m s-1 |
| `10m_v_component_of_wind` | Northward (meridional) wind at 10 m | m s-1 |
| `100m_u_component_of_wind` | Eastward wind at 100 m; relevant for wind-energy studies | m s-1 |
| `100m_v_component_of_wind` | Northward wind at 100 m | m s-1 |
| `10m_u_component_of_neutral_wind` | Eastward wind at 10 m assuming neutral atmospheric stability | m s-1 |
| `10m_v_component_of_neutral_wind` | Northward wind at 10 m assuming neutral atmospheric stability | m s-1 |
| `instantaneous_10m_wind_gust` | Wind gust at 10 m, instantaneous snapshot | m s-1 |
| `10m_wind_gust_since_previous_post_processing` | Maximum wind gust at 10 m over the preceding accumulation window | m s-1 |

## Mean rates

Mean rates are time-averaged fluxes since the previous post-processing step;
they are the preferred form for most flux analyses and avoid the
accumulation-reset gotcha of the "surface_solar_radiation_downwards" style
variables.

| CDS API name | Description | Units |
|---|---|---|
| `mean_convective_precipitation_rate` | Mean rate of convective (sub-grid) precipitation | kg m-2 s-1 |
| `mean_large_scale_precipitation_rate` | Mean rate of large-scale (stratiform, resolved) precipitation | kg m-2 s-1 |
| `mean_total_precipitation_rate` | Mean rate of total precipitation (convective + large-scale) | kg m-2 s-1 |
| `mean_evaporation_rate` | Mean surface evaporation rate. ECMWF uses the downward-positive flux convention, so evaporation is reported as **negative** (upward, loss to atmosphere); positive values indicate condensation | kg m-2 s-1 |
| `mean_snowfall_rate` | Mean snowfall rate (water equivalent) | kg m-2 s-1 |
| `mean_surface_sensible_heat_flux` | Mean surface sensible heat flux | W m-2 |
| `mean_surface_latent_heat_flux` | Mean surface latent heat flux | W m-2 |
| `mean_surface_net_short_wave_radiation_flux` | Mean net shortwave radiation at the surface (down minus up) | W m-2 |
| `mean_surface_downward_short_wave_radiation_flux` | Mean downward shortwave radiation at the surface | W m-2 |
| `mean_surface_downward_long_wave_radiation_flux` | Mean downward longwave radiation at the surface | W m-2 |
| `mean_boundary_layer_dissipation` | Mean turbulent dissipation in the boundary layer | W m-2 |
| `mean_eastward_turbulent_surface_stress` | Mean zonal turbulent surface stress | N m-2 |
| `mean_northward_turbulent_surface_stress` | Mean meridional turbulent surface stress | N m-2 |
| `mean_runoff_rate` | Mean total runoff rate (surface + subsurface) | kg m-2 s-1 |

## Radiation and heat

These are the accumulated counterparts of the "mean_..." rates: energy flux
integrated over the accumulation window. Divide by the window length in
seconds to recover an average rate.

| CDS API name | Description | Units |
|---|---|---|
| `surface_solar_radiation_downwards` | Accumulated downward shortwave (solar) radiation at the surface | J m-2 |
| `surface_thermal_radiation_downwards` | Accumulated downward longwave (thermal) radiation at the surface | J m-2 |
| `surface_solar_radiation_downward_clear_sky` | Downward shortwave assuming no cloud; useful as a clear-sky reference | J m-2 |
| `surface_thermal_radiation_downward_clear_sky` | Downward longwave assuming no cloud | J m-2 |
| `surface_net_solar_radiation` | Net shortwave at the surface (down minus up) | J m-2 |
| `surface_net_thermal_radiation` | Net longwave at the surface | J m-2 |
| `toa_incident_solar_radiation` | Incoming solar radiation at the top of atmosphere | J m-2 |
| `top_net_solar_radiation` | Net shortwave at top of atmosphere | J m-2 |
| `top_net_thermal_radiation` | Outgoing longwave at top of atmosphere; proxy for earth's thermal emission | J m-2 |
| `clear_sky_direct_solar_radiation_at_surface` | Direct (beam) shortwave at the surface assuming clear sky | J m-2 |
| `downward_uv_radiation_at_the_surface` | Downward UV radiation at the surface | J m-2 |
| `instantaneous_surface_sensible_heat_flux` | Surface sensible heat flux, instantaneous (not accumulated) | W m-2 |

## Clouds

| CDS API name | Description | Units |
|---|---|---|
| `total_cloud_cover` | Fraction of the grid cell covered by cloud in the vertical column | 0-1 |
| `high_cloud_cover` | Fraction covered by high cloud (above roughly 400 hPa) | 0-1 |
| `medium_cloud_cover` | Fraction covered by medium cloud (roughly 400-800 hPa) | 0-1 |
| `low_cloud_cover` | Fraction covered by low cloud (below roughly 800 hPa) | 0-1 |
| `cloud_base_height` | Height of cloud base above ground level | m |
| `total_column_cloud_liquid_water` | Vertically integrated liquid water in clouds | kg m-2 |
| `total_column_cloud_ice_water` | Vertically integrated ice water in clouds | kg m-2 |

## Lakes

ERA5's lake scheme (FLake) provides a handful of lake-specific variables for
grid cells with non-zero lake fraction.

| CDS API name | Description | Units |
|---|---|---|
| `lake_cover` | Fraction of the grid cell covered by lake water | 0-1 |
| `lake_depth` | Mean depth of the lake in the grid cell | m |
| `lake_ice_depth` | Thickness of ice on the lake surface | m |
| `lake_ice_temperature` | Temperature of the lake ice | K |
| `lake_mix_layer_temperature` | Temperature of the lake's surface mixed layer | K |
| `lake_bottom_temperature` | Temperature at the lake bottom | K |
| `lake_total_layer_temperature` | Bulk temperature averaged over the full lake depth | K |
| `lake_mix_layer_depth` | Depth of the lake's surface mixed layer | m |
| `lake_shape_factor` | Shape factor for the lake thermocline profile | dimensionless |

## Evaporation and runoff

| CDS API name | Description | Units |
|---|---|---|
| `evaporation` | Accumulated surface evaporation. Downward-positive flux convention: evaporation is reported as **negative** (loss from surface to atmosphere); positive values indicate condensation | m of water equivalent |
| `potential_evaporation` | Accumulated potential evaporation (evaporation demand assuming unlimited water) | m of water equivalent |
| `runoff` | Accumulated total runoff (surface + subsurface) | m |
| `surface_runoff` | Accumulated surface runoff | m |
| `sub_surface_runoff` | Accumulated subsurface runoff | m |

## Precipitation and rain

| CDS API name | Description | Units |
|---|---|---|
| `total_precipitation` | Accumulated precipitation (liquid plus frozen) over the accumulation window | m |
| `convective_precipitation` | Accumulated convective precipitation (sub-grid, parametrised) | m |
| `large_scale_precipitation` | Accumulated large-scale (stratiform, resolved) precipitation | m |
| `precipitation_type` | Categorical precipitation type code (rain, snow, freezing rain, sleet, etc.) | code 0-8 |
| `total_column_rain_water` | Vertically integrated rain water in the atmosphere | kg m-2 |

## Snow

| CDS API name | Description | Units |
|---|---|---|
| `snowfall` | Accumulated snowfall (water equivalent) | m of water equivalent |
| `convective_snowfall` | Accumulated convective snowfall | m of water equivalent |
| `large_scale_snowfall` | Accumulated large-scale snowfall | m of water equivalent |
| `snow_depth` | Snow depth expressed as equivalent liquid water on open ground | m of water equivalent |
| `snow_albedo` | Albedo of the snow surface | 0-1 |
| `snow_density` | Snow density | kg m-3 |
| `snowmelt` | Accumulated snowmelt | m of water equivalent |
| `snow_evaporation` | Accumulated evaporation from the snowpack | m of water equivalent |
| `total_column_snow_water` | Vertically integrated snow water in the atmosphere | kg m-2 |
| `temperature_of_snow_layer` | Temperature of the snow layer | K |

## Soil

ERA5 uses four soil layers of fixed thickness: 0-7 cm, 7-28 cm, 28-100 cm,
and 100-289 cm.

| CDS API name | Description | Units |
|---|---|---|
| `soil_temperature_level_1` | Soil temperature, layer 1 (0-7 cm) | K |
| `soil_temperature_level_2` | Soil temperature, layer 2 (7-28 cm) | K |
| `soil_temperature_level_3` | Soil temperature, layer 3 (28-100 cm) | K |
| `soil_temperature_level_4` | Soil temperature, layer 4 (100-289 cm) | K |
| `volumetric_soil_water_layer_1` | Volumetric soil moisture, layer 1 (0-7 cm) | m3 m-3 |
| `volumetric_soil_water_layer_2` | Volumetric soil moisture, layer 2 (7-28 cm) | m3 m-3 |
| `volumetric_soil_water_layer_3` | Volumetric soil moisture, layer 3 (28-100 cm) | m3 m-3 |
| `volumetric_soil_water_layer_4` | Volumetric soil moisture, layer 4 (100-289 cm) | m3 m-3 |
| `soil_type` | Categorical soil type classification | code |

## Vertical integrals

| CDS API name | Description | Units |
|---|---|---|
| `vertical_integral_of_temperature` | Vertically integrated air temperature through the column | K kg m-2 |
| `vertical_integral_of_moisture_divergence` | Vertical integral of moisture flux divergence | kg m-2 s-1 |
| `vertically_integrated_moisture_divergence` | Alias for the above; same field under a different naming convention | kg m-2 s-1 |
| `total_column_water_vapour` | Total precipitable water (water vapour in the column) | kg m-2 |
| `total_column_water` | Total column water (vapour plus liquid plus ice plus snow) | kg m-2 |

## Vegetation

| CDS API name | Description | Units |
|---|---|---|
| `high_vegetation_cover` | Fraction of the grid cell covered by high vegetation (trees) | 0-1 |
| `low_vegetation_cover` | Fraction covered by low vegetation (grass, crops) | 0-1 |
| `leaf_area_index_high_vegetation` | Leaf area index of high vegetation | m2 m-2 |
| `leaf_area_index_low_vegetation` | Leaf area index of low vegetation | m2 m-2 |
| `type_of_high_vegetation` | Dominant high-vegetation type code | code |
| `type_of_low_vegetation` | Dominant low-vegetation type code | code |

## Ocean waves

Wave variables come from the coupled ECMWF wave model on a reduced
latitude/longitude grid at approximately 0.36 degree resolution (not the
0.25 degree atmospheric grid). Coverage is ocean only.

| CDS API name | Description | Units |
|---|---|---|
| `significant_height_of_combined_wind_waves_and_swell` | Significant wave height of the total sea state | m |
| `mean_wave_period` | Mean wave period of the total spectrum | s |
| `mean_wave_direction` | Mean direction waves are coming from | degrees (true) |
| `significant_height_of_wind_waves` | Significant height of wind-sea waves only | m |
| `mean_period_of_wind_waves` | Mean period of wind-sea waves | s |
| `significant_height_of_total_swell` | Significant height of swell only | m |
| `peak_wave_period` | Period at the spectral peak | s |
| `mean_zero_crossing_wave_period` | Mean zero-crossing wave period | s |
