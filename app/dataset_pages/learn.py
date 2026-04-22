"""Learn tab: guided recipes that answer climate questions with data.

Each recipe downloads open-access data, plots it interactively, and
shows the portable code underneath. The user tweaks widgets, the plot
updates, and the code block updates to match.
"""

from __future__ import annotations

import streamlit as st

from app.dataset_pages.recipes import RECIPES


_BADGE_COLORS = {
    "None": "green",
    "CDS API": "blue",
}


def render_page() -> None:
    """Render the Learn landing page or a selected recipe."""
    # If a recipe is selected, render it directly
    if "learn_recipe" in st.session_state and st.session_state["learn_recipe"]:
        recipe_id = st.session_state["learn_recipe"]
        recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)
        if recipe:
            # Back button
            if st.button(
                ":material/arrow_back: Back to recipes",
                key="learn_back",
                type="tertiary",
            ):
                st.session_state["learn_recipe"] = None
                st.rerun()
            recipe["module"].render_recipe()
            return

    # Landing page
    st.title(":material/school: Learn")
    st.markdown(
        "Guided recipes that answer real climate questions using datasets "
        "from this toolkit. Each recipe downloads data, plots it interactively, "
        "and gives you the code to reproduce it in your own scripts or notebooks."
    )
    st.markdown(
        "Recipes marked **No credentials** work immediately with no setup. "
        "Just pick one and run it."
    )

    # Recipe cards
    for recipe in RECIPES:
        with st.container(border=True):
            col_text, col_action = st.columns([4, 1])
            with col_text:
                st.markdown(f"**{recipe['title']}**")
                st.caption(recipe["description"])
                tag_col1, tag_col2, tag_col3 = st.columns(3)
                with tag_col1:
                    st.caption(f":material/dataset: {', '.join(recipe['datasets'])}")
                with tag_col2:
                    cred_color = _BADGE_COLORS.get(recipe["credentials"], "gray")
                    st.badge(
                        f"Credentials: {recipe['credentials']}",
                        color=cred_color,
                    )
                with tag_col3:
                    st.caption(f":material/schedule: {recipe['time']}")
            with col_action:
                st.button(
                    ":material/play_arrow: Run",
                    key=f"learn_{recipe['id']}",
                    use_container_width=True,
                    type="primary",
                    on_click=_select_recipe,
                    args=(recipe["id"],),
                )


def _select_recipe(recipe_id: str) -> None:
    """Callback: select a recipe to run."""
    st.session_state["learn_recipe"] = recipe_id
