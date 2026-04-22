"""Download GPWv4 population density from NASA SEDAC.

Edit the USER CONFIGURATION block and run:

    python scripts/gpw_population_download.py

Requires a free NASA Earthdata account. Credentials must be in
``~/.netrc`` (Linux/macOS) or ``~/_netrc`` (Windows) with an entry for
``machine urs.earthdata.nasa.gov``.

Documentation: docs/gpw-population/README.md
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
YEAR: int = 2020
RESOLUTION: str = "2pt5_min"  # 30_sec, 2pt5_min, 15_min, 30_min, 1_deg
OUTPUT_DIR: str = "./data/gpw"
# ==================================================================


SEDAC_BASE = (
    "https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/"
    "gpw-v4-population-density-rev11"
)


def download(
    year: int = YEAR,
    resolution: str = RESOLUTION,
    output_dir: str = OUTPUT_DIR,
) -> Path:
    """Download GPWv4 population density GeoTIFF.

    Args:
        year: Target year (2000, 2005, 2010, 2015, or 2020).
        resolution: Grid resolution string.
        output_dir: Directory to write to.

    Returns:
        Path to the extracted GeoTIFF.
    """
    from netrc import netrc

    import requests

    from common.credentials import check_netrc_entry

    check_netrc_entry("urs.earthdata.nasa.gov")

    netrc_path = check_netrc_entry("urs.earthdata.nasa.gov")
    creds = netrc(str(netrc_path))
    username, _, password = creds.authenticators("urs.earthdata.nasa.gov")

    session = _earthdata_session(username, password)

    zip_name = f"gpw-v4-population-density-rev11_{year}_{resolution}_tif.zip"
    url = f"{SEDAC_BASE}/{zip_name}"

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / zip_name

    if not zip_path.exists():
        print(f"Downloading {zip_name}...")
        resp = session.get(url, stream=True, timeout=300)
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
        print(f"Downloaded {zip_path} ({zip_path.stat().st_size / 1e6:.1f} MB)")

    tif_path = _extract_tif(zip_path, out_dir)
    return tif_path


def _earthdata_session(
    username: str, password: str
) -> "requests.Session":
    """Create a requests session that handles Earthdata login redirects."""
    import requests

    class SessionWithHeaderRedirection(requests.Session):
        AUTH_HOST = "urs.earthdata.nasa.gov"

        def __init__(self, user: str, pw: str):
            super().__init__()
            self.auth = (user, pw)

        def rebuild_auth(
            self, prepared_request: requests.PreparedRequest, response: requests.Response
        ) -> None:
            headers = prepared_request.headers
            url = prepared_request.url
            if "Authorization" in headers:
                orig = requests.utils.urlparse(response.request.url)
                redir = requests.utils.urlparse(url)
                if (
                    orig.hostname != redir.hostname
                    and redir.hostname != self.AUTH_HOST
                    and orig.hostname != self.AUTH_HOST
                ):
                    del headers["Authorization"]

    return SessionWithHeaderRedirection(username, password)


def _extract_tif(zip_path: Path, out_dir: Path) -> Path:
    """Extract the first .tif file from a SEDAC zip archive."""
    with zipfile.ZipFile(zip_path) as zf:
        tif_names = [n for n in zf.namelist() if n.endswith(".tif")]
        if not tif_names:
            raise FileNotFoundError(f"No .tif file found in {zip_path}")
        target = tif_names[0]
        extracted = out_dir / Path(target).name
        if not extracted.exists():
            zf.extract(target, out_dir)
            actual = out_dir / target
            if actual != extracted:
                actual.rename(extracted)
        print(f"Extracted: {extracted}")
    return extracted


if __name__ == "__main__":
    path = download()
    print(f"GeoTIFF: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
