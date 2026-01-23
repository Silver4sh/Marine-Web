import streamlit as st

# Peran Pengguna
ROLE_OPERATIONS = "Operations"
ROLE_MARCOM = "Marcom"
ROLE_ADMIN = "Admin"
ROLE_FINANCE = "Finance"

def load_css(file_name):
    """Memuat file CSS dari folder asset dashboard."""
    # Assuming standard path relative to dashboard/main.py execution
    # If config.py is in dashboard/, asset is in dashboard/front/asset or just asset?
    # Original 'back/src/utils.py' loaded form 'front/asset/css'
    # We will consolidate assets later, but for now let's assume 'assets/css' relative to main.
    try:
        with open(f"dashboard/assets/css/{file_name}") as f:
            return f.read()
    except FileNotFoundError:
        # Try alternate path if structure changes
        try:
             with open(f"assets/css/{file_name}") as f:
                return f.read()
        except:
             return None

def inject_custom_css():
    """Menyematkan gaya CSS global untuk dasbor."""
    css = load_css("global.css")
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
