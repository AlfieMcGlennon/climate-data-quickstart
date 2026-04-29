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
    NavItem("learn", "Learn", "school"),
    NavItem("recipes", "Recipes", "menu_book"),
    NavItem("build", "Build a notebook", "auto_stories"),
    NavItem("datasets", "Browse datasets", "dataset"),
)


def render_sidebar() -> str:
    """Render the cloud-app sidebar and return the active mode key."""
    st.sidebar.markdown("## :material/cloud_download: Climate data quickstart")
    st.sidebar.caption(
        "Open data + open code. No credentials needed to learn the basics; "
        "the live download code is shown so you can run it locally with "
        "your own keys."
    )

    if "cloud_mode" not in st.session_state:
        valid = {item.key for item in NAV_ITEMS}
        url_mode = st.query_params.get("mode", "learn")
        st.session_state["cloud_mode"] = url_mode if url_mode in valid else "learn"

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

    st.sidebar.divider()
    st.sidebar.caption(
        ":material/info: This is the **cloud demo**. For full live "
        "downloads with your own API keys, run the desktop app locally - "
        "see the repo for setup."
    )
    st.sidebar.caption(
        "Repo: https://github.com/AlfieMcGlennon/climate-data-quickstart"
    )

    return current


def _set_mode(mode: str) -> None:
    st.session_state["cloud_mode"] = mode
