"""What is an API? (Climate-data flavour, with the CDS as the worked example.)"""

from __future__ import annotations

import streamlit as st


def render_page() -> None:
    st.title("What is an API?")
    st.caption(
        "From 'I have heard the term' to 'I can read the code that calls one' "
        "in about five minutes."
    )

    st.header("API in one paragraph")
    st.markdown(
        "**API** stands for *Application Programming Interface*. In plain "
        "English: it's a contract between two pieces of software. You send "
        "a request in a specific shape, the server promises to send a "
        "response in a specific shape. For climate data, the API is how "
        "your laptop asks the Copernicus server (sitting in a data centre "
        "in Europe) for a slice of ERA5, and how it gets back a NetCDF "
        "file."
    )

    st.header("What an API call actually looks like")
    st.markdown(
        "Here's a real call to the **Copernicus Climate Data Store (CDS)** "
        "asking for one hour of 2-metre temperature over the UK on "
        "1 July 2023. This is the same call the **Build a notebook** mode "
        "in this app generates for you."
    )
    st.code(
        "import cdsapi\n\n"
        "client = cdsapi.Client()  # reads ~/.cdsapirc for your key\n\n"
        'client.retrieve(\n'
        '    "reanalysis-era5-single-levels",\n'
        '    {\n'
        '        "product_type": ["reanalysis"],\n'
        '        "variable": ["2m_temperature"],\n'
        '        "year": ["2023"],\n'
        '        "month": ["07"],\n'
        '        "day": ["01"],\n'
        '        "time": ["12:00"],\n'
        '        "data_format": "netcdf",\n'
        '        "area": [55, -8, 49, 2],  # north, west, south, east\n'
        "    },\n"
        ').download("era5_uk_1july2023.nc")',
        language="python",
    )
    st.markdown(
        "Three things are happening:\n"
        "1. **Authentication.** `cdsapi.Client()` reads a small file at "
        "`~/.cdsapirc` containing your personal access token. The CDS uses "
        "that to know it's you (and to enforce your rate limits).\n"
        "2. **The request.** You hand over a dictionary of parameters - "
        "what dataset, what variable, what dates, what region.\n"
        "3. **The response.** `.download(...)` blocks until the CDS has "
        "queued and processed your request, then writes the result to disk "
        "as a NetCDF file."
    )

    st.divider()

    st.header("Why APIs need a key")
    st.markdown(
        "Climate data servers cost real money to run. Free public access "
        "with a personal key lets the server:\n"
        "- check that you've accepted the dataset's licence;\n"
        "- prevent one user from hammering the queue and starving everyone "
        "else;\n"
        "- contact you if there's a service issue."
    )
    st.markdown(
        "**Your key is a password. Never paste it into an email, a public "
        "GitHub repo, or a chat.** Save it once to the file the API client "
        "expects (`~/.cdsapirc`, `~/.netrc`, etc.) and let the client read "
        "it from there."
    )

    st.divider()

    st.header("Setting up a CDS key (the most common case)")
    st.markdown(
        "1. Register at https://cds.climate.copernicus.eu/. Free, no card.\n"
        "2. Sign in. Visit the *How to API* page: "
        "https://cds.climate.copernicus.eu/how-to-api\n"
        "3. Copy the two-line `url:` / `key:` block it shows you.\n"
        "4. Save it to your home directory as `.cdsapirc`:\n"
        "   - macOS / Linux: `~/.cdsapirc`\n"
        "   - Windows: `C:\\Users\\YOU\\.cdsapirc`\n"
        "5. Accept the licence on the dataset page (e.g. ERA5 single levels). "
        "**Do this once per dataset family.**\n"
        "6. Run any `cdsapi`-based script."
    )
    st.success(
        "If a script gives you a `403` or 'licence not accepted' error, "
        "it's almost always because step 5 was skipped for that specific "
        "dataset. Open the dataset page on the CDS site, scroll down, and "
        "tick the licence box."
    )

    st.divider()

    st.header("APIs that don't need a key")
    st.markdown(
        "Some datasets are open over plain HTTP - no registration, no key. "
        "This app will run those live. Examples:\n"
        "- **HadCET** (Met Office central England temperature, 1659-present)\n"
        "- **HadCRUT5** (global temperature anomalies, 1850-present)\n"
        "- **CHIRPS** (satellite rainfall, tropics)\n"
        "- **ECMWF Open Data** (real-time forecast fields)\n"
        "- **ARCO-ERA5** (cloud-native ERA5 on Google Cloud)\n"
        "- **ESGF CMIP6** (the full CMIP6 archive)\n\n"
        "If you're learning APIs and want to see one work end-to-end "
        "without any setup, start with one of these in the **Build a "
        "notebook** mode."
    )

    st.divider()

    st.header("Where to go next")
    st.markdown(
        "- Mozilla's plain-English intro to APIs: "
        "https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction\n"
        "- CDS How-to-API: https://cds.climate.copernicus.eu/how-to-api\n"
        "- Earth Data Hub: https://earthdatahub.destine.eu/\n"
        "- Try the **Build a notebook** mode here with HadCET first - "
        "it works without any key, so you can see a complete API-driven "
        "workflow before setting up credentials."
    )
