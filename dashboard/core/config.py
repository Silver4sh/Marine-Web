import streamlit as st

# --- CONFIGURATION ---
ROLE_OPERATIONS = "Operations"
ROLE_MARCOM = "Marcom"
ROLE_ADMIN = "Admin"
ROLE_FINANCE = "Finance"

import os

def load_css(file_name):
    """Memuat file CSS dari folder asset dashboard."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        file_path = os.path.join(project_dir, "assets", "css", file_name)
        with open(file_path, "r", encoding="utf-8") as f: return f.read()
    except FileNotFoundError:
        return None

def inject_custom_css():
    """Menyematkan gaya CSS global untuk dasbor."""
    css = load_css("global.css")
    if css: st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
