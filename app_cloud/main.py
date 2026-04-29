"""Streamlit entry point for the cloud-hosted education-first variant.

Launch with::

    streamlit run app_cloud/main.py

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
from app_cloud.learn import PAGES as LEARN_PAGES  # noqa: E402
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
#
# Lists/dicts in `config` aren't directly hashable for st.cache_data, so
# we serialise to canonical JSON at the call boundary. ``sort_keys`` is
# critical: dict iteration order would otherwise produce different cache
# keys for the same logical config.


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
        page_title="Climate data quickstart - learn",
        page_icon=":material/cloud_download:",
        layout="wide",
    )

    mode = render_sidebar()

    if mode == "learn":
        _render_learn_landing()
    elif mode == "recipes":
        recipes_page.render_page()
    elif mode == "build":
        _render_build()
    elif mode == "datasets":
        _render_datasets_browser()
    else:
        _render_learn_landing()


# ── Learn landing ────────────────────────────────────────────────────


_LEARN_DESCRIPTIONS: dict[str, str] = {
    "what-is-python-jupyter": (
        "Python is the language. Jupyter is the notebook format. How to "
        "install both and open a `.ipynb` file."
    ),
    "what-is-module": (
        "Why every script starts with `import xarray as xr` and what you "
        "have to do once before that line works."
    ),
    "what-is-api": (
        "What an API call to the Copernicus CDS actually looks like, why "
        "it needs a key, and how to set one up."
    ),
}


_LEARN_ICONS: dict[str, str] = {
    "what-is-python-jupyter": "code",
    "what-is-module": "extension",
    "what-is-api": "vpn_key",
}


def _render_learn_landing() -> None:
    """Top-level Learn page: cards linking to the educational sub-pages."""
    selected = st.session_state.get("cloud_learn_page")
    if selected and selected in LEARN_PAGES:
        if st.button(
            ":material/arrow_back: Back to Learn",
            key="learn_back",
            type="tertiary",
        ):
            st.session_state["cloud_learn_page"] = None
            st.rerun()
        _, module = LEARN_PAGES[selected]
        module.render_page()
        return

    st.title(":material/school: Learn")
    st.caption(
        "Plain-English answers to the questions that come up the first "
        "time you try to use a climate dataset. No prior coding "
        "knowledge assumed."
    )

    for key, (label, _module) in LEARN_PAGES.items():
        icon = _LEARN_ICONS.get(key, "menu_book")
        with st.container(border=True):
            c_icon, c_text, c_action = st.columns([1, 6, 2], vertical_alignment="center")
            with c_icon:
                st.markdown(
                    f"## :material/{icon}:",
                    unsafe_allow_html=False,
                )
            with c_text:
                st.markdown(f"**{label}**")
                st.caption(_LEARN_DESCRIPTIONS.get(key, ""))
            with c_action:
                st.button(
                    "Open",
                    icon=":material/arrow_forward:",
                    key=f"learn_open_{key}",
                    use_container_width=True,
                    type="primary",
                    on_click=_select_learn_page,
                    args=(key,),
                )

    st.caption(
        "Once you have read these, head to **Recipes** for hands-on "
        "walkthroughs that load real data and plot it, or **Build a "
        "notebook** to generate a `.ipynb` for a dataset and plot type "
        "of your choosing."
    )


def _select_learn_page(key: str) -> None:
    st.session_state["cloud_learn_page"] = key


# ── Build a notebook ─────────────────────────────────────────────────


def _render_build() -> None:
    st.title(":material/auto_stories: Build a notebook")
    st.caption(
        "Pick a dataset, configure the request, choose the plots you "
        "want. The app gives you a Jupyter notebook (`.ipynb`) and a "
        "Python script (`.py`) - both fully self-contained, ready to "
        "run on your own machine."
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
                "see the **Learn > What is an API?** page for setup."
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
        "All 19 datasets in the toolkit. Open-access datasets work in any "
        "build of this app; credentialed datasets show the live download "
        "code so you can run it locally with your own key."
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
                    st.caption(f":material/menu_book: `docs/{slug}/README.md`")


main()
