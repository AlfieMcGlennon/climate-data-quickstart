"""Download and parse a GHCNd station .dly file to a tidy DataFrame.

Edit the USER CONFIGURATION block and run:

    python scripts/ghcnd_download.py

The default downloads the London Heathrow station record, parses the
fixed-width .dly format, scales TMAX/TMIN/PRCP from tenths into natural
units, and writes a CSV.

Documentation: docs/ghcnd/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# GHCNd station ID (11 characters). Browse ghcnd-stations.txt for the
# full list. Examples in docs/ghcnd/README.md.
STATION_ID: str = "UKM00003772"  # London Heathrow

# Elements to keep. GHCNd has ~50 available; these are the common five.
ELEMENTS: tuple[str, ...] = ("TMAX", "TMIN", "PRCP", "SNOW", "SNWD")

# Filter to QC-passing observations only.
DROP_FAILED_QC: bool = True

OUTPUT_DIR: str = "./data/ghcnd"
OUTPUT_FILENAME: str = "ghcnd_heathrow.csv"
# ==================================================================


GHCND_BASE: str = "https://www.ncei.noaa.gov/pub/data/ghcn/daily"

# Scale factors for the core elements (value in file is integer).
_SCALE: dict[str, float] = {
    "TMAX": 0.1,   # tenths of degC -> degC
    "TMIN": 0.1,
    "TAVG": 0.1,
    "PRCP": 0.1,   # tenths of mm -> mm
    "SNOW": 1.0,   # already in mm
    "SNWD": 1.0,   # already in mm
}


def _dly_colspecs() -> tuple[list[tuple[int, int]], list[str]]:
    """Build the column specs for pandas.read_fwf for a .dly file.

    The GHCNd .dly format is 269 chars per line:
    - ID (1-11), YEAR (12-15), MONTH (16-17), ELEMENT (18-21)
    - Then 31 daily records of 8 chars each: VALUE (5), MFLAG (1),
      QFLAG (1), SFLAG (1). pandas colspecs are (start, end) zero-indexed.
    """
    colspecs = [(0, 11), (11, 15), (15, 17), (17, 21)]
    names = ["id", "year", "month", "element"]
    pos = 21
    for d in range(1, 32):
        colspecs += [
            (pos, pos + 5),
            (pos + 5, pos + 6),
            (pos + 6, pos + 7),
            (pos + 7, pos + 8),
        ]
        names += [f"value_{d:02d}", f"mflag_{d:02d}", f"qflag_{d:02d}", f"sflag_{d:02d}"]
        pos += 8
    return colspecs, names


def download(
    station_id: str = STATION_ID,
    elements: tuple[str, ...] = ELEMENTS,
    drop_failed_qc: bool = DROP_FAILED_QC,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download one GHCNd station .dly file, parse, and save a tidy CSV.

    The output DataFrame has columns: ``id``, ``date``, ``element``,
    ``value`` (scaled to natural units), and ``qflag``, ``mflag``,
    ``sflag`` (the three QC/metadata flags).

    Implementation uses a single vectorised ``wide_to_long`` reshape
    (one pass over the data) followed by vectorised scaling and
    date construction.

    Args:
        station_id: 11-character GHCNd station ID.
        elements: Tuple of element codes to keep (e.g. ``("TMAX", "TMIN", "PRCP")``).
        drop_failed_qc: If True, drop rows with non-blank QFLAG.
        output_dir: Directory to write to.
        output_filename: Output CSV filename.

    Returns:
        Path to the written CSV.
    """
    import pandas as pd

    url = f"{GHCND_BASE}/all/{station_id}.dly"
    colspecs, names = _dly_colspecs()
    wide = pd.read_fwf(url, colspecs=colspecs, names=names, na_values=["-9999"])

    if elements:
        wide = wide[wide["element"].isin(elements)].copy()

    # Single vectorised reshape: four stub columns (value, mflag, qflag, sflag)
    # with suffix "_DD" for day of month.
    long = pd.wide_to_long(
        wide,
        stubnames=["value", "mflag", "qflag", "sflag"],
        i=["id", "year", "month", "element"],
        j="day",
        sep="_",
        suffix=r"\d{2}",
    ).reset_index()
    long["day"] = long["day"].astype(int)

    # Drop rows where the value is missing
    long = long.dropna(subset=["value"])

    # Build a proper date; drop impossible combinations (e.g. Feb 30)
    long["date"] = pd.to_datetime(
        dict(year=long.year, month=long.month, day=long.day),
        errors="coerce",
    )
    long = long.dropna(subset=["date"]).copy()

    # Vectorised scaling: look up the factor per element
    long["value"] = long["value"] * long["element"].map(_SCALE).fillna(1.0)

    if drop_failed_qc:
        long = long[long["qflag"].isna() | (long["qflag"].str.strip() == "")]

    long = (
        long[["id", "date", "element", "value", "mflag", "qflag", "sflag"]]
        .sort_values(["element", "date"])
        .reset_index(drop=True)
    )

    out = Path(output_dir) / output_filename
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    return out


if __name__ == "__main__":
    path = download()
    print(f"Downloaded and parsed: {path}")
    print(f"Size: {path.stat().st_size / 1e3:.1f} kB")
