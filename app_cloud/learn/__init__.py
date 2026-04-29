"""Hand-written educational pages for the cloud-hosted app.

Each module exposes ``render_page()``. No LLM calls at runtime; copy is
written once, version-controlled, and links out to authoritative sources
for any depth.
"""

from . import what_is_api, what_is_module, what_is_python_jupyter

PAGES: dict[str, tuple[str, object]] = {
    "what-is-python-jupyter": (
        "What are Python and Jupyter?",
        what_is_python_jupyter,
    ),
    "what-is-module": (
        "What is a module / pip install?",
        what_is_module,
    ),
    "what-is-api": (
        "What is an API?",
        what_is_api,
    ),
}
