"""Streamlit entry point for the climate data quickstart app.

Launch via ``run_app.bat`` / ``run_app.sh`` or manually with::

    streamlit run app/main.py

The app binds to ``localhost`` only. It never reads or stores credential
strings; it invokes the same ``scripts/*_download.download()`` functions
as the command-line route, which in turn call ``cdsapi.Client()`` and
``requests`` with the user's standard config files.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Ensure the repo root is on sys.path so ``scripts.*`` and ``common.*``
# imports resolve when streamlit launches this file directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st  # noqa: E402

from app import credentials  # noqa: E402
from app.dataset_pages import DATASETS  # noqa: E402
from app.forms import result_panel  # noqa: E402
from app.runner import run  # noqa: E402


def _render_sidebar() -> str:
    """Render the sidebar (dataset picker + credential status) and return slug."""
    st.sidebar.title("Climate data quickstart")
    st.sidebar.caption(
        "Local-only UI for the twelve datasets in the repo. Credentials "
        "stay on your machine."
    )

    slug = st.sidebar.selectbox(
        "Dataset",
        list(DATASETS.keys()),
        format_func=lambda s: DATASETS[s][0],
    )

    st.sidebar.divider()
    st.sidebar.subheader("Credential status")
    _render_credential_panel()

    st.sidebar.divider()
    st.sidebar.caption(
        "See `docs/{slug}/README.md` for each dataset's full reference."
    )
    return slug


def _render_credential_panel() -> None:
    statuses = credentials.all_statuses()
    labels = {
        "cds": "Copernicus CDS",
        "edh": "Earth Data Hub",
        "earthdata": "NASA Earthdata",
        "ceda": "CEDA",
        "ewds": "CEMS EWDS (GloFAS)",
    }
    for key, label in labels.items():
        status = statuses[key]
        icon = "[OK]" if status.configured else "[--]"
        with st.sidebar.expander(f"{icon} {label}", expanded=not status.configured):
            st.caption(f"Location: `{status.location}`")
            if not status.configured:
                st.caption(f"Register: {status.registration_url}")
                st.code(status.instructions, language="text")


def main() -> None:
    st.set_page_config(
        page_title="Climate data quickstart",
        layout="wide",
    )

    slug = _render_sidebar()
    name, module = DATASETS[slug]

    st.title(name)

    ready, missing = credentials.dataset_ready(slug)
    if missing:
        st.warning(
            "This dataset needs credentials that are not configured yet. "
            "Check the sidebar to see what to set up."
        )
        for m in missing:
            st.caption(f"- Missing: `{m.location}` (register at {m.registration_url})")

    # Render the dataset-specific form. The form returns the config dict
    # that feeds the download function.
    with st.form(key=f"form_{slug}"):
        config = module.render_form()

        # EDH is streaming-first. Show code snippet by default, download
        # only if the user explicitly asks for a file.
        if slug == "earth-data-hub":
            c1, c2 = st.columns(2)
            show_code = c1.form_submit_button(
                "Show streaming code",
                use_container_width=True,
                disabled=not ready,
            )
            download = c2.form_submit_button(
                "Download sliced data to file",
                use_container_width=True,
                disabled=not ready,
            )
            submitted = download
        else:
            submitted = st.form_submit_button(
                "Download",
                disabled=not ready,
                use_container_width=True,
            )
            show_code = False

    # Streaming code display for EDH, outside the form so it renders after
    # the buttons.
    if slug == "earth-data-hub" and (show_code or submitted):
        st.subheader("Streaming code snippet")
        st.caption(
            "Copy this into a notebook or script to work with the data lazily. "
            "Only the bytes you actually reduce or save flow over the network."
        )
        st.code(module.streaming_snippet(config), language="python")

    if submitted:
        _run_and_display(slug, config)


def _run_and_display(slug: str, config: dict) -> None:
    """Invoke the download and render the result panel."""
    status = st.empty()
    if slug == "earth-data-hub":
        status.info(
            "Streaming sliced bytes from Earth Data Hub. Time scales with "
            "how much data you asked for, not with a queue."
        )
    else:
        status.info(
            "Submitting request. CDS requests are queued server-side; direct "
            "downloads are usually immediate."
        )

    try:
        output_path = run(slug, config)
    except Exception as exc:
        status.empty()
        st.error(f"Download failed: {type(exc).__name__}: {exc}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc(), language="python")
        return

    status.empty()
    result_panel(output_path)


if __name__ == "__main__":
    main()
else:
    # Streamlit runs the file as a module; call main() unconditionally.
    main()
