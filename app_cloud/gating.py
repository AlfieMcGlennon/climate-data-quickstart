"""Cloud-mode dataset gating.

Decides whether a dataset's live download path can run on the public
cloud deployment. The rule is simple: any dataset that needs a private
credential is gated off and routed to the "code-only + cached sample"
panel instead of the live download flow.

We derive the open-access set from ``app.credentials.DATASET_REQUIREMENTS``
rather than hard-coding it, so adding a new dataset to the desktop app
automatically does the right thing here.
"""

from __future__ import annotations

from app.credentials import DATASET_REQUIREMENTS


def is_open_access(slug: str) -> bool:
    """True if this dataset can be downloaded from the cloud app live.

    A dataset is "open access" for the cloud app's purposes when it
    requires zero credentials. Any required credential at all (CDS,
    Earthdata, CEDA, EWDS, EDH) routes the user to the code-only panel.
    """
    return DATASET_REQUIREMENTS.get(slug, ()) == ()


OPEN_ACCESS_SLUGS: frozenset[str] = frozenset(
    slug for slug in DATASET_REQUIREMENTS if is_open_access(slug)
)
