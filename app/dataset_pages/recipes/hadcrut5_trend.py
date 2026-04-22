"""Recipe: Global warming trend from HadCRUT5.

Uses HadCRUT5 global summary series (open access, no credentials,
small download) to show the global temperature anomaly trend from 1850.
"""

from __future__ import annotations

import streamlit as st

TITLE = "How much has the world warmed since 1850?"
DESCRIPTION = (
    "Plot the global temperature anomaly from 1850 to present using "
    "HadCRUT5, the standard reference for long-term warming."
)
DATASETS_USED = ["HadCRUT5"]
CREDENTIALS = "None"
ESTIMATED_TIME = "Instant"


def _build_trend_code(window: int, baseline_start: int, baseline_end: int) -> str:
    return (
        "import requests\n"
        "import xarray as xr\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "from pathlib import Path\n"
        "\n"
        "# Download HadCRUT5 global monthly summary series (~200 KB)\n"
        'url = (\n'
        '    "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/"\n'
        '    "HadCRUT.5.1.0.0/analysis/diagnostics/"\n'
        '    "HadCRUT.5.1.0.0.analysis.summary_series.global.monthly.nc"\n'
        ')\n'
        'out = Path("data/hadcrut5/hadcrut5_global_monthly.nc")\n'
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "\n"
        "with requests.get(url, stream=True, timeout=120) as r:\n"
        "    r.raise_for_status()\n"
        "    with open(out, 'wb') as f:\n"
        "        for chunk in r.iter_content(chunk_size=1 << 20):\n"
        "            f.write(chunk)\n"
        "\n"
        "ds = xr.open_dataset(out)\n"
        "# The main variable is tas_mean (temperature anomaly)\n"
        "da = ds['tas_mean'].squeeze()\n"
        "\n"
        f"# Re-baseline to {baseline_start}-{baseline_end}\n"
        f'baseline = da.sel(time=slice("{baseline_start}", "{baseline_end}")).mean()\n'
        "da = da - baseline\n"
        "\n"
        "# Annual means\n"
        'annual = da.resample(time="YE").mean()\n'
        "years = [t.dt.year.item() for t in annual.time]\n"
        "\n"
        "# Rolling mean\n"
        f"rolling = annual.rolling(time={window}, center=True).mean()\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(12, 5))\n"
        "colours = ['steelblue' if v < 0 else 'firebrick' for v in annual.values]\n"
        "ax.bar(years, annual.values, color=colours, width=0.8, alpha=0.7)\n"
        "ax.plot(years, rolling.values, color='black', linewidth=2,\n"
        f"        label='{window}-year rolling mean')\n"
        "ax.axhline(0, color='gray', linewidth=0.5)\n"
        f"ax.set_ylabel('Temperature anomaly (deg C, vs {baseline_start}-{baseline_end})')\n"
        "ax.set_title('Global temperature anomaly (HadCRUT5)')\n"
        "ax.legend()\n"
        "ax.grid(alpha=0.3, axis='y')\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
    )


def _build_stripes_code(baseline_start: int, baseline_end: int) -> str:
    return (
        "# Warming stripes (inspired by Ed Hawkins' #ShowYourStripes)\n"
        "import requests\n"
        "import xarray as xr\n"
        "import matplotlib.pyplot as plt\n"
        "from pathlib import Path\n"
        "\n"
        "# Download HadCRUT5 global monthly summary series\n"
        'url = (\n'
        '    "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/"\n'
        '    "HadCRUT.5.1.0.0/analysis/diagnostics/"\n'
        '    "HadCRUT.5.1.0.0.analysis.summary_series.global.monthly.nc"\n'
        ')\n'
        'out = Path("data/hadcrut5/hadcrut5_global_monthly.nc")\n'
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "\n"
        "with requests.get(url, stream=True, timeout=120) as r:\n"
        "    r.raise_for_status()\n"
        "    with open(out, 'wb') as f:\n"
        "        for chunk in r.iter_content(chunk_size=1 << 20):\n"
        "            f.write(chunk)\n"
        "\n"
        "ds = xr.open_dataset(out)\n"
        "da = ds['tas_mean'].squeeze()\n"
        "\n"
        f"# Re-baseline to {baseline_start}-{baseline_end}\n"
        f'baseline = da.sel(time=slice("{baseline_start}", "{baseline_end}")).mean()\n'
        "da = da - baseline\n"
        "\n"
        '# Annual means\n'
        'annual = da.resample(time="YE").mean()\n'
        "years = [t.dt.year.item() for t in annual.time]\n"
        "\n"
        "# Plot warming stripes\n"
        "fig, ax = plt.subplots(figsize=(12, 2.5))\n"
        "norm = plt.Normalize(vmin=float(annual.min()), vmax=float(annual.max()))\n"
        "cmap = plt.cm.RdBu_r\n"
        "for yr, val in zip(years, annual.values):\n"
        "    ax.axvspan(yr - 0.5, yr + 0.5, color=cmap(norm(val)))\n"
        "ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)\n"
        "ax.set_yticks([])\n"
        "ax.set_title('Warming stripes (HadCRUT5)')\n"
        "ax.set_xlabel('Year')\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
    )


