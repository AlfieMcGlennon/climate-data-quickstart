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
    """Build the column specs for pandas.read_fwf for a .dly file."""
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
        names += [f"value{d}", f"mflag{d}", f"qflag{d}", f"sflag{d}"]
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
    df_wide = pd.read_fwf(url, colspecs=colspecs, names=names, na_values=["-9999"])

    if elements:
        df_wide = df_wide[df_wide["element"].isin(elements)].copy()

    value_cols = [f"value{d}" for d in range(1, 32)]
    mflag_cols = [f"mflag{d}" for d in range(1, 32)]
    qflag_cols = [f"qflag{d}" for d in range(1, 32)]
    sflag_cols = [f"sflag{d}" for d in range(1, 32)]

    # Melt four times, then merge.
    def _melt(cols, name):
        m = df_wide.melt(
            id_vars=["id", "year", "month", "element"],
            value_vars=cols,
            var_name="day",
            value_name=name,
        )
        m["day"] = m["day"].str.replace(r"^[a-z]+", "", regex=True).astype(int)
        return m

    long = _melt(value_cols, "value")
    long["mflag"] = _melt(mflag_cols, "mflag")["mflag"]
    long["qflag"] = _melt(qflag_cols, "qflag")["qflag"]
    long["sflag"] = _melt(sflag_cols, "sflag")["sflag"]

    # Drop rows where the value is missing (-9999 became NaN via na_values)
    long = long.dropna(subset=["value"])

    # Build a proper date; drop impossible combinations (e.g. Feb 30)
    long["date"] = pd.to_datetime(
        dict(year=long.year, month=long.month, day=long.day),
        errors="coerce",
    )
    long = long.dropna(subset=["date"]).copy()

    # Apply element-specific scaling
    long["value"] = long.apply(
        lambda r: r["value"] * _SCALE.get(r["element"], 1.0),
        axis=1,
    )

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
