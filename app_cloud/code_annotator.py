"""Augment a standalone download snippet with extra references for learners.

The canonical scripts in ``scripts/`` already carry well-written inline
comments and docstrings; the standalone snippet generator preserves
those. This module adds a reference block at the top of each snippet
listing the libraries used along with their documentation URLs, so a
learner can click straight through to authoritative docs without
guessing what ``cdsapi`` or ``xarray`` actually is.

Pure deterministic string transformation. No LLM calls, no network
access, no opinion.
"""

from __future__ import annotations

import ast
import re

from app.standalone_script import standalone_snippet


# Library metadata: import name -> (one-line description, docs URL)
LIBRARY_DOCS: dict[str, tuple[str, str]] = {
    "cdsapi": (
        "Copernicus CDS API client",
        "https://cds.climate.copernicus.eu/how-to-api",
    ),
    "xarray": (
        "Multi-dimensional labelled array library",
        "https://docs.xarray.dev/",
    ),
    "requests": (
        "Synchronous HTTP client",
        "https://docs.python-requests.org/",
    ),
    "ecmwf.opendata": (
        "ECMWF Open Data client",
        "https://github.com/ecmwf/ecmwf-opendata",
    ),
    "pandas": (
        "Tabular data library",
        "https://pandas.pydata.org/docs/",
    ),
    "numpy": (
        "Numerical array library",
        "https://numpy.org/doc/",
    ),
    "matplotlib": (
        "Plotting library",
        "https://matplotlib.org/stable/",
    ),
    "matplotlib.pyplot": (
        "Plotting library (pyplot interface)",
        "https://matplotlib.org/stable/api/pyplot_summary.html",
    ),
    "cartopy": (
        "Cartographic projections",
        "https://scitools.org.uk/cartopy/docs/latest/",
    ),
    "fsspec": (
        "Filesystem abstraction layer",
        "https://filesystem-spec.readthedocs.io/",
    ),
    "gcsfs": (
        "Google Cloud Storage filesystem for fsspec",
        "https://gcsfs.readthedocs.io/",
    ),
    "zarr": (
        "Chunked compressed array storage",
        "https://zarr.readthedocs.io/",
    ),
    "netCDF4": (
        "NetCDF4 file format library",
        "https://unidata.github.io/netcdf4-python/",
    ),
    "cfgrib": (
        "GRIB engine for xarray",
        "https://github.com/ecmwf/cfgrib",
    ),
}


# Inline call-site annotations: substring -> short explanation.
# Inserted as a comment immediately before the line containing the
# substring (only the first occurrence in the file).
CALL_SITE_NOTES: dict[str, str] = {
    "cdsapi.Client(": (
        "cdsapi.Client(): reads ~/.cdsapirc, prepares an authenticated session"
    ),
    ".retrieve(": (
        "client.retrieve(): submits the request to CDS, returns a result handle"
    ),
    "xr.open_dataset(": (
        "xr.open_dataset(): lazy-load NetCDF or GRIB into an xarray.Dataset"
    ),
    "xr.open_zarr(": (
        "xr.open_zarr(): lazy-open a Zarr store; bytes flow only when reduced"
    ),
    "requests.get(": (
        "requests.get(): blocking HTTP GET; .raise_for_status() throws on 4xx/5xx"
    ),
}


def annotate(slug: str, config: dict) -> str:
    """Return the standalone snippet with a references block prepended.

    Args:
        slug: Dataset slug (e.g. ``"era5-single-levels"``).
        config: Form config dict, same shape passed to ``standalone_snippet``.

    Returns:
        Annotated Python source ready for display or notebook embedding.
    """
    base = standalone_snippet(slug, config)
    refs_block = _references_block(base)
    annotated = _insert_call_site_notes(base)
    return _splice_after_module_docstring(annotated, refs_block)


