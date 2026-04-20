"""Download E-OBS gridded daily observations from the Copernicus CDS.

Edit the USER CONFIGURATION block and run:

    python scripts/e_obs_download.py

The default pulls the ensemble-mean daily mean temperature at 0.1 degree
for the latest version. Files are large (up to ~1 GB for the full
1950-present period per variable); first run may take a while.

Documentation: docs/e-obs/README.md
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.credentials import check_cds_credentials  # noqa: E402


# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
# Variable: one of `mean_temperature`, `maximum_temperature`,
# `minimum_temperature`, `precipitation_amount`, `mean_sea_level_pressure`,
# `relative_humidity`, `global_radiation`, `wind_speed`.
VARIABLE: str = "mean_temperature"

# Product type: `ensemble_mean` (default) or `ensemble_spread` or
# `ensemble_members` (returns 100 files).
PRODUCT_TYPE: str = "ensemble_mean"

# Grid: "0.1deg" or "0.25deg".
GRID_RESOLUTION: str = "0.1deg"

# Version. Pin in reproducible work. See CDS dataset page for current
# available versions.
VERSION: str = "29.0e"

# Period. "full_period" is the whole 1950-present archive in one file.
PERIOD: str = "full_period"

OUTPUT_DIR: str = "./data/e-obs"
OUTPUT_FILENAME: str = "e_obs_test.nc"
# ==================================================================


def download(
    variable: str = VARIABLE,
    product_type: str = PRODUCT_TYPE,
    grid_resolution: str = GRID_RESOLUTION,
    version: str = VERSION,
    period: str = PERIOD,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = OUTPUT_FILENAME,
) -> Path:
    """Download and unzip an E-OBS whole-period NetCDF.

    E-OBS is served as zipped NetCDF; this function unzips the archive
    and leaves the main NetCDF at ``output_dir/output_filename``.

    Args:
        variable: CDS API variable name.
        product_type: ``ensemble_mean``, ``ensemble_spread``, or
            ``ensemble_members``.
        grid_resolution: ``0.1deg`` or ``0.25deg``.
        version: E-OBS version string, e.g. ``29.0e``.
        period: Always ``full_period`` (only option on CDS).
        output_dir: Directory to write to.
        output_filename: Final NetCDF filename.

    Returns:
        Path to the unzipped NetCDF.

    Raises:
        FileNotFoundError: If ``~/.cdsapirc`` is missing.
    """
    check_cds_credentials()

    import cdsapi

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir_path / (output_filename + ".zip")
    nc_path = output_dir_path / output_filename

    request = {
        "product_type": product_type,
        "variable": variable,
        "grid_resolution": grid_resolution,
        "period": period,
        "version": version,
        "format": "zip",
    }

    client = cdsapi.Client()
    client.retrieve("insitu-gridded-observations-europe", request).download(str(zip_path))

    # Extract every NetCDF from the archive. For ensemble_mean /
    # ensemble_spread the archive usually contains one file; for
    # ensemble_members it contains up to 100. We keep the first at
    # OUTPUT_FILENAME and any siblings alongside it named after the
    # archive members so nothing is silently discarded.
    with zipfile.ZipFile(zip_path) as zf:
        members = sorted(m for m in zf.namelist() if m.endswith(".nc"))
        if not members:
            raise RuntimeError(f"No NetCDF found in {zip_path}")
        with zf.open(members[0]) as src, open(nc_path, "wb") as dst:
            dst.write(src.read())
        for extra in members[1:]:
            extra_name = Path(extra).name
            with zf.open(extra) as src, open(output_dir_path / extra_name, "wb") as dst:
                dst.write(src.read())
    zip_path.unlink()

    return nc_path


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
