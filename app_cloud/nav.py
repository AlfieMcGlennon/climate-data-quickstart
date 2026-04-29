"""Sidebar nav for the cloud-hosted app: Learn-first ordering."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    icon: str  # Material symbol name for `:material/...:` syntax


NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem("recipes", "Recipes", "menu_book"),
    NavItem("build", "Build a notebook", "auto_stories"),
    NavItem("datasets", "Browse datasets", "dataset"),
)


def render_sidebar() -> str:
    """Render the cloud-app sidebar and return the active mode key."""
    st.sidebar.markdown("## :material/cloud_download: Climate data quickstart")
    st.sidebar.caption(
        "Configure a request, grab the code, run it in your own notebook. "
        "Every snippet is fully self-contained: paste into any folder, "
        "`python file.py`, done."
    )

    if "cloud_mode" not in st.session_state:
        valid = {item.key for item in NAV_ITEMS}
        url_mode = st.query_params.get("mode", "recipes")
        st.session_state["cloud_mode"] = url_mode if url_mode in valid else "recipes"

    current = st.session_state["cloud_mode"]
    st.query_params["mode"] = current

    for item in NAV_ITEMS:
        st.sidebar.button(
            f":material/{item.icon}: {item.label}",
            key=f"nav_{item.key}",
            use_container_width=True,
            type="primary" if current == item.key else "tertiary",
            on_click=_set_mode,
            args=(item.key,),
        )

    with st.sidebar.expander(":material/help: How to use this", expanded=False):
        st.markdown(
            "1. **Browse datasets** to find what you need. Each card has a "
            "**Show default code** button - copy it or download the "
            "notebook directly.\n"
            "2. **Build a notebook** to customise the request "
            "(variables, dates, region) and pick plots before downloading.\n"
            "3. **Recipes** runs three worked examples in the browser to "
            "give you a feel for the kind of analysis these datasets "
            "support."
        )
        st.markdown(
            "**Credentials.** Open-access datasets (HadCET, HadCRUT5, "
            "CHIRPS, ARCO-ERA5, ESGF, ECMWF Open Data) need none. "
            "CDS, CEDA, EWDS, NASA Earthdata datasets need your own key - "
            "set up locally and run the downloaded code there."
        )

    st.sidebar.caption(
        "[Repo](https://github.com/AlfieMcGlennon/climate-data-quickstart) "
        "- MIT licensed"
    )

    return current


def _set_mode(mode: str) -> None:
    st.session_state["cloud_mode"] = mode
