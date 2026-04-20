"""Download HadCRUT5 global temperature anomaly NetCDF from the Met Office.

Edit the USER CONFIGURATION block and run:

    python scripts/hadcrut5_download.py

The default pulls the infilled ensemble-mean NetCDF, a few tens of MB.

Documentation: docs/hadcrut5/README.md
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# Sub-version of HadCRUT5. Bumps when the Met Office reissues inputs.
SUB_VERSION: str = "5.0.2.0"

# Product: "ensemble_mean" (default) or "ensemble_mean.infilled" for the
# statistically infilled analysis. Members 1..200 can be pulled by setting
# MEMBER to an integer.
PRODUCT: str = "ensemble_mean.infilled"
MEMBER: int | None = None  # set to integer 1..200 for a specific ensemble member

OUTPUT_DIR: str = "./data/hadcrut5"
OUTPUT_FILENAME: str = "hadcrut5_ensemble_mean_infilled.nc"
# ==================================================================


BASE_URL: str = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/analysis"


def _build_url(sub_version: str, product: str, member: int | None) -> str:
    """Return the canonical HadCRUT5 analysis NetCDF URL."""
    stem = f"HadCRUT.{sub_version}.analysis.anomalies"
    if member is not None:
        # Ensemble member: HadCRUT.<ver>.analysis.anomalies.<N>.nc
        # or .<N>.infilled.nc
        suffix = ".infilled" if "infilled" in product else ""
        return f"{BASE_URL}/{stem}.{member}{suffix}.nc"
    return f"{BASE_URL}/{stem}.{product}.nc"


def download(
    sub_version: str = SUB_VERSION,
    product: str = PRODUCT,
    member: int | None = MEMBER,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Stream a HadCRUT5 NetCDF to disk.

    Args:
        sub_version: HadCRUT5 patch version string, e.g. ``"5.0.2.0"``.
        product: ``"ensemble_mean"`` or ``"ensemble_mean.infilled"`` for
            analyses; ignored when ``member`` is set.
        member: Optional ensemble member index 1..200. When given, the
            per-member file is fetched instead of the ensemble mean;
            infilling is inherited from ``product`` (whether the string
            contains ``infilled``).
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        Path to the downloaded NetCDF.
    """
    import requests

    url = _build_url(sub_version, product, member)
    out = Path(output_dir) / output_filename
    out.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return out


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
