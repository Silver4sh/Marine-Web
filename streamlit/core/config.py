"""
core/config.py
==============
Application-wide constants and CSS injection helper.
This file was recreated after the original was accidentally deleted.
"""
import os
import streamlit as st

# ── Role constants ────────────────────────────────────────────────────────────
ROLE_ADMIN      = "Admin"
ROLE_OPERATIONS = "Operations"
ROLE_MARCOM     = "MarCom"
ROLE_FINANCE    = "Finance"

ALL_ROLES = [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE]

# ── Asset paths ───────────────────────────────────────────────────────────────
_BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CSS_DIR   = os.path.join(_BASE_DIR, "assets", "css")
_HTML_DIR  = os.path.join(_BASE_DIR, "assets", "html")


def _load_css(filename: str) -> str:
    """Read a CSS file from assets/css/ and return its content."""
    path = os.path.join(_CSS_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def inject_custom_css():
    """
    Inject all global CSS stylesheets into the Streamlit page.
    Call once per render cycle (it is idempotent via Streamlit's markdown cache).
    """
    # Load CSS files in priority order
    css_files = ["style.css", "loader.css", "map_style.css", "map.css", "global.css"]
    combined = "\n".join(_load_css(f) for f in css_files)

    if combined.strip():
        st.markdown(f"<style>{combined}</style>", unsafe_allow_html=True)
