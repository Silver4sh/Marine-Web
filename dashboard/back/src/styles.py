import streamlit as st
from back.src.utils import load_css

def inject_custom_css():
    """Injects global CSS styles for the dashboard."""
    css = load_css("global.css")
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
