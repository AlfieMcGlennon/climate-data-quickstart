"""Earth Data Hub form.

EDH is a streaming platform, not a queued download service like the CDS.
The primary output here is a code snippet the user can copy and run in
their own notebook to work with the data lazily; an optional "download
to NetCDF" materialises the sliced bytes locally if they actually want a
file.
"""

from __future__ import annotations

import streamlit as st

from app.forms import bbox_input, output_dir_input

SLUG = "earth-data-hub"

# EDH ERA5 Zarr stores expose variables by their GRIB short name, not
# by the CDS API snake_case name. Map friendly labels to the short name.
EDH_ERA5_VARIABLES = {
    "2m temperature (t2m)": "t2m",
    "2m dewpoint temperature (d2m)": "d2m",
    "10m u-wind (u10)": "u10",
    "10m v-wind (v10)": "v10",
    "100m u-wind (u100)": "u100",
    "100m v-wind (v100)": "v100",
    "Mean sea level pressure (msl)": "msl",
    "Surface pressure (sp)": "sp",
    "Sea surface temperature (sst)": "sst",
    "Total cloud cover (tcc)": "tcc",
    "Total precipitation (tp)": "tp",
    "Surface solar radiation downwards (ssrd)": "ssrd",
    "Custom (type short name below)": None,
}

EDH_DATASETS = {
    "ERA5 single levels (1940-present)": (
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-single-levels-v0.zarr",
        EDH_ERA5_VARIABLES,
    ),
    "ERA5-Land (1950-present)": (
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-land-v0.zarr",
        EDH_ERA5_VARIABLES,
    ),
    "ERA5 single levels monthly means": (
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-single-levels-monthly-means-v0.zarr",
        EDH_ERA5_VARIABLES,
    ),
}


def render_form() -> dict:
    st.markdown(
        "Stream climate data from Earth Data Hub via xarray + Zarr. "
        "Same underlying ERA5 data as the CDS entries above, but accessed "
        "**lazily** rather than downloaded as a whole file. "
        "[Full docs](docs/earth-data-hub/README.md)."
    )
    st.info(
        "EDH is a streaming service, not a queued download service. When you "
        "open the store, only the coordinate metadata travels over the wire. "
        "Bytes are fetched only when you reduce, plot, or save the slice."
    )

    dataset_label = st.selectbox("EDH dataset", list(EDH_DATASETS.keys()))
    default_url, variable_map = EDH_DATASETS[dataset_label]

    edh_dataset_url = st.text_input("Zarr URL", default_url)

    var_label = st.selectbox("Variable", list(variable_map.keys()))
    variable = variable_map[var_label]
    if variable is None:
        variable = st.text_input(
            "Variable short name",
            "t2m",
            help="Use the GRIB short name (what appears in the opened xarray Dataset).",
        )

    c1, c2 = st.columns(2)
    time_start = c1.text_input("Start (ISO)", "2023-07-01T00:00")
    time_end = c2.text_input("End (ISO)", "2023-07-01T23:00")

    bbox = bbox_input(default_preset="UK (55, -8, 49, 2)")
    output_dir, output_filename = output_dir_input(SLUG)

    return {
        "edh_dataset_url": edh_dataset_url,
        "variable": variable,
        "time_start": time_start,
        "time_end": time_end,
        "lat_north": bbox.north,
        "lat_south": bbox.south,
        "lon_west": bbox.west,
        "lon_east": bbox.east,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }


def streaming_snippet(config: dict) -> str:
    """Return the copy-pasteable code block a user can run to stream this slice."""
    return f'''\
import xarray as xr

# Open the Zarr store lazily. Only coordinate metadata is fetched here.
# storage_options with trust_env=True lets aiohttp read your
# ~/.netrc (or ~/_netrc on Windows) entry for data.earthdatahub.destine.eu.
ds = xr.open_dataset(
    "{config["edh_dataset_url"]}",
    engine="zarr",
    chunks={{}},
    storage_options={{"client_kwargs": {{"trust_env": True}}}},
)

# Normalise longitude to -180..180 if the store uses 0..360, then
# sortby so .sel slices work regardless of axis direction.
if float(ds["longitude"].max()) > 180:
    ds = ds.assign_coords(longitude=(((ds["longitude"] + 180) % 360) - 180))
ds = ds.sortby("latitude").sortby("longitude")

# Lazy slice: defines the byte-ranges that will be fetched later.
# No network traffic happens on this line.
# EDH ERA5 stores use 'valid_time'; older ones used 'time'.
time_dim = "valid_time" if "valid_time" in ds.sizes else "time"
indexers = {{
    time_dim: slice("{config["time_start"]}", "{config["time_end"]}"),
    "latitude": slice({config["lat_south"]}, {config["lat_north"]}),
    "longitude": slice({config["lon_west"]}, {config["lon_east"]}),
}}
subset = ds["{config["variable"]}"].sel(indexers)

# Work with subset lazily:
#   subset.mean("latitude").plot()       # time series of area-mean, fetches on plot
#   mean = subset.mean("latitude").mean("longitude").load()   # materialise a small array
#   subset.to_netcdf("era5_slice.nc")    # materialise and save if you do want a file
print(subset)
'''
