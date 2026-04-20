"""Download and parse HadCET monthly or daily temperature data from the Met Office.

Edit the USER CONFIGURATION block and run:

    python scripts/hadcet_download.py

The default pulls the monthly mean file, parses it to long-format, and
writes a CSV.

Documentation: docs/hadcet/README.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# Resolution: "monthly" or "daily"
RESOLUTION: str = "monthly"

# Statistic: "mean", "max", or "min"
# (max/min are available monthly and daily from 1878)
STATISTIC: str = "mean"

OUTPUT_DIR: str = "./data/hadcet"
OUTPUT_FILENAME: str = "hadcet_monthly_mean.csv"
# ==================================================================


HADLEY_BASE: str = "https://hadleyserver.metoffice.gov.uk/hadcet/data"


def _url_for(resolution: str, statistic: str) -> str:
    """Build the canonical HadCET file URL for a given resolution/statistic."""
    if resolution not in {"monthly", "daily"}:
        raise ValueError(f"resolution must be 'monthly' or 'daily', got {resolution!r}")
    if statistic not in {"mean", "max", "min"}:
        raise ValueError(f"statistic must be 'mean', 'max', or 'min', got {statistic!r}")
    return f"{HADLEY_BASE}/{statistic}temp_{resolution}_totals.txt"


def _parse_monthly(text: str):
    """Parse a HadCET monthly totals file into a tidy long-format DataFrame."""
    import pandas as pd

    lines = text.splitlines()
    data_start = next(
        i for i, line in enumerate(lines)
        if len(line.strip()) >= 4 and line.strip()[:4].isdigit()
    )
    cols = [
        "year", "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec", "ann",
    ]
    wide = pd.read_csv(
        io.StringIO("\n".join(lines[data_start:])),
        sep=r"\s+", header=None, names=cols, engine="python",
    )
    months = {m: i + 1 for i, m in enumerate(cols[1:13])}
    long = (
        wide.drop(columns=["ann"])
        .melt(id_vars="year", var_name="month_name", value_name="temperature_degC")
    )
    long["month"] = long["month_name"].map(months)
    long["date"] = pd.to_datetime(dict(year=long["year"], month=long["month"], day=1))
    long = (
        long[long["temperature_degC"] > -99]
        .sort_values("date")
        .reset_index(drop=True)
        [["date", "year", "month", "temperature_degC"]]
    )
    return long


def _parse_daily(text: str):
    """Parse a HadCET daily totals file into a tidy DataFrame."""
    import pandas as pd

    lines = text.splitlines()
    data_start = next(
        i for i, line in enumerate(lines)
        if len(line.strip()) >= 4 and line.strip()[:4].isdigit()
    )
    df = pd.read_csv(
        io.StringIO("\n".join(lines[data_start:])),
        sep=r"\s+", header=None,
        names=["year", "month", "day", "temperature_degC"],
        engine="python",
    )
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df = (
        df[df["temperature_degC"] > -99]
        .sort_values("date")
        .reset_index(drop=True)
        [["date", "year", "month", "day", "temperature_degC"]]
    )
    return df


def download(
    resolution: str = RESOLUTION,
    statistic: str = STATISTIC,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Fetch HadCET text file, parse to DataFrame, write CSV.

    Args:
        resolution: ``"monthly"`` or ``"daily"``.
        statistic: ``"mean"``, ``"max"``, or ``"min"``.
        output_dir: Directory to write to.
        output_filename: Output CSV filename.

    Returns:
        Path to the written CSV.
    """
    import requests

    url = _url_for(resolution, statistic)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    if resolution == "monthly":
        df = _parse_monthly(resp.text)
    else:
        df = _parse_daily(resp.text)

    out = Path(output_dir) / output_filename
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out


if __name__ == "__main__":
    path = download()
    print(f"Downloaded and parsed: {path}")
    print(f"Size: {path.stat().st_size / 1e3:.1f} kB")
