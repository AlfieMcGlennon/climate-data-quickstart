"""Recipe: England's longest temperature record.

Uses HadCET (open access, no credentials, instant download) to show
350+ years of monthly temperature data with rolling-mean trend and
seasonal cycle analysis.
"""

from __future__ import annotations

import streamlit as st

TITLE = "How has England's temperature changed since 1659?"
DESCRIPTION = (
    "Plot 350+ years of the world's longest instrumental temperature "
    "record and see the warming trend emerge."
)
DATASETS_USED = ["HadCET"]
CREDENTIALS = "None"
ESTIMATED_TIME = "Instant"


def _build_trend_code(start_year: int, window: int) -> str:
    return (
        "import requests\n"
        "import io\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "\n"
        "# Download HadCET monthly mean temperatures\n"
        'url = "https://hadleyserver.metoffice.gov.uk/hadcet/data/meantemp_monthly_totals.txt"\n'
        "resp = requests.get(url, timeout=30)\n"
        "resp.raise_for_status()\n"
        "\n"
        "# Parse the fixed-width file: year + 12 months + annual mean\n"
        "lines = resp.text.splitlines()\n"
        "cols = ['year', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',\n"
        "        'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'ann']\n"
        "\n"
        "# Skip header lines (find first line starting with a 4-digit year\n"
        "# followed by 13 numeric columns)\n"
        "data_start = 0\n"
        "for i, line in enumerate(lines):\n"
        "    tokens = line.strip().split()\n"
        "    if len(tokens) >= 14 and tokens[0][:4].isdigit():\n"
        "        try:\n"
        "            [float(t) for t in tokens[:14]]\n"
        "            data_start = i\n"
        "            break\n"
        "        except ValueError:\n"
        "            continue\n"
        "\n"
        "df = pd.read_csv(\n"
        '    io.StringIO("\\n".join(lines[data_start:])),\n'
        '    sep=r"\\s+", header=None, names=cols, engine="python",\n'
        ")\n"
        "\n"
        "# Reshape to long format\n"
        "months = {m: i+1 for i, m in enumerate(cols[1:13])}\n"
        "long = df.drop(columns=['ann']).melt(\n"
        "    id_vars='year', var_name='month_name', value_name='temp'\n"
        ")\n"
        "long['month'] = long['month_name'].map(months)\n"
        "long = long[long['temp'] > -99].sort_values(['year', 'month'])\n"
        "\n"
        f"# Filter to start year\n"
        f"long = long[long['year'] >= {start_year}]\n"
        "\n"
        "# Plot with rolling mean\n"
        "fig, ax = plt.subplots(figsize=(12, 5))\n"
        "ax.plot(range(len(long)), long['temp'].values,\n"
        "        linewidth=0.3, alpha=0.3, color='steelblue', label='Monthly')\n"
        f"rolling = long['temp'].rolling({window}, center=True).mean()\n"
        "ax.plot(range(len(long)), rolling.values,\n"
        f"        linewidth=2, color='firebrick', label='{window}-month rolling mean')\n"
        "ax.set_ylabel('Temperature (deg C)')\n"
        f"ax.set_title('Central England Temperature, {start_year}-present')\n"
        "ax.legend()\n"
        "ax.grid(alpha=0.3)\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
    )


def _build_seasonal_code(start_year: int) -> str:
    return (
        "# Seasonal cycle: compare early period vs recent\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "\n"
        "# (assumes 'long' DataFrame from the code above)\n"
        f"early = long[(long['year'] >= {start_year}) & (long['year'] < {start_year + 50})]\n"
        f"recent = long[long['year'] >= {max(start_year, 1975)}]\n"
        "\n"
        "early_cycle = early.groupby('month')['temp'].mean()\n"
        "recent_cycle = recent.groupby('month')['temp'].mean()\n"
        "\n"
        "month_labels = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(8, 4))\n"
        "ax.plot(range(1, 13), early_cycle.values, 'o-',\n"
        f"        label='{start_year}-{start_year + 49}', color='steelblue')\n"
        "ax.plot(range(1, 13), recent_cycle.values, 's-',\n"
        f"        label='{max(start_year, 1975)}-present', color='firebrick')\n"
        "ax.set_xticks(range(1, 13))\n"
        "ax.set_xticklabels(month_labels)\n"
        "ax.set_ylabel('Temperature (deg C)')\n"
        "ax.set_title('Seasonal cycle: early vs recent')\n"
        "ax.legend()\n"
        "ax.grid(alpha=0.3)\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
    )


