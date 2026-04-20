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
    return download_fn(**config)
