# ERA5 single levels: full variable list

Variables are grouped by the categories used in the CDS download form. Names
shown are the exact strings expected by the CDS API (snake_case).

For units and the corresponding GRIB short names, consult the ECMWF parameter
database: https://codes.ecmwf.int/grib/param-db/

The CDS download form advertises more than 250 parameters in total. The list
below covers the common variables grouped by category; for the full
authoritative list see the CDS "Download data" tab.

## Temperature and pressure

- `2m_temperature`
- `2m_dewpoint_temperature`
- `mean_sea_level_pressure`
- `surface_pressure`
- `sea_surface_temperature`
- `skin_temperature`
- `maximum_2m_temperature_since_previous_post_processing`
- `minimum_2m_temperature_since_previous_post_processing`
- `ice_temperature_layer_1`
- `ice_temperature_layer_2`
- `ice_temperature_layer_3`
- `ice_temperature_layer_4`

## Wind

- `10m_u_component_of_wind`
- `10m_v_component_of_wind`
- `100m_u_component_of_wind`
- `100m_v_component_of_wind`
- `10m_u_component_of_neutral_wind`
- `10m_v_component_of_neutral_wind`
- `instantaneous_10m_wind_gust`
- `10m_wind_gust_since_previous_post_processing`

## Mean rates

- `mean_convective_precipitation_rate`
- `mean_large_scale_precipitation_rate`
- `mean_total_precipitation_rate`
- `mean_evaporation_rate`
- `mean_snowfall_rate`
- `mean_surface_sensible_heat_flux`
- `mean_surface_latent_heat_flux`
- `mean_surface_net_short_wave_radiation_flux`
- `mean_surface_downward_short_wave_radiation_flux`
- `mean_surface_downward_long_wave_radiation_flux`
- `mean_boundary_layer_dissipation`
- `mean_eastward_turbulent_surface_stress`
- `mean_northward_turbulent_surface_stress`
- `mean_runoff_rate`

## Radiation and heat

- `surface_solar_radiation_downwards`
- `surface_thermal_radiation_downwards`
- `surface_solar_radiation_downward_clear_sky`
- `surface_thermal_radiation_downward_clear_sky`
- `surface_net_solar_radiation`
- `surface_net_thermal_radiation`
- `toa_incident_solar_radiation`
- `top_net_solar_radiation`
- `top_net_thermal_radiation`
- `clear_sky_direct_solar_radiation_at_surface`
- `downward_uv_radiation_at_the_surface`
- `instantaneous_surface_sensible_heat_flux`

## Clouds

- `total_cloud_cover`
- `high_cloud_cover`
- `medium_cloud_cover`
- `low_cloud_cover`
- `cloud_base_height`
- `total_column_cloud_liquid_water`
- `total_column_cloud_ice_water`

## Lakes

- `lake_cover`
- `lake_depth`
- `lake_ice_depth`
- `lake_ice_temperature`
- `lake_mix_layer_temperature`
- `lake_bottom_temperature`
- `lake_total_layer_temperature`
- `lake_mix_layer_depth`
- `lake_shape_factor`

## Evaporation and runoff

- `evaporation`
- `potential_evaporation`
- `runoff`
- `surface_runoff`
- `sub_surface_runoff`

## Precipitation and rain

- `total_precipitation`
- `convective_precipitation`
- `large_scale_precipitation`
- `precipitation_type`
- `total_column_rain_water`

## Snow

- `snowfall`
- `convective_snowfall`
- `large_scale_snowfall`
- `snow_depth`
- `snow_albedo`
- `snow_density`
- `snowmelt`
- `snow_evaporation`
- `total_column_snow_water`
- `temperature_of_snow_layer`

## Soil

- `soil_temperature_level_1`
- `soil_temperature_level_2`
- `soil_temperature_level_3`
- `soil_temperature_level_4`
- `volumetric_soil_water_layer_1`
- `volumetric_soil_water_layer_2`
- `volumetric_soil_water_layer_3`
- `volumetric_soil_water_layer_4`
- `soil_type`

## Vertical integrals

- `vertical_integral_of_temperature`
- `vertical_integral_of_moisture_divergence`
- `vertically_integrated_moisture_divergence`
- `total_column_water_vapour`
- `total_column_water`

## Vegetation

- `high_vegetation_cover`
- `low_vegetation_cover`
- `leaf_area_index_high_vegetation`
- `leaf_area_index_low_vegetation`
- `type_of_high_vegetation`
- `type_of_low_vegetation`

## Ocean waves

- `significant_height_of_combined_wind_waves_and_swell`
- `mean_wave_period`
- `mean_wave_direction`
- `significant_height_of_wind_waves`
- `mean_period_of_wind_waves`
- `significant_height_of_total_swell`
- `peak_wave_period`
- `mean_zero_crossing_wave_period`