def _build_decade_code(baseline_start: int, baseline_end: int) -> str:
    return (
        "# Decadal averages\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "\n"
        "# (assumes 'da' from the code above, re-baselined)\n"
        'annual = da.resample(time="YE").mean()\n'
        "years = np.array([t.dt.year.item() for t in annual.time])\n"
        "decades = (years // 10) * 10\n"
        "\n"
        "import pandas as pd\n"
        "decade_df = pd.DataFrame({'year': years, 'decade': decades, 'anomaly': annual.values})\n"
        "decade_mean = decade_df.groupby('decade')['anomaly'].mean()\n"
        "\n"
        "colours = ['steelblue' if v < 0 else 'firebrick' for v in decade_mean.values]\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(10, 4))\n"
        "ax.bar(decade_mean.index, decade_mean.values, width=8, color=colours, alpha=0.8)\n"
        "ax.axhline(0, color='gray', linewidth=0.5)\n"
        f"ax.set_ylabel('Temperature anomaly (deg C, vs {baseline_start}-{baseline_end})')\n"
        "ax.set_title('Decadal average temperature anomaly')\n"
        "ax.grid(alpha=0.3, axis='y')\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
    )


@st.cache_data(ttl=3600, show_spinner="Downloading HadCRUT5 data...")
def _load_hadcrut5():
    """Download HadCRUT5 global monthly summary series."""
    from pathlib import Path

    import requests
    import xarray as xr

    url = (
        "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/"
        "HadCRUT.5.1.0.0/analysis/diagnostics/"
        "HadCRUT.5.1.0.0.analysis.summary_series.global.monthly.nc"
    )
    out = Path("data/hadcrut5/hadcrut5_global_monthly.nc")
    out.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)

    return xr.open_dataset(out)