@st.cache_data(ttl=3600, show_spinner="Downloading HadCET data...")
def _load_hadcet():
    """Download and parse HadCET monthly mean data."""
    import io

    import numpy as np
    import pandas as pd
    import requests

    url = "https://hadleyserver.metoffice.gov.uk/hadcet/data/meantemp_monthly_totals.txt"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    lines = resp.text.splitlines()
    cols = [
        "year", "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec", "ann",
    ]

    data_start = 0
    for i, line in enumerate(lines):
        tokens = line.strip().split()
        if len(tokens) >= 14 and tokens[0][:4].isdigit():
            try:
                [float(t) for t in tokens[:14]]
                data_start = i
                break
            except ValueError:
                continue

    df = pd.read_csv(
        io.StringIO("\n".join(lines[data_start:])),
        sep=r"\s+", header=None, names=cols, engine="python",
    )
    months = {m: i + 1 for i, m in enumerate(cols[1:13])}
    long = df.drop(columns=["ann"]).melt(
        id_vars="year", var_name="month_name", value_name="temp",
    )
    long["month"] = long["month_name"].map(months)
    long = long[long["temp"] > -99].sort_values(["year", "month"]).reset_index(drop=True)
    return long


def render_recipe() -> None:
    """Render the HadCET record recipe."""
    st.header("How has England's temperature changed since 1659?")
    st.markdown(
        "HadCET is the longest instrumental temperature record in the world, "
        "maintained by the Met Office. It covers Central England (roughly the "
        "triangle bounded by Lancashire, London, and Bristol) with monthly "
        "values from 1659 and daily values from 1772."
    )
    st.markdown(
        "This recipe downloads the monthly mean series, plots it with a "
        "rolling mean to reveal the long-term trend, and compares the "
        "seasonal cycle between an early period and recent decades."
    )

    st.caption(
        ":material/download: Open access, no credentials needed. "
        "Data source: Met Office Hadley Centre."
    )

    # Widgets
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.slider(
            "Start year", 1659, 2000, 1659, key="hadcet_start",
        )
    with col2:
        window = st.slider(
            "Rolling mean window (months)",
            12, 600, 120, step=12, key="hadcet_window",
            help="120 months = 10 years. Larger windows show smoother trends.",
        )

    # Load data
    long = _load_hadcet()
    subset = long[long["year"] >= start_year].copy()

    if subset.empty:
        st.warning("No data for the selected range.")
        return

    # Trend plot
    import matplotlib.pyplot as plt

    st.subheader("Long-term trend")
    st.markdown(
        f"Monthly temperatures from {start_year} to present, with a "
        f"{window}-month ({window // 12}-year) rolling mean. The raw data "
        f"shows strong seasonality; the rolling mean reveals the underlying "
        f"warming trend."
    )

    rolling = subset["temp"].rolling(window, center=True).mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        range(len(subset)), subset["temp"].values,
        linewidth=0.3, alpha=0.3, color="steelblue", label="Monthly",
    )
    ax.plot(
        range(len(subset)), rolling.values,
        linewidth=2, color="firebrick",
        label=f"{window}-month rolling mean",
    )
    ax.set_ylabel("Temperature (deg C)")
    ax.set_title(f"Central England Temperature, {start_year}-present")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)

    with st.expander(":material/code: Code for this plot"):
        st.code(_build_trend_code(start_year, window), language="python")

    # Seasonal cycle comparison
    st.subheader("Seasonal cycle: early vs recent")
    early_end = start_year + 50
    recent_start = max(start_year, 1975)
    st.markdown(
        f"The average monthly temperature for {start_year}-{early_end - 1} "
        f"compared with {recent_start}-present. The shape stays similar "
        f"(cold winters, warm summers) but the whole curve has shifted upward."
    )

    early = subset[(subset["year"] >= start_year) & (subset["year"] < early_end)]
    recent = subset[subset["year"] >= recent_start]

    if early.empty or recent.empty:
        st.info("Not enough data to compare periods. Try an earlier start year.")
        return

    early_cycle = early.groupby("month")["temp"].mean()
    recent_cycle = recent.groupby("month")["temp"].mean()

    month_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(
        range(1, 13), early_cycle.values, "o-",
        label=f"{start_year}-{early_end - 1}", color="steelblue",
    )
    ax2.plot(
        range(1, 13), recent_cycle.values, "s-",
        label=f"{recent_start}-present", color="firebrick",
    )
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(month_labels)
    ax2.set_ylabel("Temperature (deg C)")
    ax2.set_title("Seasonal cycle: early vs recent")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    st.pyplot(fig2)

    warming = recent_cycle.mean() - early_cycle.mean()
    st.caption(
        f"The mean annual temperature has risen by approximately "
        f"**{warming:.1f} deg C** between the two periods."
    )

    with st.expander(":material/code: Code for this plot"):
        st.code(_build_seasonal_code(start_year), language="python")

    # Key stats
    st.subheader("At a glance")
    col_a, col_b, col_c, col_d = st.columns(4)
    all_temps = subset["temp"]
    col_a.metric("Records span", f"{int(subset['year'].min())}-{int(subset['year'].max())}", border=True)
    col_b.metric("Data points", f"{len(subset):,}", border=True)
    col_c.metric("Coldest month", f"{all_temps.min():.1f} deg C", border=True)
    col_d.metric("Warmest month", f"{all_temps.max():.1f} deg C", border=True)

    # Get this data yourself
    st.markdown("---")
    st.subheader("Get this data yourself")
    st.markdown(
        "Everything above uses real data from the Met Office, downloaded "
        "live. No API key, no registration, no queue. Copy the code below "
        "to pull the same data in your own Python environment."
    )

    with st.expander(":material/download: Download code", expanded=False):
        st.code(
            "import requests\n"
            "\n"
            "# HadCET monthly mean temperatures (open access, Met Office)\n"
            "url = 'https://hadleyserver.metoffice.gov.uk/hadcet/data/meantemp_monthly_totals.txt'\n"
            "resp = requests.get(url, timeout=30)\n"
            "resp.raise_for_status()\n"
            "\n"
            "# Save to file\n"
            "with open('hadcet_monthly_mean.txt', 'w') as f:\n"
            "    f.write(resp.text)\n"
            "print('Downloaded HadCET monthly mean temperatures')\n"
            "\n"
            "# Other options:\n"
            "# Daily mean:  .../meantemp_daily_totals.txt\n"
            "# Monthly max: .../maxtemp_monthly_totals.txt\n"
            "# Monthly min: .../mintemp_monthly_totals.txt\n"
            "# Daily max:   .../maxtemp_daily_totals.txt\n"
            "# Daily min:   .../mintemp_daily_totals.txt\n",
            language="python",
        )

    with st.expander(":material/folder_open: Open and inspect", expanded=False):
        st.code(
            "import io\n"
            "import pandas as pd\n"
            "\n"
            "# Parse the fixed-width text file into a DataFrame\n"
            "lines = open('hadcet_monthly_mean.txt').read().splitlines()\n"
            "cols = ['year', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',\n"
            "        'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'ann']\n"
            "\n"
            "# Skip header lines\n"
            "data_start = 0\n"
            "for i, line in enumerate(lines):\n"
            "    tokens = line.strip().split()\n"
            "    if len(tokens) >= 14 and tokens[0][:4].isdigit():\n"
            "        try:\n"
            "            [float(t) for t in tokens[:14]]\n"
            "            data_start = i\n"
            "            break\n"
            "        except ValueError:\n"
            "            continue\n"
            "\n"
            "df = pd.read_csv(\n"
            "    io.StringIO('\\n'.join(lines[data_start:])),\n"
            "    sep=r'\\s+', header=None, names=cols, engine='python',\n"
            ")\n"
            "\n"
            "# Filter missing values (-99.9)\n"
            "print(df.head())\n"
            "print(f'\\n{len(df)} years of data, {df[\"year\"].min()}-{df[\"year\"].max()}')\n",
            language="python",
        )

    st.caption(
        "No dependencies beyond `requests` and `pandas`. "
        "Works in any Python 3.10+ environment, Colab, or Jupyter."
    )

    # Next steps
    st.markdown("---")
    st.subheader("Next steps")
    st.markdown(
        "- See the full dataset documentation in `docs/hadcet/README.md`\n"
        "- Try the daily resolution for finer detail (available from 1772)\n"
        "- Compare with HadCRUT5 to see if England's trend matches the global average\n"
        "- Use the Download tab to pull HadCET data for your own analysis"
    )
