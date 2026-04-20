"""Streamlit app for the climate data quickstart toolkit.

Runs entirely on the user's local machine. Credentials never pass
through the app; they are read by the underlying library clients
(``cdsapi``, ``requests`` + ``~/.netrc``) exactly as they would when
scripts are invoked from the command line.

Entry point: ``app/main.py``. Launch via the ``run_app.bat`` /
``run_app.sh`` shortcut.
"""
