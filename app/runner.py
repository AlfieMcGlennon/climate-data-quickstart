"""Dispatches a config dict to the right script's download() function.

The app never re-implements download logic. Each dataset has a module in
``scripts/`` with a ``download()`` entry point that takes keyword args;
this runner imports the module lazily (so a missing optional dependency
does not break the whole app) and calls download() with the provided
config.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any


def _module_for(slug: str) -> str:
    """Map a dataset slug to the corresponding script module name."""
    return f"scripts.{slug.replace('-', '_')}_download"


def run(slug: str, config: dict[str, Any]) -> Path:
    """Invoke the download function for a dataset slug with a config dict.

    Args:
        slug: Dataset slug (e.g., ``era5-single-levels``).
        config: Keyword arguments to pass to the dataset's ``download()``
            function. The caller is responsible for the dict's shape.

    Returns:
        Path to the downloaded file as returned by ``download()``.

    Raises:
        ImportError: If the dataset's script module cannot be imported.
        Whatever the dataset's ``download()`` itself raises.
    """
    module_name = _module_for(slug)
    module = importlib.import_module(module_name)
    download_fn = getattr(module, "download")
    clean = {k: v for k, v in config.items() if k != "chunked"}
    return download_fn(**clean)


def run_chunked(
    slug: str,
    config: dict[str, Any],
    progress_callback: Any | None = None,
) -> Path:
    """Invoke the chunked download function for a dataset slug.

    Falls back to run() if the dataset module has no download_chunked().

    Args:
        slug: Dataset slug.
        config: Full config dict including chunked options.
        progress_callback: Optional progress callback passed through.

    Returns:
        Path to the merged or output directory.
    """
    module_name = _module_for(slug)
    module = importlib.import_module(module_name)

    download_fn = getattr(module, "download_chunked", None)
    if download_fn is None:
        return run(slug, config)

    chunk_config = config.get("chunked") or {}
    clean = {k: v for k, v in config.items() if k != "chunked"}
    clean["chunk_by"] = chunk_config.get("chunk_by", "month")
    clean["max_retries"] = chunk_config.get("max_retries", 3)
    clean["merge_output"] = chunk_config.get("merge_output", True)
    clean["progress_callback"] = progress_callback

    return download_fn(**clean)
