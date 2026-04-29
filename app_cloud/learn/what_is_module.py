"""What is a module / pip install?"""

from __future__ import annotations

import streamlit as st


def render_page() -> None:
    st.title("What is a module / pip install?")
    st.caption(
        "Why every climate data script starts with a list of `import` "
        "statements, and what you have to do once before they work."
    )

    st.header("Modules in one paragraph")
    st.markdown(
        "A **module** (also called a **package** or **library**) is a chunk "
        "of Python code somebody else wrote that does something useful. "
        "Rather than reinventing the wheel - writing your own HTTP client, "
        "your own NetCDF parser, your own plotting library - you `import` "
        "their work into your own script. Climate data work uses a small "
        "set of modules over and over again."
    )

    st.header("The five you'll see most often")
    st.markdown(
        "| Module | What it does | Docs |\n"
        "| --- | --- | --- |\n"
        "| `xarray` | Loads multi-dimensional gridded data (NetCDF, GRIB, Zarr) and lets you slice it like a fancy spreadsheet. | https://docs.xarray.dev/ |\n"
        "| `pandas` | The same idea but for flat tables - rows and columns, like a CSV. | https://pandas.pydata.org/docs/ |\n"
        "| `numpy` | The numerical engine underneath both of the above. Fast arrays, basic maths. | https://numpy.org/doc/ |\n"
        "| `matplotlib` | Plotting. Every static line plot, map, or histogram in the climate world is one of these. | https://matplotlib.org/stable/ |\n"
        "| `cdsapi` | The Copernicus CDS API client. Turns a Python dict into an ERA5 / CMIP6 / E-OBS request. | https://cds.climate.copernicus.eu/how-to-api |"
    )

    st.space("medium")

    st.header("`pip install`: the one-time setup")
    st.markdown(
        "Modules don't ship with Python. The first time you want to use "
        "one, you install it with `pip` (Python's package manager) from "
        "the terminal:"
    )
    st.code(
        "pip install xarray pandas numpy matplotlib cdsapi netcdf4",
        language="bash",
    )
    st.markdown(
        "After that, every script that says `import xarray as xr` will "
        "find it. You don't need to install it again unless you move to a "
        "new computer or a new virtual environment."
    )

    st.info(
        "**Tip - virtual environments.** A virtual environment is a "
        "throwaway sandbox for one project. It keeps the modules you "
        "install for *this* project from interfering with anything else. "
        "Create one once per project:\n\n"
        "```\n"
        "python -m venv .venv\n"
        "# activate (macOS/Linux):\n"
        "source .venv/bin/activate\n"
        "# activate (Windows):\n"
        "  .venv\\Scripts\\activate\n"
        "```\n\n"
        "Then run `pip install ...` inside the activated environment.",
        icon=":material/lightbulb:",
    )

    st.space("medium")

    st.header("`import` in your script")
    st.markdown(
        "At the top of any Python file or notebook cell you'll see lines "
        "like this:"
    )
    st.code(
        "import xarray as xr\n"
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        'from pathlib import Path',
        language="python",
    )
    st.markdown(
        "These pull the modules into your script under short aliases "
        "(`xr`, `pd`, `plt`, `np`) by convention. After that, you call "
        "their functions through the alias:"
    )
    st.code(
        'ds = xr.open_dataset("era5_july_2023.nc")\n'
        'df = pd.read_csv("hadcet_monthly_mean.csv")\n'
        'plt.plot([1, 2, 3])',
        language="python",
    )

    st.space("medium")

    st.header("If a notebook fails on the first cell")
    st.markdown(
        "The most common error a learner hits is:"
    )
    st.code('ModuleNotFoundError: No module named "xarray"', language="text")
    st.markdown(
        "It means the module isn't installed in the Python environment "
        "you're running. Fix it with `pip install xarray` (or whichever "
        "module is missing). If you're in Jupyter, you can do it from a "
        "cell by running `!pip install xarray` (the leading `!` runs the "
        "command in your terminal, not in Python)."
    )

    st.space("medium")

    st.header("Where to go next")
    st.markdown(
        "- Python Packaging User Guide: https://packaging.python.org/\n"
        "- Real Python on virtual environments: https://realpython.com/python-virtual-environments-a-primer/\n"
        "- Pip docs: https://pip.pypa.io/en/stable/"
    )
