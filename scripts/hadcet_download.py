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


def _find_data_start(lines: list[str], expected_columns: int) -> int:
    """Find the first line that looks like a data row, not a header.

    A data row is one that starts with a 4-digit year and has at least
    ``expected_columns`` whitespace-separated tokens. This rejects header
    lines like "1659-1973 Manley..." that happen to start with four
    digits but lack the numeric columns.
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) < 4 or not stripped[:4].isdigit():
            continue
        tokens = stripped.split()
        if len(tokens) >= expected_columns and all(
            _is_numeric_token(t) for t in tokens[:expected_columns]
        ):
            return i
    raise RuntimeError("Could not locate the start of the HadCET data table.")


def _is_numeric_token(token: str) -> bool:
    """True if a token is an integer, float, or negative value (e.g. -99.9)."""
    try:
        float(token)
        return True
    except ValueError:
        return False


def _parse_monthly(text: str):
    """Parse a HadCET monthly totals file into a tidy long-format DataFrame.

    Monthly files are whitespace-delimited with one row per year: a
    year column followed by 12 monthly values and an annual mean.
    Missing values are encoded as ``-99.9``.
    """
    import pandas as pd

    lines = text.splitlines()
    # Expect 14 columns: year + 12 months + annual
    data_start = _find_data_start(lines, expected_columns=14)
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
    # Use datetime64[s] precision rather than the default ns, because ns
    # only spans 1677-2262. HadCET monthly data starts in 1659.
    long["date"] = _ymd_to_datetime(
        long["year"].astype(int).to_numpy(),
        long["month"].astype(int).to_numpy(),
        1,
    )
    long = (
        long[long["temperature_degC"] > -99]
        .sort_values("date")
        .reset_index(drop=True)
        [["date", "year", "month", "temperature_degC"]]
    )
    return long


def _ymd_to_datetime(years, months, days):
    """Build a numpy datetime64[D] array from year/month/day arrays.

    This avoids the pandas default datetime64[ns] range (1677-2262) so
    we can represent dates back to 1659.
    """
    import numpy as np

    if isinstance(days, int):
        iso = [f"{int(y):04d}-{int(m):02d}-{int(days):02d}" for y, m in zip(years, months)]
    else:
        iso = [
            f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
            for y, m, d in zip(years, months, days)
        ]
    return np.array(iso, dtype="datetime64[D]")


def _parse_daily(text: str):
    """Parse a HadCET daily totals file into a tidy DataFrame.

    Current Met Office format: two whitespace-separated columns
    ``Date Value`` with Date as ISO 8601 ``YYYY-MM-DD`` and Value as a
    decimal temperature or ``-99.9`` for missing.
    """
    import pandas as pd
    import numpy as np

    lines = text.splitlines()
    # Find the first line that matches a YYYY-MM-DD start.
    data_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) >= 10 and stripped[4] == "-" and stripped[7] == "-":
            try:
                int(stripped[:4])
                int(stripped[5:7])
                int(stripped[8:10])
                data_start = i
                break
            except ValueError:
                continue
    if data_start is None:
        raise RuntimeError("Could not locate the start of the HadCET daily data table.")

    df = pd.read_csv(
        io.StringIO("\n".join(lines[data_start:])),
        sep=r"\s+", header=None,
        names=["date_str", "temperature_degC"],
        engine="python",
    )
    # datetime64[D] avoids the pandas ns precision limit for pre-1677 dates.
    df["date"] = np.array(df["date_str"].tolist(), dtype="datetime64[D]")
    df["year"] = df["date_str"].str.slice(0, 4).astype(int)
    df["month"] = df["date_str"].str.slice(5, 7).astype(int)
    df["day"] = df["date_str"].str.slice(8, 10).astype(int)
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
