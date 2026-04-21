"""Download CMIP6 data directly from the ESGF federated archive.

Edit the USER CONFIGURATION block below and run directly:

    python scripts/esgf_cmip6_download.py

The defaults search the DKRZ index node for monthly near-surface air
temperature from MPI-ESM1-2-LR historical, then download the first matching
file. No authentication is needed for CMIP6 HTTP downloads.

This script uses the ESGF Search REST API with ``requests`` (zero extra
dependencies beyond the standard scientific stack). For the CDS-based CMIP6
route, see scripts/cmip6_download.py instead.

Documentation: docs/esgf-cmip6/README.md
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
# ESGF Solr index node to search. DKRZ is the most stable during the
# ESGF-NG transition (the LLNL node was shut down July 2025).
SEARCH_NODE: str = "https://esgf-data.dkrz.de/esg-search/search"

# CMIP6 search facets. These must match the CMIP6 controlled vocabulary
# exactly. See https://wcrp-cmip.github.io/CMIP6_CVs/ for valid values.
SOURCE_ID: str = "MPI-ESM1-2-LR"
EXPERIMENT_ID: str = "historical"
VARIABLE_ID: str = "tas"
TABLE_ID: str = "Amon"
VARIANT_LABEL: str = "r1i1p1f1"
GRID_LABEL: str = "gn"

OUTPUT_DIR: str = "./data/esgf-cmip6"
# None => auto-name from the first matching file on ESGF
OUTPUT_FILENAME: str | None = None
# ==================================================================


def search_esgf(
    search_node: str,
    source_id: str,
    experiment_id: str,
    variable_id: str,
    table_id: str,
    variant_label: str,
    grid_label: str,
    limit: int = 10,
) -> list[dict]:
    """Query the ESGF Search REST API for CMIP6 file records.

    Args:
        search_node: Full URL of the Solr search endpoint.
        source_id: Model name (e.g. ``"MPI-ESM1-2-LR"``).
        experiment_id: Experiment (e.g. ``"historical"``).
        variable_id: CMOR variable short name (e.g. ``"tas"``).
        table_id: MIP table (e.g. ``"Amon"``).
        variant_label: Ensemble member (e.g. ``"r1i1p1f1"``).
        grid_label: Grid type (e.g. ``"gn"``).
        limit: Maximum number of file records to return.

    Returns:
        List of Solr document dicts, one per file.

    Raises:
        RuntimeError: If the search returns no results or the HTTP request
            fails.
    """
    import requests

    params = {
        "project": "CMIP6",
        "source_id": source_id,
        "experiment_id": experiment_id,
        "variable_id": variable_id,
        "table_id": table_id,
        "variant_label": variant_label,
        "grid_label": grid_label,
        "latest": "true",
        "replica": "false",
        "type": "File",
        "format": "application/solr+json",
        "limit": limit,
    }

    resp = requests.get(search_node, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    num_found = data["response"]["numFound"]
    if num_found == 0:
        hints = []
        if variant_label.endswith("f1") and source_id in (
            "UKESM1-0-LL", "HadGEM3-GC31-LL", "CNRM-CM6-1",
            "CNRM-ESM2-1", "MIROC-ES2L",
        ):
            hints.append(
                f"{source_id} uses r1i1p1f2 as its flagship member, "
                f"not r1i1p1f1. Try changing variant_label to "
                f"{variant_label[:-1]}2."
            )
        if grid_label == "gr" or grid_label == "gr1":
            hints.append(
                "Not all models provide regridded output. "
                "Try grid_label='gn' (native grid)."
            )
        hint_str = " ".join(hints) if hints else ""
        raise RuntimeError(
            f"ESGF search returned 0 files for "
            f"{variable_id}_{table_id}_{source_id}_{experiment_id}_"
            f"{variant_label}_{grid_label}. "
            f"Check that this facet combination exists. {hint_str}"
        )

    docs = data["response"]["docs"]
    print(f"ESGF search: {num_found} file(s) found, {len(docs)} returned.")
    return docs


def extract_http_url(doc: dict) -> str:
    """Extract the HTTP download URL from an ESGF file record.

    The ``url`` field contains pipe-separated triples like
    ``url|mime_type|service_name``. We want the one where service_name
    is ``HTTPServer``.

    Args:
        doc: A single Solr document dict from the search response.

    Returns:
        The HTTP download URL.

    Raises:
        ValueError: If no HTTPServer URL is found in the record.
    """
    for url_entry in doc.get("url", []):
        parts = url_entry.split("|")
        if len(parts) == 3 and parts[2] == "HTTPServer":
            return parts[0]

    title = doc.get("title", "<unknown>")
    raise ValueError(
        f"No HTTPServer URL found for file '{title}'. "
        f"Available URL entries: {doc.get('url', [])}"
    )


def download(
    search_node: str = SEARCH_NODE,
    source_id: str = SOURCE_ID,
    experiment_id: str = EXPERIMENT_ID,
    variable_id: str = VARIABLE_ID,
    table_id: str = TABLE_ID,
    variant_label: str = VARIANT_LABEL,
    grid_label: str = GRID_LABEL,
    output_dir: str = OUTPUT_DIR,
    output_filename: str | None = OUTPUT_FILENAME,
) -> Path:
    """Search ESGF for a CMIP6 file and download it via HTTP.

    Searches the ESGF index for files matching the given facets, then
    downloads the first result. CMIP6 data is open access and does not
    require authentication for HTTP downloads from most data nodes.

    Args:
        search_node: Full URL of the ESGF Solr search endpoint.
        source_id: Model name.
        experiment_id: Experiment identifier.
        variable_id: CMOR variable short name.
        table_id: MIP table (determines frequency and realm).
        variant_label: Ensemble member (ripf notation).
        grid_label: Grid type (``"gn"`` for native, ``"gr"`` for regridded).
        output_dir: Directory to write to, relative or absolute.
        output_filename: Override filename. If ``None``, uses the original
            CMIP6 DRS filename from ESGF.

    Returns:
        Path to the downloaded NetCDF file.

    Raises:
        RuntimeError: If the ESGF search returns no results.
        ValueError: If no HTTP download URL can be extracted from the
            search results.
    """
    import requests

    docs = search_esgf(
        search_node=search_node,
        source_id=source_id,
        experiment_id=experiment_id,
        variable_id=variable_id,
        table_id=table_id,
        variant_label=variant_label,
        grid_label=grid_label,
    )

    file_url = extract_http_url(docs[0])
    # CMIP6 filenames follow the DRS convention, so the URL basename is
    # already a well-structured name like tas_Amon_MPI-ESM1-2-LR_historical_...nc
    filename = output_filename or file_url.split("/")[-1]

    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip re-download if the file already exists and is non-empty
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"File already exists: {output_path}")
        return output_path

    print(f"Downloading {filename} ...")
    print(f"  URL: {file_url}")

    with requests.get(file_url, stream=True, timeout=600) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  Progress: {downloaded / 1e6:.1f} / "
                          f"{total / 1e6:.1f} MB ({pct:.0f}%)",
                          end="", flush=True)
                else:
                    print(f"\r  Downloaded: {downloaded / 1e6:.1f} MB",
                          end="", flush=True)
        print()  # newline after progress

    return output_path


# Models whose flagship ensemble member uses f2 forcing
_F2_MODELS = {"CNRM-CM6-1", "HadGEM3-GC31-LL", "UKESM1-0-LL"}


def _flagship_variant(source_id: str, realisation: int = 1) -> str:
    """Build the variant_label for a given model and realisation number."""
    f = 2 if source_id in _F2_MODELS else 1
    return f"r{realisation}i1p1f{f}"


def download_multi(
    search_node: str = SEARCH_NODE,
    source_ids: list[str] | None = None,
    experiment_id: str = EXPERIMENT_ID,
    variable_id: str = VARIABLE_ID,
    table_id: str = TABLE_ID,
    n_members: int = 1,
    grid_label: str = GRID_LABEL,
    output_dir: str = OUTPUT_DIR,
) -> list[Path]:
    """Download one file per model/member combination.

    For each (source_id, realisation) pair, searches ESGF and downloads
    the first matching file. If the requested grid_label returns no
    results, falls back to the alternative (gn -> gr or gr -> gn).
    Models that still return no results are skipped with a warning.

    Args:
        search_node: Full URL of the ESGF Solr search endpoint.
        source_ids: List of CMIP6 model names. Defaults to three models.
        experiment_id: Experiment identifier.
        variable_id: CMOR variable short name.
        table_id: MIP table.
        n_members: Number of realisations (r1, r2, ...) per model.
        grid_label: Grid type (tries fallback if no results).
        output_dir: Directory to write files into.

    Returns:
        List of Paths to successfully downloaded files.
    """
    if source_ids is None:
        source_ids = ["MPI-ESM1-2-LR", "UKESM1-0-LL", "IPSL-CM6A-LR"]

    fallback_grid = "gr" if grid_label == "gn" else "gn"

    paths: list[Path] = []
    for source_id in source_ids:
        for r in range(1, n_members + 1):
            variant_label = _flagship_variant(source_id, r)
            for gl in (grid_label, fallback_grid):
                try:
                    path = download(
                        search_node=search_node,
                        source_id=source_id,
                        experiment_id=experiment_id,
                        variable_id=variable_id,
                        table_id=table_id,
                        variant_label=variant_label,
                        grid_label=gl,
                        output_dir=output_dir,
                    )
                    paths.append(path)
                    break
                except (RuntimeError, ValueError) as exc:
                    if gl == fallback_grid:
                        print(
                            f"  Skipping {source_id} {variant_label}: "
                            f"no data on {grid_label} or {fallback_grid}"
                        )
                    else:
                        print(
                            f"  {source_id}: no {gl} data, "
                            f"trying {fallback_grid}..."
                        )
    return paths


if __name__ == "__main__":
    path = download()
    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size / 1e6:.2f} MB")
