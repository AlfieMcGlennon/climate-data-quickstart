"""Per-dataset licence labels and links.

Sourced from the ``## Licence and attribution`` sections of each
``docs/{slug}/README.md``. Surfaced on the Browse cards so a researcher
can confirm a dataset's terms in one click before reusing it.

Tuple shape: ``(short label, public URL to canonical licence text)``.
A None URL is acceptable for licences that don't have a single
canonical link (e.g. mixed-source aggregations); the UI renders text
without a link in that case.
"""

from __future__ import annotations

# Canonical URLs reused below
_COPERNICUS_LICENCE = "https://apps.ecmwf.int/datasets/licences/copernicus/"
_OGL_V3 = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
_CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
_CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
_CMIP6_TERMS = "https://pcmdi.llnl.gov/CMIP6/TermsOfUse/TermsOfUse6-2.html"
_ECAD_POLICY = "https://www.ecad.eu/documents/ECAD_datapolicy.pdf"


# slug -> (label, url)
DATASET_LICENCES: dict[str, tuple[str, str | None]] = {
    "era5-single-levels": ("Copernicus Products licence", _COPERNICUS_LICENCE),
    "era5-pressure-levels": ("Copernicus Products licence", _COPERNICUS_LICENCE),
    "era5-land": ("Copernicus Products licence", _COPERNICUS_LICENCE),
    "era5-daily-stats": ("Copernicus Products licence", _COPERNICUS_LICENCE),
    "earth-data-hub": ("Copernicus Products licence (ERA5)", _COPERNICUS_LICENCE),
    "edh-explorer": ("Inherited per dataset (mostly Copernicus / CC BY 4.0)", _COPERNICUS_LICENCE),
    "arco-era5": ("CC BY 4.0", _CC_BY_4),
    "cmip6": ("CC BY 4.0 (most models)", _CMIP6_TERMS),
    "esgf-cmip6": ("CC BY 4.0", _CMIP6_TERMS),
    "c3s-seasonal": ("Copernicus Products licence", _COPERNICUS_LICENCE),
    "ukcp18": ("UK Open Government Licence v3.0", _OGL_V3),
    "hadcet": ("UK Open Government Licence", _OGL_V3),
    "hadcrut5": ("UK Open Government Licence", _OGL_V3),
    "ghcnd": ("Public domain (US Government work)", _CC0),
    "e-obs": ("ECA&D research/education only", _ECAD_POLICY),
    "chirps": ("Public domain", _CC0),
    "ecmwf-open-data": ("CC BY 4.0", _CC_BY_4),
    "glofas": ("Copernicus Products + CEMS terms", _COPERNICUS_LICENCE),
    "gpw-population": ("CC BY 4.0", _CC_BY_4),
}


def licence_for(slug: str) -> tuple[str, str | None]:
    """Return ``(label, url)`` for a dataset slug. Falls back to 'see docs'."""
    return DATASET_LICENCES.get(slug, ("see docs", None))
