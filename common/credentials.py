"""Credential checks for the three access patterns used by datasets in this repo.

Every download script should call the appropriate check from this module before
attempting a data request. Each check raises ``FileNotFoundError`` with a message
pointing to the registration page if credentials are missing, so users get a
clear next step rather than a cryptic API error.

Patterns:
    A - Copernicus CDS API (``~/.cdsapirc``)
    B - Direct download, optionally via NASA Earthdata (``~/.netrc``)
    C - Custom Python API (Earth Data Hub token, CEDA bearer token)
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
    """Verify a ``~/.netrc`` entry exists for a given host.

    Used by datasets that authenticate via NASA Earthdata or similar services
    that read credentials from ``~/.netrc``.

    Args:
        machine: Hostname to look for (e.g., ``urs.earthdata.nasa.gov``).

    Returns:
        Path to the ``~/.netrc`` file.

    Raises:
        FileNotFoundError: If ``~/.netrc`` does not exist or has no entry for
            the given machine.
    """
    path = Path.home() / ".netrc"
    if not path.exists():
        raise FileNotFoundError(
            f"~/.netrc not found. This dataset needs an entry for '{machine}'.\n"
            "For NASA Earthdata, register at https://urs.earthdata.nasa.gov/ "
            "and follow https://disc.gsfc.nasa.gov/data-access#mac_linux_wget "
            "to set up ~/.netrc."
        )

    # Read without parsing credentials, just check machine line is present
    content = path.read_text(encoding="utf-8", errors="ignore")
    if f"machine {machine}" not in content:
        raise FileNotFoundError(
            f"~/.netrc exists but has no entry for '{machine}'.\n"
            f"Add a block:\n"
            f"  machine {machine}\n"
            f"  login YOUR_USERNAME\n"
            f"  password YOUR_PASSWORD"
        )
    return path


def check_edh_token() -> str:
    """Verify an Earth Data Hub access token is configured.

    Earth Data Hub uses an environment variable or a token file. This check
    prefers the ``EDH_API_KEY`` environment variable, falling back to
    ``~/.edh_token`` if set.

    Returns:
        The token string.

    Raises:
        FileNotFoundError: If no token is configured via either mechanism.
    """
    env_token = os.environ.get("EDH_API_KEY")
    if env_token:
        return env_token

    path = Path.home() / ".edh_token"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()

    raise FileNotFoundError(
        "Earth Data Hub token not found.\n"
        "Set the EDH_API_KEY environment variable or save the token to "
        "~/.edh_token.\n"
        "Register at https://earthdatahub.destine.eu/ to obtain a token."
    )


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
