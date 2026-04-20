# ERA5 pressure levels: full variable list

All 16 variables are available on all 37 pressure levels (1, 2, 3, 5, 7,
10, 20, 30, 50, 70, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400,
450, 500, 550, 600, 650, 700, 750, 775, 800, 825, 850, 875, 900, 925,
950, 975, 1000 hPa).

For full units and the GRIB parameter ID, consult the ECMWF parameter
database: https://codes.ecmwf.int/grib/param-db/

| CDS API name | Short name | Description | Units |
|---|---|---|---|
| `geopotential` | `z` | Gravitational potential energy per unit mass at a given pressure level. Divide by 9.80665 to get geopotential height in metres. | m2 s-2 |
| `temperature` | `t` | Air temperature on the pressure surface. | K |
| `u_component_of_wind` | `u` | Eastward (zonal) wind speed on the pressure surface. | m s-1 |
| `v_component_of_wind` | `v` | Northward (meridional) wind speed on the pressure surface. | m s-1 |
| `specific_humidity` | `q` | Mass of water vapour per unit mass of moist air. | kg kg-1 |
| `relative_humidity` | `r` | Ratio of the actual vapour pressure to the saturation vapour pressure at the local temperature. | % |
| `vertical_velocity` | `w` | Vertical velocity in pressure coordinates (omega). Positive values indicate downward motion. | Pa s-1 |
| `divergence` | `d` | Horizontal divergence of the wind field. | s-1 |
| `vorticity` | `vo` | Vertical component of the relative vorticity. | s-1 |
| `potential_vorticity` | `pv` | Ertel potential vorticity. Conserved under adiabatic, frictionless flow. | K m2 kg-1 s-1 |
| `fraction_of_cloud_cover` | `cc` | Fraction of grid box at this pressure level covered by cloud. | 0-1 |
| `ozone_mass_mixing_ratio` | `o3` | Mass of ozone per unit mass of air. Meaningful mainly at stratospheric levels (above ~100 hPa). | kg kg-1 |
| `specific_cloud_liquid_water_content` | `clwc` | Mass of liquid water in cloud per unit mass of moist air. | kg kg-1 |
| `specific_cloud_ice_water_content` | `ciwc` | Mass of cloud ice per unit mass of moist air. | kg kg-1 |
| `specific_rain_water_content` | `crwc` | Mass of rain water per unit mass of moist air. | kg kg-1 |
| `specific_snow_water_content` | `cswc` | Mass of snow per unit mass of moist air. | kg kg-1 |
