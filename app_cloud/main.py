"""Streamlit entry point for the cloud-hosted education-first variant.

Launch with::

    streamlit run app_cloud/main.py

Imports from ``app/`` are read-only. The desktop app at ``app/main.py``
is the canonical local experience and is never edited from here.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st  # noqa: E402

from app.dataset_pages import (  # noqa: E402
    DATASET_INFO,
    DATASETS,
)
from app.dataset_pages import learn as recipes_page  # noqa: E402
from app_cloud import gating  # noqa: E402
from app_cloud.code_annotator import annotate  # noqa: E402
from app_cloud.learn import PAGES as LEARN_PAGES  # noqa: E402
from app_cloud.nav import render_sidebar  # noqa: E402
from app_cloud.notebook_builder import (  # noqa: E402
    PLOT_LABELS,
    available_plots,
    build_notebook,
    build_script,
)


_DOWNLOAD_DATASETS = {k: v for k, v in DATASETS.items() if k != "home"}


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
    st.markdown(
        "Short, plain-English answers to the questions that come up the "
        "first time you try to use a climate dataset. No prior coding "
        "knowledge assumed. Each page links out to authoritative sources "
        "for depth."
    )

    descriptions = {
        "what-is-python-jupyter": (
            "Python is the language. Jupyter is the notebook format. "
            "How to install both and open a `.ipynb` file."
        ),
        "what-is-module": (
            "Why every script starts with `import xarray as xr` and what "
            "you have to do once before that line works."
        ),
        "what-is-api": (
            "What an API call to the Copernicus CDS actually looks like, "
            "why it needs a key, and how to set one up."
        ),
    }

    for key, (label, _module) in LEARN_PAGES.items():
        with st.container(border=True):
            c_text, c_action = st.columns([4, 1])
            with c_text:
                st.markdown(f"**{label}**")
                st.caption(descriptions.get(key, ""))
            with c_action:
                st.button(
                    ":material/arrow_forward: Open",
                    key=f"learn_open_{key}",
                    use_container_width=True,
                    type="primary",
                    on_click=_select_learn_page,
                    args=(key,),
                )

    st.divider()
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
    st.markdown(
        "Pick a dataset, configure the request, choose the plots you want. "
        "The app gives you a Jupyter notebook (`.ipynb`) and a Python "
        "script (`.py`) - both fully self-contained, ready to run on your "
        "own machine."
    )

    slugs = list(_DOWNLOAD_DATASETS.keys())
    slug = st.selectbox(
        "Dataset",
        slugs,
        format_func=lambda s: _DOWNLOAD_DATASETS[s][0],
        key="build_slug",
    )
    name, module = _DOWNLOAD_DATASETS[slug]

    info = DATASET_INFO.get(slug, "")
    if info:
        st.caption(info)

    if not gating.is_open_access(slug):
        st.info(
            ":material/key: This dataset needs your own API key to "
            "download live (see the **Learn > What is an API?** page for "
            "how to set one up). The notebook will still be generated; "
            "you'll run it on your own machine after configuring the key."
        )

    st.subheader("Configure the download")
    if hasattr(module, "render_mode_selector"):
        module.render_mode_selector()
    config = module.render_form()

    st.subheader("Pick plots to include")
    plots = available_plots(slug)
    if not plots:
        st.caption(
            "No automatic plots for this dataset yet - the notebook will "
            "still include the download and load cells. Add your own plots "
            "after."
        )
        plot_choices: list[str] = []
    else:
        plot_choices = st.multiselect(
            "Plots",
            plots,
            default=plots,
            format_func=lambda p: PLOT_LABELS.get(p, p),
            key="build_plots",
        )

    st.subheader("Preview the download cell")
    with st.expander("Show generated download code"):
        st.code(annotate(slug, config), language="python")

    st.subheader("Download")
    nb_bytes = build_notebook(slug, config, plot_choices, name, info)
    py_text = build_script(slug, config, plot_choices, name, info)

    c1, c2 = st.columns(2)
    base = slug.replace("-", "_")
    c1.download_button(
        ":material/file_download: Download .ipynb",
        data=nb_bytes,
        file_name=f"{base}_quickstart.ipynb",
        mime="application/x-ipynb+json",
        use_container_width=True,
        type="primary",
    )
    c2.download_button(
        ":material/file_download: Download .py",
        data=py_text.encode("utf-8"),
        file_name=f"{base}_quickstart.py",
        mime="text/x-python",
        use_container_width=True,
    )


# ── Browse datasets ──────────────────────────────────────────────────


def _render_datasets_browser() -> None:
    st.title(":material/dataset: Browse datasets")
    st.markdown(
        "All 19 datasets in the toolkit. Open-access datasets work in any "
        "build of this app; credentialed datasets show the live download "
        "code so you can run it locally with your own key."
    )

    open_count = sum(1 for s in _DOWNLOAD_DATASETS if gating.is_open_access(s))
    cred_count = len(_DOWNLOAD_DATASETS) - open_count
    c1, c2 = st.columns(2)
    c1.metric("Open access", open_count, border=True)
    c2.metric("Needs credentials", cred_count, border=True)

    for slug, (name, _module) in _DOWNLOAD_DATASETS.items():
        with st.container(border=True):
            c_text, c_badge = st.columns([4, 1])
            with c_text:
                st.markdown(f"**{name}**")
                st.caption(DATASET_INFO.get(slug, ""))
                st.caption(f"`docs/{slug}/README.md`")
            with c_badge:
                if gating.is_open_access(slug):
                    st.badge("Open access", icon=":material/lock_open:", color="green")
                else:
                    st.badge("Needs key", icon=":material/key:", color="orange")


main()
