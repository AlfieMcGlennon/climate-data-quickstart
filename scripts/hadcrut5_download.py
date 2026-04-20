"""Download HadCRUT5 global temperature anomaly NetCDF from the Met Office.

Edit the USER CONFIGURATION block and run:

    python scripts/hadcrut5_download.py

The default pulls the infilled ensemble-mean NetCDF (~40 MB).

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
# Current at time of writing: 5.1.0.0. Check
# https://www.metoffice.gov.uk/hadobs/hadcrut5/ for the latest.
SUB_VERSION: str = "5.1.0.0"

# Product: one of
#   "analysis.anomalies.ensemble_mean"           - infilled, global continuous field
#   "noninfilled.anomalies.ensemble_mean"        - non-infilled, has gaps where obs are sparse
#   "analysis.summary_series.global.monthly"     - global-mean time series, infilled
#   "noninfilled.summary_series.global.monthly"  - global-mean time series, non-infilled
PRODUCT: str = "analysis.anomalies.ensemble_mean"

OUTPUT_DIR: str = "./data/hadcrut5"
OUTPUT_FILENAME: str = "hadcrut5_analysis_ensemble_mean.nc"
# ==================================================================


BASE_URL: str = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data"


def _build_url(sub_version: str, product: str) -> str:
    """Return the canonical HadCRUT5 NetCDF URL for a product string.

    The Met Office lays out files under
    ``/data/HadCRUT.<ver>/<folder>/HadCRUT.<ver>.<stem>.nc`` where
    ``<folder>`` is either ``analysis`` (infilled fields) or
    ``non-infilled`` (non-infilled fields), and ``diagnostics/`` is
    appended for per-series summary products.
    """
    if product.startswith("analysis"):
        folder = "analysis"
        stem = product  # e.g. "analysis.ensemble_mean"
    elif product.startswith("noninfilled"):
        folder = "non-infilled"
        stem = product
    else:
        raise ValueError(
            f"Unknown product {product!r}. Expected something starting with "
            f"'analysis' or 'noninfilled'."
        )

    # Summary series and component series live under a diagnostics/ subdir
    if "summary_series" in product or "component_series" in product or "ensemble_series" in product:
        folder = f"{folder}/diagnostics"

    return (
        f"{BASE_URL}/HadCRUT.{sub_version}/{folder}/"
        f"HadCRUT.{sub_version}.{stem}.nc"
    )


def download(
    sub_version: str = SUB_VERSION,
    product: str = PRODUCT,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Stream a HadCRUT5 NetCDF to disk.

    Args:
        sub_version: HadCRUT5 patch version string, e.g. ``"5.1.0.0"``.
        product: Product string; see module docstring for the supported values.
        output_dir: Directory to write to.
        output_filename: Output filename.

    Returns:
        Path to the downloaded NetCDF.
    """
    import requests

    url = _build_url(sub_version, product)
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
