"""Recipe registry for the Learn tab.

Each recipe module exposes:
- TITLE: str - the question the recipe answers
- DESCRIPTION: str - one-line summary
- DATASETS_USED: list[str] - human-readable dataset names
- CREDENTIALS: str - "none" or description of what's needed
- ESTIMATED_TIME: str - "instant" or "1-2 min" etc.
- render_recipe() -> None - renders the full recipe in Streamlit
"""

from __future__ import annotations

from . import hadcet_record, hadcrut5_trend, spatial_maps

RECIPES: list[dict] = [
    {
        "id": "hadcet_record",
        "title": hadcet_record.TITLE,
        "description": hadcet_record.DESCRIPTION,
        "datasets": hadcet_record.DATASETS_USED,
        "credentials": hadcet_record.CREDENTIALS,
        "time": hadcet_record.ESTIMATED_TIME,
        "module": hadcet_record,
    },
    {
        "id": "hadcrut5_trend",
        "title": hadcrut5_trend.TITLE,
        "description": hadcrut5_trend.DESCRIPTION,
        "datasets": hadcrut5_trend.DATASETS_USED,
        "credentials": hadcrut5_trend.CREDENTIALS,
        "time": hadcrut5_trend.ESTIMATED_TIME,
        "module": hadcrut5_trend,
    },
    {
        "id": "spatial_maps",
        "title": spatial_maps.TITLE,
        "description": spatial_maps.DESCRIPTION,
        "datasets": spatial_maps.DATASETS_USED,
        "credentials": spatial_maps.CREDENTIALS,
        "time": spatial_maps.ESTIMATED_TIME,
        "module": spatial_maps,
    },
]