def _references_block(text: str) -> str:
    """Build a `# References:` comment block listing libraries used in text."""
    used = _detect_libraries(text)
    if not used:
        return ""

    lines = [
        "# " + "=" * 64,
        "# Libraries used in this script (click for docs):",
        "# " + "=" * 64,
    ]
    width = max(len(name) for name in used)
    for name in used:
        desc, url = LIBRARY_DOCS[name]
        lines.append(f"# {name:<{width}}  {desc}")
        lines.append(f"# {' ' * width}  -> {url}")
    lines.append("# " + "=" * 64)
    return "\n".join(lines) + "\n\n"


def _detect_libraries(text: str) -> list[str]:
    """Return the libraries from LIBRARY_DOCS imported by ``text``, in order."""
    found: list[str] = []
    seen: set[str] = set()
    # Match `import X`, `import X as Y`, `from X import ...`, `from X.Y import ...`
    pattern = re.compile(
        r"^\s*(?:import\s+([\w.]+)(?:\s+as\s+\w+)?|from\s+([\w.]+)\s+import)",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        name = match.group(1) or match.group(2)
        # Try the full dotted name first, then the top-level package
        for candidate in (name, name.split(".")[0]):
            if candidate in LIBRARY_DOCS and candidate not in seen:
                found.append(candidate)
                seen.add(candidate)
                break
    return found


def _insert_call_site_notes(text: str) -> str:
    """Prepend a one-line `# note` above the first real Call for each pattern.

    Uses ast to walk Call nodes so docstring or comment text mentioning
    e.g. ``.retrieve(`` does not get falsely matched.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text

    # Map pattern -> sorted list of line numbers (1-indexed) where it really fires
    call_lines: dict[str, list[int]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for sig in _call_signatures(node):
            call_lines.setdefault(sig, []).append(node.lineno)
    for sig in call_lines:
        call_lines[sig].sort()

    lines = text.split("\n")
    inserts: dict[int, str] = {}
    for needle, note in CALL_SITE_NOTES.items():
        targets = call_lines.get(needle)
        if not targets:
            continue
        line_idx = targets[0] - 1  # convert to 0-indexed
        if line_idx in inserts:
            continue  # already annotated by another pattern
        indent = lines[line_idx][: len(lines[line_idx]) - len(lines[line_idx].lstrip())]
        inserts[line_idx] = f"{indent}# {note}"

    if not inserts:
        return text
    out: list[str] = []
    for i, line in enumerate(lines):
        if i in inserts:
            out.append(inserts[i])
        out.append(line)
    return "\n".join(out)


def _call_signatures(call: ast.Call) -> set[str]:
    """Derive matching signatures for an ast.Call node.

    For ``cdsapi.Client(...)`` returns ``{"cdsapi.Client(", ".Client("}``.
    For ``client.retrieve(...)`` returns ``{"client.retrieve(", ".retrieve("}``.
    For ``open(...)`` returns ``{"open("}``.

    The CALL_SITE_NOTES table can be keyed by either the dotted form (when
    the receiver is a known module name) or the bare ``.attr(`` form
    (when the receiver is an arbitrary local variable).
    """
    fn = call.func
    sigs: set[str] = set()
    if isinstance(fn, ast.Attribute):
        sigs.add(f".{fn.attr}(")
        if isinstance(fn.value, ast.Name):
            sigs.add(f"{fn.value.id}.{fn.attr}(")
    elif isinstance(fn, ast.Name):
        sigs.add(f"{fn.id}(")
    return sigs


def _splice_after_module_docstring(text: str, block: str) -> str:
    """Insert ``block`` after the module docstring, before the imports.

    If the file has no module docstring, insert at the very top.
    """
    if not block:
        return text
    # Find the end of the module docstring (triple-quoted string at top)
    match = re.match(r'^(\s*"""[\s\S]*?"""\s*\n)', text)
    if match:
        return text[: match.end()] + "\n" + block + text[match.end():]
    return block + text
