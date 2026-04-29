"""What is Python? What is a Jupyter notebook?"""

from __future__ import annotations

import streamlit as st


def render_page() -> None:
    st.title("What are Python and Jupyter?")
    st.caption(
        "Plain-English answers for anyone who's about to download a .ipynb "
        "from this app and isn't sure what to do with it."
    )

    st.header("Python in one paragraph")
    st.markdown(
        "**Python** is a programming language. You write instructions in a "
        "text file ending in `.py`, and the Python *interpreter* on your "
        "computer reads those instructions and does what they say. The "
        "climate datasets in this app are accessed using small Python "
        "scripts that talk to remote servers (the API call), download a "
        "file, and let you analyse it."
    )
    st.markdown(
        "You install Python once. After that you can run any `.py` file "
        "or any `.ipynb` notebook on your machine."
    )

    st.header("Install Python")
    st.markdown(
        "Pick the route for your operating system. The official installer "
        "from python.org is the simplest first step."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Windows")
        st.markdown(
            "1. Go to https://www.python.org/downloads/windows/\n"
            "2. Download the latest Python 3.x installer.\n"
            "3. Run it. **Tick \"Add Python to PATH\"** before clicking Install.\n"
            "4. Open Command Prompt and type `python --version` to check."
        )
    with c2:
        st.subheader("macOS")
        st.markdown(
            "1. Open Terminal.\n"
            "2. Install Homebrew if you do not have it:\n"
            "   `/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"`\n"
            "3. `brew install python`\n"
            "4. `python3 --version` to check."
        )
    with c3:
        st.subheader("Linux")
        st.markdown(
            "Most distributions ship with Python 3 already.\n\n"
            "On Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`.\n\n"
            "On Fedora: `sudo dnf install python3 python3-pip`."
        )

    st.divider()

    st.header("Jupyter in one paragraph")
    st.markdown(
        "**Jupyter** is a way to write and run Python in *blocks* (called "
        "cells) inside your web browser. A Jupyter file ends in `.ipynb` "
        "(short for **i**nteractive **py**thon **n**ote**b**ook). Each cell "
        "can be a chunk of code or a chunk of explanatory text. You run the "
        "code cells one at a time and immediately see the output - any "
        "numbers, tables, or plots - right beneath the cell."
    )
    st.markdown(
        "This is the format the **Build a notebook** mode in this app "
        "produces. You pick a dataset and the plots you want; the app gives "
        "you a `.ipynb` file. You then open that file in Jupyter on your "
        "own machine to run, edit, and learn from it."
    )

    st.header("Open a notebook in 4 steps")
    st.markdown(
        "Once Python is installed:\n"
        "1. Open Terminal (macOS/Linux) or Command Prompt (Windows).\n"
        "2. Install Jupyter: `pip install jupyter`\n"
        "3. Move into the folder that contains your downloaded `.ipynb`:\n"
        "   `cd path/to/your/folder`\n"
        "4. Run `jupyter notebook`. Your browser opens; click the `.ipynb` "
        "to start it."
    )

    st.info(
        "**Tip - try Google Colab first.** If you don't want to install "
        "anything yet, head to https://colab.research.google.com/, click "
        "*File > Upload notebook*, and drop in the `.ipynb` you downloaded "
        "from this app. Colab runs Python in the cloud - no local install. "
        "Most cells will work directly. Cells that need a Copernicus key "
        "(CDS) won't run on Colab unless you set up your key there too."
    )

    st.divider()

    st.header("How a notebook looks once it runs")
    st.markdown(
        "Below is roughly what one cell looks like in Jupyter or Colab. "
        "On the left is the code; on the right is the output that appears "
        "after you click *Run*."
    )
    st.code(
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n\n"
        'df = pd.read_csv("hadcet_monthly_mean.csv")\n'
        'df["temperature_degC"].rolling(120, center=True).mean().plot()\n'
        "plt.title(\"Central England Temperature, 10-year rolling mean\")\n"
        "plt.show()",
        language="python",
    )
    st.caption(
        "If you ran this in Jupyter you would see a line plot appear "
        "directly under the cell. No console, no separate window."
    )

    st.divider()

    st.header("Where to go next")
    st.markdown(
        "- Real Python's getting-started page: https://realpython.com/installing-python/\n"
        "- Jupyter project's official intro: https://docs.jupyter.org/en/latest/start/index.html\n"
        "- Software Carpentry's Python lessons: https://swcarpentry.github.io/python-novice-inflammation/\n"
        "- Then come back to **Build a notebook** in this app."
    )
