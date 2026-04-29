"""Streamlit entry point for the hosted researcher preview.

Launch with::

    streamlit run app_cloud/main.py

Audience: Python-fluent researchers and analysts who want to skip the
``cdsapi`` boilerplate and grab a runnable notebook or script. Educational
scaffolding for absolute beginners is out of scope here and lives in a
separate repo.

Imports from ``app/`` are read-only. The desktop app at ``app/main.py``
is the canonical local experience and is never edited from here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st  # noqa: E402

from app.dataset_pages import (  # noqa: E402
    CATEGORIES,
    DATASET_INFO,
    DATASETS,
)
from app.dataset_pages import learn as recipes_page  # noqa: E402
from app_cloud import gating  # noqa: E402
from app_cloud.code_annotator import annotate as _annotate  # noqa: E402
from app_cloud.licences import licence_for  # noqa: E402
from app_cloud.nav import render_sidebar  # noqa: E402
from app_cloud.notebook_builder import (  # noqa: E402
    PLOT_LABELS,
    available_plots,
    build_notebook as _build_notebook,
    build_script as _build_script,
)


_DOWNLOAD_DATASETS = {k: v for k, v in DATASETS.items() if k != "home"}


# ── Cached builder wrappers ──────────────────────────────────────────
#
# Streamlit reruns the whole script on every widget interaction. The
# notebook builder reads scripts/{slug}_download.py, AST-parses it,
# applies transforms, and then assembles cells. None of that is heavy
# in absolute terms but it adds visible jank when the user is toggling
# pills. Caching by (slug, config_json, plot_choices) collapses the
# common rerun path to a dict lookup.


@st.cache_data(show_spinner=False)
def _annotated_snippet(slug: str, config_json: str) -> str:
    return _annotate(slug, json.loads(config_json))


@st.cache_data(show_spinner=False)
def _notebook_bytes(
    slug: str, config_json: str, plot_choices: tuple[str, ...],
    name: str, info: str,
) -> bytes:
    return _build_notebook(
        slug, json.loads(config_json), list(plot_choices), name, info,
    )


@st.cache_data(show_spinner=False)
def _script_text(
    slug: str, config_json: str, plot_choices: tuple[str, ...],
    name: str, info: str,
) -> str:
    return _build_script(
        slug, json.loads(config_json), list(plot_choices), name, info,
    )


def _config_key(config: dict[str, Any]) -> str:
    """Deterministic JSON for cache keying. Falls back to repr for non-JSON types."""
    try:
        return json.dumps(config, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return repr(sorted(config.items()))


# ── Entry ────────────────────────────────────────────────────────────


def main() -> None:
    st.set_page_config(
        page_title="Climate data quickstart - hosted preview",
        page_icon=":material/cloud_download:",
        layout="wide",
    )

    mode = render_sidebar()

    if mode == "recipes":
        recipes_page.render_page()
    elif mode == "build":
        _render_build()
    elif mode == "datasets":
        _render_datasets_browser()
    else:
        recipes_page.render_page()


# ── Build a notebook ─────────────────────────────────────────────────


def _render_build() -> None:
    st.title(":material/auto_stories: Build a notebook")
    st.caption(
        "Pick a dataset, configure the request, choose the plots you "
        "want. The app gives you a Jupyter notebook (`.ipynb`) and a "
        "Python script (`.py`) - both fully self-contained, ready to "
        "run on your own machine with your own API keys."
    )

    # Step 1: dataset
    with st.container(border=True):
        st.markdown(":material/dataset: **1. Pick a dataset**")
        slug = _render_dataset_picker()
        name, module = _DOWNLOAD_DATASETS[slug]
        info = DATASET_INFO.get(slug, "")
        if info:
            st.caption(info)
        if not gating.is_open_access(slug):
            st.caption(
                ":material/key: This dataset needs your own API key to "
                "download live. The notebook will still be generated; "
                "configure your key locally before running it."
            )

    # Step 2: configure the request
    with st.container(border=True):
        st.markdown(":material/tune: **2. Configure the request**")
        if hasattr(module, "render_mode_selector"):
            module.render_mode_selector()
        config = module.render_form()

    # Step 3: plots
    plots = available_plots(slug)
    with st.container(border=True):
        st.markdown(":material/insert_chart: **3. Pick plots to include**")
        if not plots:
            st.caption(
                "No automatic plots for this dataset yet. The notebook "
                "will still include the download and load cells - add your "
                "own plots after."
            )
            plot_choices: list[str] = []
        else:
            plot_choices = st.pills(
                "Plots",
                plots,
                default=plots,
                selection_mode="multi",
                format_func=lambda p: PLOT_LABELS.get(p, p),
                key="build_plots",
                label_visibility="collapsed",
            )

    # Step 4: preview + download
    config_json = _config_key(config)
    plot_choices_t = tuple(plot_choices)

    with st.container(border=True):
        st.markdown(":material/visibility: **4. Preview the download cell**")
        with st.expander("Show generated download code"):
            st.code(_annotated_snippet(slug, config_json), language="python")

    with st.container(border=True):
        st.markdown(":material/file_download: **5. Download**")
        st.caption(
            "Both files are equivalent. The `.ipynb` opens in Jupyter / "
            "Colab; the `.py` runs directly with `python`."
        )
        nb_bytes = _notebook_bytes(slug, config_json, plot_choices_t, name, info)
        py_text = _script_text(slug, config_json, plot_choices_t, name, info)
        base = slug.replace("-", "_")
        with st.container(horizontal=True, horizontal_alignment="distribute"):
            st.download_button(
                "Download notebook (.ipynb)",
                icon=":material/auto_stories:",
                data=nb_bytes,
                file_name=f"{base}_quickstart.ipynb",
                mime="application/x-ipynb+json",
                type="primary",
                use_container_width=True,
            )
            st.download_button(
                "Download script (.py)",
                icon=":material/code:",
                data=py_text.encode("utf-8"),
                file_name=f"{base}_quickstart.py",
                mime="text/x-python",
                use_container_width=True,
            )


def _render_dataset_picker() -> str:
    """Two-step picker: category pills + dataset radio within category."""
    cat_labels = list(CATEGORIES.keys())
    if "build_category" not in st.session_state:
        st.session_state["build_category"] = cat_labels[0]

    category = st.pills(
        "Category",
        cat_labels,
        format_func=lambda c: f"{CATEGORIES[c][0]} {c}",
        key="build_category",
        label_visibility="collapsed",
    )
    if not category:
        category = cat_labels[0]

    _icon, slugs = CATEGORIES[category]
    return st.radio(
        f"Dataset in {category}",
        slugs,
        format_func=lambda s: _DOWNLOAD_DATASETS[s][0],
        key=f"build_dataset_{category}",
        horizontal=False,
        label_visibility="collapsed",
    )


# ── Browse datasets ──────────────────────────────────────────────────


def _render_datasets_browser() -> None:
    st.title(":material/dataset: Browse datasets")
    st.caption(
        "All 19 datasets in the toolkit. Open-access datasets work in "
        "any deployment of this app; credentialed datasets show the live "
        "download code so you can run it locally with your own key. "
        "Each card lists the data licence."
    )

    open_count = sum(1 for s in _DOWNLOAD_DATASETS if gating.is_open_access(s))
    cred_count = len(_DOWNLOAD_DATASETS) - open_count
    m1, m2, m3 = st.columns(3)
    m1.metric("Total datasets", len(_DOWNLOAD_DATASETS), border=True)
    m2.metric("Open access", open_count, border=True)
    m3.metric("Needs credentials", cred_count, border=True)

    for cat_label, (cat_icon, slugs) in CATEGORIES.items():
        st.markdown(f"#### {cat_icon} {cat_label}")
        cols = st.columns(2)
        for i, slug in enumerate(slugs):
            name = _DOWNLOAD_DATASETS[slug][0]
            licence_label, licence_url = licence_for(slug)
            with cols[i % 2]:
                with st.container(border=True):
                    title_col, badge_col = st.columns([3, 1])
                    with title_col:
                        st.markdown(f"**{name}**")
                    with badge_col:
                        if gating.is_open_access(slug):
                            st.badge(
                                "Open",
                                icon=":material/lock_open:",
                                color="green",
                            )
                        else:
                            st.badge(
                                "Key",
                                icon=":material/key:",
                                color="orange",
                            )
                    st.caption(DATASET_INFO.get(slug, ""))
                    licence_md = (
                        f":material/balance: Licence: [{licence_label}]({licence_url})"
                        if licence_url else f":material/balance: Licence: {licence_label}"
                    )
                    st.caption(licence_md)
                    st.caption(f":material/menu_book: `docs/{slug}/README.md`")


main()
