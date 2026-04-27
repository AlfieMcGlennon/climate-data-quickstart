"""Generate fully standalone Python download snippets per dataset.

Reads the canonical ``scripts/{slug}_download.py`` source and applies a
small set of transforms so the result is copy-paste-runnable in any empty
folder with no dependency on this repo:

- Strip repo-bootstrap (``sys.path`` insert into ``REPO_ROOT``).
- Strip ``from common.X import ...`` lines and inline minimal definitions
  of any credential check the script actually uses.
- Strip ``download_chunked()`` and the chunked branch of ``__main__``;
  the standalone snippet is the simple single-request form.
- Replace USER CONFIGURATION block constants with the user's form values.
- Special-case ESGF multi-model mode by swapping ``__main__`` to call
  ``download_multi(...)`` with the chosen models.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


# Inline definitions of credential checks used across the scripts.
# These are intentionally short - the real common/credentials.py is more
# verbose with longer error messages, but a snippet user wants minimum
# code to read.
_INLINE_CHECKS: dict[str, str] = {
    "check_cds_credentials": '''def check_cds_credentials() -> Path:
    """Verify Copernicus CDS API credentials at ~/.cdsapirc."""
    path = Path.home() / ".cdsapirc"
    if not path.exists():
        raise FileNotFoundError(
            "CDS API credentials not found at ~/.cdsapirc.\\n"
            "Register at https://cds.climate.copernicus.eu and follow "
            "https://cds.climate.copernicus.eu/how-to-api to create the file."
        )
    return path
''',
    "check_netrc_entry": '''def check_netrc_entry(machine: str) -> Path:
    """Verify a netrc entry exists for a given host (~/.netrc or ~/_netrc)."""
    candidates = [Path.home() / ".netrc", Path.home() / "_netrc"]
    existing = [p for p in candidates if p.exists()]
    if not existing:
        raise FileNotFoundError(
            f"No netrc file found. Create ~/.netrc (Linux/macOS) or "
            f"~/_netrc (Windows) with an entry:\\n"
            f"  machine {machine}\\n"
            f"  login YOUR_USERNAME\\n"
            f"  password YOUR_PASSWORD_OR_TOKEN"
        )
    for path in existing:
        if f"machine {machine}" in path.read_text(encoding="utf-8", errors="ignore"):
            return path
    raise FileNotFoundError(
        f"netrc files exist but none has an entry for '{machine}'."
    )
''',
    "check_edh_token": '''def check_edh_token() -> str | None:
    """Verify an Earth Data Hub token is configured (env var or netrc)."""
    import os
    env_token = os.environ.get("EDH_API_KEY")
    if env_token:
        return env_token
    try:
        check_netrc_entry("data.earthdatahub.destine.eu")
        return None
    except FileNotFoundError:
        raise FileNotFoundError(
            "Earth Data Hub token not found. Set EDH_API_KEY env var or "
            "add a netrc entry for data.earthdatahub.destine.eu. "
            "Register at https://platform.destine.eu/."
        ) from None
''',
    "check_ewds_key": '''def check_ewds_key() -> str:
    """Return the EWDS API key from env var or ~/.ewdsapirc."""
    import os
    env_key = os.environ.get("EWDS_KEY")
    if env_key:
        return env_key
    for name in (".ewdsapirc", "_ewdsapirc"):
        path = Path.home() / name
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.strip().startswith("key:"):
                    return line.split(":", 1)[1].strip()
    raise FileNotFoundError(
        "EWDS key not found. Register at https://ewds.climate.copernicus.eu "
        "and save your token to ~/.ewdsapirc as 'key: YOUR_TOKEN', or set "
        "the EWDS_KEY environment variable."
    )
''',
    "check_ceda_token": '''def check_ceda_token() -> str:
    """Verify a CEDA bearer token (env var CEDA_TOKEN or ~/.ceda_token)."""
    import os
    env_token = os.environ.get("CEDA_TOKEN")
    if env_token:
        return env_token
    path = Path.home() / ".ceda_token"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(
        "CEDA token not found. Set CEDA_TOKEN env var or save it to "
        "~/.ceda_token. Generate one at "
        "https://services.ceda.ac.uk/api/token/create/."
    )
''',
}

# check_edh_token uses check_netrc_entry, so pulling one drags in the other.
_CHECK_DEPENDENCIES: dict[str, list[str]] = {
    "check_edh_token": ["check_netrc_entry"],
}


def standalone_snippet(slug: str, config: dict[str, Any]) -> str:
    """Build a fully standalone Python script for the given dataset + form config.

    Returns a string containing valid Python that the user can paste into
    an empty .py file or notebook cell, run with ``python file.py``, and
    have it work without any of this repo on disk.
    """
    source_path = _SCRIPTS_DIR / f"{slug.replace('-', '_')}_download.py"
    text = source_path.read_text(encoding="utf-8")

    text = _strip_repo_bootstrap(text)
    text, used_checks = _strip_credentials_imports(text)
    text = _strip_chunked_imports(text)
    text = _strip_download_chunked(text)
    text = _strip_chunked_main_branch(text)
    text = _replace_user_config(text, config)
    text = _inline_credential_defs(text, used_checks)

    if slug == "esgf-cmip6" and config.get("mode") == "multi":
        text = _swap_to_multi_main(text, config)

    text = _tidy_blank_lines(text)
    return text


# ── transform steps ───────────────────────────────────────────────────


def _strip_repo_bootstrap(text: str) -> str:
    """Remove ``REPO_ROOT = ...`` and ``sys.path.insert(...)``.

    Handles both the variant with the leading explanatory comment and
    the variant without.
    """
    text = re.sub(
        r"\n# Make ``common`` importable[^\n]*\n"
        r"REPO_ROOT = Path\(__file__\)\.resolve\(\)\.parent\.parent\n"
        r"sys\.path\.insert\(0, str\(REPO_ROOT\)\)\n",
        "\n",
        text,
    )
    text = re.sub(
        r"\nREPO_ROOT = Path\(__file__\)\.resolve\(\)\.parent\.parent\n"
        r"sys\.path\.insert\(0, str\(REPO_ROOT\)\)\n",
        "\n",
        text,
    )
    return text


def _strip_credentials_imports(text: str) -> tuple[str, set[str]]:
    """Remove ``from common.credentials import X`` (top-level + indented).

    Returns the stripped text and the set of imported names.
    """
    used: set[str] = set()
    pattern = re.compile(
        r"^[ \t]*from common\.credentials import ([\w, ]+?)(?:  # [^\n]*)?\n",
        re.MULTILINE,
    )

    def _capture(match: re.Match[str]) -> str:
        for name in match.group(1).split(","):
            used.add(name.strip())
        return ""

    return pattern.sub(_capture, text), used


def _strip_chunked_imports(text: str) -> str:
    """Remove the multi-line ``from common.chunked import (...)`` block."""
    return re.sub(
        r"\nfrom common\.chunked import \([^)]*\)[^\n]*\n",
        "\n",
        text,
        flags=re.DOTALL,
    )


def _strip_download_chunked(text: str) -> str:
    """Remove the entire ``def download_chunked(...): ...`` block."""
    start_match = re.search(r"^def download_chunked\(", text, re.MULTILINE)
    if not start_match:
        return text

    start = start_match.start()
    # Find next top-level statement after the start
    rest = text[start + 1:]
    next_match = re.search(
        r"^(?:def |class |if __name__|[A-Z_][A-Z0-9_]*\s*[:=])",
        rest,
        re.MULTILINE,
    )
    if not next_match:
        return text[:start].rstrip() + "\n"
    end = start + 1 + next_match.start()
    return text[:start] + text[end:]


def _strip_chunked_main_branch(text: str) -> str:
    """Collapse the ``--chunked`` branch in ``__main__`` to a plain call."""
    return re.sub(
        r'if "--chunked" in sys\.argv:\s*\n'
        r"[ \t]+path = download_chunked\(\)\s*\n"
        r"[ \t]+else:\s*\n"
        r"[ \t]+path = download\(\)",
        "path = download()",
        text,
    )


def _replace_user_config(text: str, config: dict[str, Any]) -> str:
    """Replace constants in the USER CONFIGURATION block with form values.

    Uses AST parsing so multi-line values (parenthesised string literals,
    lists, dicts) are handled correctly. Only assignments whose target
    is an upper-case name matching ``key.upper()`` for some form key get
    rewritten, and only those that fall inside the USER CONFIGURATION
    fence so module-level constants outside the block are left alone.
    """
    fence_lines = _user_config_line_range(text)
    if fence_lines is None:
        return text
    fence_start, fence_end = fence_lines

    targets = {
        key.upper(): value
        for key, value in config.items()
        if key not in ("chunked", "mode")
    }
    if not targets:
        return text

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text

    edits: list[tuple[int, int, str]] = []
    for node in tree.body:
        target_name: str | None = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target_name = node.target.id
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id

        if target_name is None or target_name not in targets:
            continue
        if not (fence_start <= node.lineno <= fence_end):
            continue
        end_lineno = node.end_lineno or node.lineno
        edits.append((node.lineno, end_lineno, f"{target_name} = {targets[target_name]!r}"))

    if not edits:
        return text

    lines = text.split("\n")
    # Apply in reverse so earlier line numbers remain valid.
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start - 1:end] = [replacement]
    return "\n".join(lines)


def _user_config_line_range(text: str) -> tuple[int, int] | None:
    """Return the 1-indexed line range of the USER CONFIGURATION block content."""
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


def _inline_credential_defs(text: str, used_checks: set[str]) -> str:
    """Insert inline definitions of credential checks above USER CONFIGURATION."""
    # Pull in transitive deps (e.g. check_edh_token -> check_netrc_entry)
    needed: set[str] = set()
    queue = list(used_checks)
    while queue:
        name = queue.pop()
        if name in needed:
            continue
        needed.add(name)
        for dep in _CHECK_DEPENDENCIES.get(name, []):
            queue.append(dep)

    bodies = [_INLINE_CHECKS[name] for name in needed if name in _INLINE_CHECKS]
    if not bodies:
        return text

    inserts = "\n\n".join(bodies)
    pattern = re.compile(r"^# ={20,}\n# USER CONFIGURATION", re.MULTILINE)
    match = pattern.search(text)
    if match:
        return text[:match.start()] + inserts + "\n\n" + text[match.start():]
    return inserts + "\n\n" + text


def _swap_to_multi_main(text: str, config: dict[str, Any]) -> str:
    """ESGF multi mode: rewrite ``__main__`` to call ``download_multi``.

    The single-model ``download()`` and search helpers stay defined; we
    only change the entry point so running the script downloads all
    chosen models.
    """
    kwargs = {
        "search_node": config.get("search_node", ""),
        "source_ids": config.get("source_ids", []),
        "experiment_id": config.get("experiment_id", ""),
        "variable_id": config.get("variable_id", ""),
        "table_id": config.get("table_id", ""),
        "n_members": config.get("n_members", 1),
        "grid_label": config.get("grid_label", "gn"),
        "output_dir": config.get("output_dir", "./data/esgf-cmip6"),
    }
    kwarg_block = "\n".join(f"        {k}={v!r}," for k, v in kwargs.items())
    new_main = (
        'if __name__ == "__main__":\n'
        "    paths = download_multi(\n"
        f"{kwarg_block}\n"
        "    )\n"
        "    for p in paths:\n"
        '        print(f"Downloaded: {p}")\n'
    )
    return re.sub(
        r'if __name__ == "__main__":[\s\S]*$',
        new_main,
        text,
    )


def _tidy_blank_lines(text: str) -> str:
    """Collapse runs of 3+ blank lines (left behind by stripping) to 2."""
    return re.sub(r"\n{4,}", "\n\n\n", text)
