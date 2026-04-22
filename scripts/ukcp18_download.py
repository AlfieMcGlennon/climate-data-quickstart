"""Download UKCP18 regional projections from the CEDA Archive.

Edit the USER CONFIGURATION block and run:

    python scripts/ukcp18_download.py

Requires a free CEDA account. Set the ``CEDA_TOKEN`` environment variable
or save the token to ``~/.ceda_token``.

Documentation: docs/ukcp18/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
VARIABLE: str = "tas"
SCENARIO: str = "rcp85"
COLLECTION: str = "land-rcm"
DOMAIN: str = "uk"
RESOLUTION: str = "12km"
ENSEMBLE_MEMBER: str = "01"
FREQUENCY: str = "mon"
VERSION: str = "v20190731"
TIME_PERIOD: str = "198012-208011"
OUTPUT_DIR: str = "./data/ukcp18"
# ==================================================================


CEDA_BASE = "https://dap.ceda.ac.uk/badc/ukcp18/data"


def download(
    variable: str = VARIABLE,
    scenario: str = SCENARIO,
    collection: str = COLLECTION,
    domain: str = DOMAIN,
    resolution: str = RESOLUTION,
    ensemble_member: str = ENSEMBLE_MEMBER,
    frequency: str = FREQUENCY,
    version: str = VERSION,
    time_period: str = TIME_PERIOD,
    output_dir: str = OUTPUT_DIR,
) -> Path:
    """Download a UKCP18 NetCDF file from the CEDA archive.

    Args:
        variable: CF variable name (e.g. ``tas``, ``pr``).
        scenario: Emissions scenario (e.g. ``rcp85``).
        collection: Data collection (e.g. ``land-rcm``).
        domain: Domain (e.g. ``uk``).
        resolution: Grid resolution (e.g. ``12km``).
        ensemble_member: Ensemble member ID (e.g. ``01``).
        frequency: Temporal frequency (e.g. ``mon``, ``day``).
        version: Dataset version string (e.g. ``v20190731``).
        time_period: Time range string (e.g. ``19801201-20801130``).
        output_dir: Directory to write to.

    Returns:
        Path to the downloaded NetCDF.
    """
    import requests

    from common.credentials import check_ceda_token

    token = check_ceda_token()

    filename = (
        f"{variable}_{scenario}_{collection}_{domain}_{resolution}_"
        f"{ensemble_member}_{frequency}_{time_period}.nc"
    )
    url = (
        f"{CEDA_BASE}/{collection}/{domain}/{resolution}/{scenario}/"
        f"{ensemble_member}/{variable}/{frequency}/{version}/{filename}"
    )

    out = Path(output_dir) / filename
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.exists() and out.stat().st_size > 0:
        print(f"Already downloaded: {out}")
        return out

    print(f"Downloading {filename}...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, stream=True, timeout=600)
    resp.raise_for_status()

    with open(out, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)

    print(f"Downloaded {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


if __name__ == "__main__":
    path = download()
    print(f"NetCDF: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
