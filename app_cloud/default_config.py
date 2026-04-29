"""Extract USER CONFIGURATION defaults from a canonical download script.

The Browse mode in ``app_cloud/main.py`` uses these defaults so a user
who hasn't filled out a form still gets a snippet that points to the
right output path, requests a sensible default variable, and runs out
of the box. Without this, a "default" notebook would mismatch its
download path against its plot cells.

Pure AST extraction. Keys are lowercased to match the form-config shape
that ``standalone_snippet`` and ``notebook_builder`` already accept
(e.g. ``VARIABLES`` -> ``variables``, ``OUTPUT_DIR`` -> ``output_dir``).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


def default_config(slug: str) -> dict[str, Any]:
    """Return the USER CONFIGURATION defaults from scripts/{slug}_download.py.

    Returns ``{}`` if the script is missing or has no USER CONFIGURATION
    block. Constants whose values aren't a Python literal (e.g. derived
    expressions) are skipped.
    """
    source_path = _SCRIPTS_DIR / f"{slug.replace('-', '_')}_download.py"
    if not source_path.exists():
        return {}
    text = source_path.read_text(encoding="utf-8")

    fence = _user_config_line_range(text)
    if fence is None:
        return {}
    fence_start, fence_end = fence

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}

    config: dict[str, Any] = {}
    for node in tree.body:
        target_name: str | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target_name = node.target.id
            value_node = node.value
        elif (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            target_name = node.targets[0].id
            value_node = node.value

        if target_name is None or value_node is None:
            continue
        if not (fence_start <= node.lineno <= fence_end):
            continue
        if target_name != target_name.upper():
            continue  # only constants
        try:
            value = ast.literal_eval(value_node)
        except (ValueError, SyntaxError):
            continue  # skip derived/non-literal values (e.g. None | str)
        config[target_name.lower()] = value

    return config


def _user_config_line_range(text: str) -> tuple[int, int] | None:
    """Return the 1-indexed line range of the USER CONFIGURATION block content.

    Mirrors ``app.standalone_script._user_config_line_range`` but inlined
    here to avoid coupling to an underscore-prefixed import.
    """
    start_match = re.search(r"^# USER CONFIGURATION[^\n]*$", text, re.MULTILINE)
    if not start_match:
        return None
    after_header_match = re.search(
        r"^# ={20,}$", text[start_match.end():], re.MULTILINE,
    )
    if not after_header_match:
        return None
    content_start = start_match.end() + after_header_match.end() + 1
    closing_match = re.search(
        r"^# ={20,}$", text[content_start:], re.MULTILINE,
    )
    if not closing_match:
        return None
    content_end = content_start + closing_match.start()
    start_line = text.count("\n", 0, content_start) + 1
    end_line = text.count("\n", 0, content_end)
    return start_line, end_line
