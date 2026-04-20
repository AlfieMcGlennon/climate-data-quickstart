"""Credential checks for the three access patterns used by datasets in this repo.

Every download script should call the appropriate check from this module before
attempting a data request. Each check raises ``FileNotFoundError`` with a message
pointing to the registration page if credentials are missing, so users get a
clear next step rather than a cryptic API error.

Patterns:
    A - Copernicus CDS API (``~/.cdsapirc``)
    B - Direct download, optionally via NASA Earthdata (``~/.netrc``)
    C - Custom Python API (Earth Data Hub via ``~/.netrc``, CEDA bearer token)
"""

from __future__ import annotations

import os
from pathlib import Path


def check_cds_credentials() -> Path:
    """Verify Copernicus CDS API credentials are configured.

    Returns:
        Path to the ``~/.cdsapirc`` file.

    Raises:
        FileNotFoundError: If ``~/.cdsapirc`` does not exist. Message includes
            the registration URL.
    """
    path = Path.home() / ".cdsapirc"
    if not path.exists():
        raise FileNotFoundError(
            "CDS API credentials not found at ~/.cdsapirc.\n"
            "Register at https://cds.climate.copernicus.eu and follow "
            "https://cds.climate.copernicus.eu/how-to-api to create the file."
        )
    return path


def check_netrc_entry(machine: str) -> Path:
    """Verify a netrc entry exists for a given host.

    Checks both ``~/.netrc`` (Linux/macOS convention) and ``~/_netrc``
    (Windows convention, since Windows File Explorer does not accept
    leading-dot filenames by default).

    Args:
        machine: Hostname to look for (e.g., ``urs.earthdata.nasa.gov``,
            ``data.earthdatahub.destine.eu``).

    Returns:
        Path to the netrc file that contains the matching entry.

    Raises:
        FileNotFoundError: If no netrc file exists or none of them has
            an entry for the given machine.
    """
    candidates = [Path.home() / ".netrc", Path.home() / "_netrc"]
    existing = [p for p in candidates if p.exists()]

    if not existing:
        raise FileNotFoundError(
            f"No netrc file found. This dataset needs an entry for '{machine}'.\n"
            "Create ~/.netrc (Linux/macOS) or ~/_netrc (Windows) with a block:\n"
            f"  machine {machine}\n"
            "  login YOUR_USERNAME\n"
            "  password YOUR_PASSWORD_OR_TOKEN\n"
            "For NASA Earthdata, register at https://urs.earthdata.nasa.gov/.\n"
            "For Earth Data Hub, register at https://platform.destine.eu/."
        )

    for path in existing:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if f"machine {machine}" in content:
            return path

    locations = ", ".join(str(p) for p in existing)
    raise FileNotFoundError(
        f"netrc file(s) found at {locations} but none has an entry for '{machine}'.\n"
        f"Add a block:\n"
        f"  machine {machine}\n"
        f"  login YOUR_USERNAME\n"
        f"  password YOUR_PASSWORD_OR_TOKEN"
    )


def check_edh_token() -> str | None:
    """Verify an Earth Data Hub access token is configured.

    EDH authenticates via ``~/.netrc`` or via the ``EDH_API_KEY``
    environment variable. This check prefers the env var, then falls
    back to verifying a ``~/.netrc`` entry exists for
    ``data.earthdatahub.destine.eu``.

    Returns:
        The token string if configured via ``EDH_API_KEY``; ``None`` if
        credentials are configured via ``~/.netrc`` (in which case they
        are read by the underlying HTTP client rather than returned
        here).

    Raises:
        FileNotFoundError: If no token is configured via either mechanism.
    """
    env_token = os.environ.get("EDH_API_KEY")
    if env_token:
        return env_token

    # Fall back to .netrc; check_netrc_entry raises if not present
    try:
        check_netrc_entry("data.earthdatahub.destine.eu")
        return None
    except FileNotFoundError:
        raise FileNotFoundError(
            "Earth Data Hub token not found.\n"
            "Either set the EDH_API_KEY environment variable or add an entry "
            "to ~/.netrc for machine 'data.earthdatahub.destine.eu'.\n"
            "Register at https://platform.destine.eu/ to obtain a token."
        ) from None


def check_ceda_token() -> str:
    """Verify a CEDA bearer token is configured.

    CEDA issues OAuth bearer tokens for programmatic access. This check prefers
    the ``CEDA_TOKEN`` environment variable, falling back to ``~/.ceda_token``.

    Returns:
        The token string.

    Raises:
        FileNotFoundError: If no token is configured.
    """
    env_token = os.environ.get("CEDA_TOKEN")
    if env_token:
        return env_token

    path = Path.home() / ".ceda_token"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()

    raise FileNotFoundError(
        "CEDA token not found.\n"
        "Set the CEDA_TOKEN environment variable or save the token to "
        "~/.ceda_token.\n"
        "Register at https://services.ceda.ac.uk/cedasite/register/info/ and "
        "generate a token at https://services.ceda.ac.uk/api/token/create/."
    )
