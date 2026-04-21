"""Download ECMWF Open Data IFS forecast fields.

Edit the USER CONFIGURATION block below and run directly:

    python scripts/ecmwf_open_data_download.py

The defaults fetch the latest deterministic forecast of 2 metre temperature
at T+24 h. No registration or API key is required.

Documentation: docs/ecmwf-open-data/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make ``common`` importable when running this script from the repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# GRIB short names. See docs/ecmwf-open-data/README.md for common variables,
# or the ECMWF parameter database for the full list.
PARAMS: list[str] = ["2t"]

# Forecast lead time in hours. 0-144 every 3h, then 150-240 every 6h
# for 00z/12z runs.
STEP: int = 24

# Forecast type: "fc" (HRES deterministic), "cf" (control), "pf" (perturbed)
TYPE: str = "fc"

# Forecast stream: "oper" (00z/12z), "scda" (06z/18z), "enfo" (ensemble)
STREAM: str = "oper"

# Model: "ifs", "aifs-single", "aifs-ens"
MODEL: str = "ifs"

# Where to save the output, relative to the repo root.
OUTPUT_DIR: str = "./data/ecmwf-open-data"
OUTPUT_FILENAME: str = "ecmwf_open_data_test.grib2"
# ==================================================================


def download(
    params: list[str] = PARAMS,
    step: int = STEP,
    fc_type: str = TYPE,
    stream: str = STREAM,
    model: str = MODEL,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download an IFS forecast slice from ECMWF Open Data.

    Uses the ``ecmwf-opendata`` client to fetch the latest available run.
    No authentication is needed.

    Args:
        params: GRIB short names (e.g. ``["2t", "msl"]``).
        step: Forecast lead time in hours.
        fc_type: ``"fc"`` for HRES, ``"cf"`` for control, ``"pf"`` for
            perturbed ensemble members.
        stream: ``"oper"`` for 00z/12z, ``"scda"`` for 06z/18z,
            ``"enfo"`` for ensemble.
        model: ``"ifs"``, ``"aifs-single"``, or ``"aifs-ens"``.
        output_dir: Directory to write to, relative or absolute.
        output_filename: Output filename.

    Returns:
        The path to the downloaded GRIB2 file.
    """
    from ecmwf.opendata import Client

    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = Client(source="ecmwf", model=model)
    client.retrieve(
        step=step,
        type=fc_type,
        stream=stream,
        param=params,
        target=str(output_path),
    )

    return output_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