def render_recipe() -> None:
    """Render the HadCRUT5 global warming trend recipe."""
    st.header("How much has the world warmed since 1850?")
    st.markdown(
        "HadCRUT5 is a global temperature dataset produced jointly by the "
        "Met Office Hadley Centre and the Climatic Research Unit at the "
        "University of East Anglia. It combines land surface temperature "
        "observations with sea surface temperature measurements, gridded "
        "onto a 5-degree grid from 1850 to present."
    )
    st.markdown(
        "This recipe downloads the global monthly summary series (a single "
        "time series of global mean anomaly, about 200 KB), re-baselines it "
        "to a reference period of your choice, and plots the annual warming "
        "trend with a warming stripes visualisation."
    )

    st.caption(
        ":material/download: Open access, no credentials needed. "
        "Data source: Met Office Hadley Centre / CRU."
    )

    # Widgets
    col1, col2, col3 = st.columns(3)
    with col1:
        window = st.slider(
            "Rolling mean window (years)",
            5, 30, 10, key="hadcrut5_window",
        )
    with col2:
        baseline_start = st.number_input(
            "Baseline start", 1850, 2000, 1961, key="hadcrut5_bl_start",
            help="Anomalies are relative to this period's mean.",
        )
    with col3:
        baseline_end = st.number_input(
            "Baseline end", 1860, 2020, 1990, key="hadcrut5_bl_end",
            help="Anomalies are relative to this period's mean.",
        )

    if baseline_end <= baseline_start:
        st.error("Baseline end must be after baseline start.")
        return

    # Load data
    ds = _load_hadcrut5()
    da = ds["tas_mean"].squeeze()

    # Re-baseline
    baseline = da.sel(time=slice(str(baseline_start), str(baseline_end))).mean()
    da = da - baseline

    # Annual means
    annual = da.resample(time="YE").mean()
    years = [t.dt.year.item() for t in annual.time]

    import matplotlib.pyplot as plt
    import numpy as np

    # Bar chart with rolling mean
    st.subheader("Annual temperature anomaly")
    st.markdown(
        f"Each bar is one year's global mean temperature anomaly relative to "
        f"{baseline_start}-{baseline_end}. Blue bars are cooler than the "
        f"baseline, red bars are warmer. The black line is a {window}-year "
        f"rolling mean."
    )

    rolling = annual.rolling(time=window, center=True).mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    colours = ["steelblue" if v < 0 else "firebrick" for v in annual.values]
    ax.bar(years, annual.values, color=colours, width=0.8, alpha=0.7)
    ax.plot(years, rolling.values, color="black", linewidth=2,
            label=f"{window}-year rolling mean")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.set_ylabel(f"Temperature anomaly (deg C, vs {baseline_start}-{baseline_end})")
    ax.set_title("Global temperature anomaly (HadCRUT5)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    st.pyplot(fig)

    with st.expander(":material/code: Code for this plot"):
        st.code(_build_trend_code(window, baseline_start, baseline_end), language="python")

    # Warming stripes
    st.subheader("Warming stripes")
    st.markdown(
        "Each vertical stripe is one year, coloured by its anomaly. This "
        "visualisation (inspired by Ed Hawkins' #ShowYourStripes) makes the "
        "acceleration of warming visually immediate."
    )

    fig2, ax2 = plt.subplots(figsize=(12, 2.5))
    norm = plt.Normalize(vmin=float(annual.min()), vmax=float(annual.max()))
    cmap = plt.cm.RdBu_r
    for i, (yr, val) in enumerate(zip(years, annual.values)):
        ax2.axvspan(yr - 0.5, yr + 0.5, color=cmap(norm(val)))
    ax2.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    ax2.set_yticks([])
    ax2.set_title("Warming stripes (HadCRUT5)")
    ax2.set_xlabel("Year")
    fig2.tight_layout()
    st.pyplot(fig2)

    with st.expander(":material/code: Code for this plot"):
        st.code(_build_stripes_code(baseline_start, baseline_end), language="python")

    # Decadal averages
    st.subheader("Decadal averages")
    st.markdown(
        "Averaging by decade smooths out year-to-year variability (El Nino, "
        "volcanic eruptions) and shows the persistent trend more clearly."
    )

    import pandas as pd

    years_arr = np.array(years)
    decades = (years_arr // 10) * 10
    decade_df = pd.DataFrame({
        "year": years_arr, "decade": decades, "anomaly": annual.values,
    })
    decade_mean = decade_df.groupby("decade")["anomaly"].mean()

    dec_colours = ["steelblue" if v < 0 else "firebrick" for v in decade_mean.values]

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.bar(decade_mean.index, decade_mean.values, width=8, color=dec_colours, alpha=0.8)
    ax3.axhline(0, color="gray", linewidth=0.5)
    ax3.set_ylabel(f"Temperature anomaly (deg C, vs {baseline_start}-{baseline_end})")
    ax3.set_title("Decadal average temperature anomaly")
    ax3.grid(alpha=0.3, axis="y")
    fig3.tight_layout()
    st.pyplot(fig3)

    with st.expander(":material/code: Code for this plot"):
        st.code(_build_decade_code(baseline_start, baseline_end), language="python")

    # Key stats
    st.subheader("At a glance")
    recent_decade = decade_mean.iloc[-1] if len(decade_mean) > 0 else 0
    warmest_year_idx = int(np.nanargmax(annual.values))
    warmest_year = years[warmest_year_idx]
    warmest_val = float(annual.values[warmest_year_idx])

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Record starts", "1850", border=True)
    col_b.metric("Warmest year", str(warmest_year), border=True)
    col_c.metric(
        "Warmest year anomaly",
        f"+{warmest_val:.2f} deg C",
        border=True,
    )
    col_d.metric(
        "Latest decade",
        f"+{recent_decade:.2f} deg C",
        border=True,
    )

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
            "from pathlib import Path\n"
            "\n"
            "# HadCRUT5 global monthly summary series (open access, Met Office)\n"
            "url = (\n"
            "    'https://www.metoffice.gov.uk/hadobs/hadcrut5/data/'\n"
            "    'HadCRUT.5.1.0.0/analysis/diagnostics/'\n"
            "    'HadCRUT.5.1.0.0.analysis.summary_series.global.monthly.nc'\n"
            ")\n"
            "\n"
            "out = Path('hadcrut5_global_monthly.nc')\n"
            "with requests.get(url, stream=True, timeout=120) as r:\n"
            "    r.raise_for_status()\n"
            "    with open(out, 'wb') as f:\n"
            "        for chunk in r.iter_content(chunk_size=1 << 20):\n"
            "            f.write(chunk)\n"
            "print(f'Downloaded {out} ({out.stat().st_size / 1e3:.0f} KB)')\n"
            "\n"
            "# Other products:\n"
            "# Gridded field (maps):  ...analysis.anomalies.ensemble_mean.nc  (~40 MB)\n"
            "# Non-infilled field:    ...noninfilled.anomalies.ensemble_mean.nc\n"
            "# Annual global series:  ...analysis.summary_series.global.annual.nc\n",
            language="python",
        )

    with st.expander(":material/folder_open: Open and inspect", expanded=False):
        st.code(
            "import xarray as xr\n"
            "\n"
            "ds = xr.open_dataset('hadcrut5_global_monthly.nc')\n"
            "print(ds)\n"
            "\n"
            "# The main variable is tas_mean (temperature anomaly in deg C)\n"
            "# Baseline is 1961-1990 by default\n"
            "da = ds['tas_mean'].squeeze()\n"
            "print(f'\\nTime range: {da.time.values[0]} to {da.time.values[-1]}')\n"
            "print(f'Shape: {da.shape}')\n"
            "print(f'Mean anomaly: {float(da.mean()):.3f} deg C')\n",
            language="python",
        )

    st.caption(
        "Requires `requests` and `xarray` (with `netcdf4`). "
        "Works in any Python 3.10+ environment, Colab, or Jupyter."
    )

    # Next steps
    st.markdown("---")
    st.subheader("Next steps")
    st.markdown(
        "- See the full dataset documentation in `docs/hadcrut5/README.md`\n"
        "- Download the gridded product to see warming patterns by region\n"
        "- Compare with the HadCET recipe to see how England tracks the global mean\n"
        "- Use CMIP6 projections to see what models predict for coming decades"
    )
