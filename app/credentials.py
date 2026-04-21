"""Credential status for the Streamlit app sidebar.

This module does NOT read or store any credential string. It only checks
whether the appropriate configuration files or environment variables
exist, and returns a structured status report the sidebar can render.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CredentialStatus:
    """Result of a single credential check.

    Attributes:
        configured: True if the credential appears to be set up.
        location: Human-readable description of where the credential lives.
        registration_url: Where to sign up if it is not yet configured.
        instructions: One-sentence prompt telling the user what to do next.
    """

    configured: bool
    location: str
    registration_url: str
    instructions: str


def _netrc_paths() -> list[Path]:
    """Return the candidate netrc paths for the current OS.

    Unix-like systems use ``~/.netrc``. Windows uses ``~/_netrc`` because
    File Explorer has historically refused leading-dot filenames. We
    check both on every platform since users sometimes port config
    between environments.
    """
    home = Path.home()
    return [home / ".netrc", home / "_netrc"]


def _netrc_has(machine: str) -> bool:
    for path in _netrc_paths():
        if not path.exists():
            continue
        try:
            if f"machine {machine}" in path.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def _netrc_location_hint() -> str:
    """Return a friendly, user-agnostic description of the netrc file."""
    for path in _netrc_paths():
        if path.exists():
            return f"~/{path.name}"
    return "~/_netrc" if Path.home().drive else "~/.netrc"


def check_cds() -> CredentialStatus:
    """Check Copernicus CDS API credentials (~/.cdsapirc)."""
    path = Path.home() / ".cdsapirc"
    return CredentialStatus(
        configured=path.exists(),
        location="~/.cdsapirc",
        registration_url="https://cds.climate.copernicus.eu/",
        instructions=(
            "Register at the URL above, accept the licence for the dataset "
            "you want, then create ~/.cdsapirc with two lines:\n"
            "  url: https://cds.climate.copernicus.eu/api\n"
            "  key: <your personal access token>"
        ),
    )


def check_earthdata() -> CredentialStatus:
    """Check NASA Earthdata credentials (netrc entry)."""
    configured = _netrc_has("urs.earthdata.nasa.gov")
    return CredentialStatus(
        configured=configured,
        location=(
            f"{_netrc_location_hint()} (entry for urs.earthdata.nasa.gov)"
        ),
        registration_url="https://urs.earthdata.nasa.gov/",
        instructions=(
            "Register at the URL above, then add a block to your netrc file\n"
            "(~/.netrc on Linux/macOS, ~/_netrc on Windows):\n"
            "  machine urs.earthdata.nasa.gov\n"
            "  login YOUR_USERNAME\n"
            "  password YOUR_PASSWORD"
        ),
    )


def check_edh() -> CredentialStatus:
    """Check Earth Data Hub credentials (netrc entry or env var)."""
    via_env = bool(os.environ.get("EDH_API_KEY"))
    via_netrc = _netrc_has("data.earthdatahub.destine.eu")
    return CredentialStatus(
        configured=via_env or via_netrc,
        location=(
            "EDH_API_KEY env var"
            if via_env
            else f"{_netrc_location_hint()} (entry for data.earthdatahub.destine.eu)"
        ),
        registration_url="https://platform.destine.eu/",
        instructions=(
            "Register at the URL above, generate a Personal Access Token in "
            "Earth Data Hub settings, then add a block to your netrc file\n"
            "(~/.netrc on Linux/macOS, ~/_netrc on Windows):\n"
            "  machine data.earthdatahub.destine.eu\n"
            "  login your-destine-username\n"
            "  password YOUR_TOKEN"
        ),
    )


def check_ceda() -> CredentialStatus:
    """Check CEDA bearer token (env var or ~/.ceda_token)."""
    via_env = bool(os.environ.get("CEDA_TOKEN"))
    path = Path.home() / ".ceda_token"
    return CredentialStatus(
        configured=via_env or path.exists(),
        location="CEDA_TOKEN env var" if via_env else "~/.ceda_token",
        registration_url="https://services.ceda.ac.uk/cedasite/register/info/",
        instructions=(
            "Register at the URL above, generate a bearer token at "
            "https://services.ceda.ac.uk/api/token/create/, then either set "
            "the CEDA_TOKEN environment variable or save the token to "
            "~/.ceda_token."
        ),
    )


def check_ewds() -> CredentialStatus:
    """Check Copernicus CEMS EWDS credentials (EWDS_KEY env var)."""
    return CredentialStatus(
        configured=bool(os.environ.get("EWDS_KEY")),
        location="EWDS_KEY environment variable",
        registration_url="https://ewds.climate.copernicus.eu/",
        instructions=(
            "Register at the URL above (separate account from the main CDS), "
            "accept the GloFAS licence, copy your Personal Access Token, "
            "and export it:\n"
            "  export EWDS_KEY=<your-token>"
        ),
    )


# Map of dataset slug -> required credential key (as returned by _all)
DATASET_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "era5-single-levels": ("cds",),
    "era5-pressure-levels": ("cds",),
    "era5-land": ("cds",),
    "era5-daily-stats": ("cds",),
    "earth-data-hub": ("edh",),
    "hadcet": (),
    "hadcrut5": (),
    "cmip6": ("cds",),
    "ukcp18": ("ceda",),
    "glofas": ("ewds",),
    "ghcnd": (),
    "e-obs": ("cds",),
    "gpw-population": ("earthdata",),
    "chirps": (),
    "ecmwf-open-data": (),
    "c3s-seasonal": ("cds",),
    "arco-era5": (),
    "edh-explorer": ("edh",),
    "esgf-cmip6": (),
}


def all_statuses() -> dict[str, CredentialStatus]:
    """Return the full credential-status report keyed by short name."""
    return {
        "cds": check_cds(),
        "edh": check_edh(),
        "earthdata": check_earthdata(),
        "ceda": check_ceda(),
        "ewds": check_ewds(),
    }


def dataset_ready(slug: str) -> tuple[bool, list[CredentialStatus]]:
    """Report whether a dataset can be downloaded, plus any missing creds.

    Args:
        slug: Dataset slug as used in docs/ and scripts/.

    Returns:
        (ready, missing): ``ready`` is True iff all required credentials
        are configured. ``missing`` is the list of ``CredentialStatus``
        objects for the required credentials that are not configured.
    """
    statuses = all_statuses()
    required = DATASET_REQUIREMENTS.get(slug, ())
    missing = [statuses[k] for k in required if not statuses[k].configured]
    return (len(missing) == 0, missing)
