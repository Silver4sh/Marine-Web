import streamlit as st

# --- CONFIGURATION ---
ROLE_OPERATIONS = "Operations"
ROLE_MARCOM = "Marcom"
ROLE_ADMIN = "Admin"
ROLE_FINANCE = "Finance"

def load_css(file_name):
    """Memuat file CSS dari folder asset dashboard."""
    try:
        with open(f"dashboard/assets/css/{file_name}") as f: return f.read()
    except FileNotFoundError:
        try:
             with open(f"assets/css/{file_name}") as f: return f.read()
        except: return None

def inject_custom_css():
    """Menyematkan gaya CSS global untuk dasbor."""
    css = load_css("global.css")
    if css: st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
