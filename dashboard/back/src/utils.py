import os
import pandas as pd
import folium
import streamlit as st

def _load_asset(subdir, filename):
    """Helper to load asset files."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir, "front", "asset", "style", subdir, filename)
    
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def load_html(filename):
    """Loads an HTML template from front/asset/style/html."""
    return _load_asset("html", filename)

def load_css(filename):
    """Loads a CSS file from front/asset/style/css."""
    return _load_asset("css", filename)

def render_metric_card(label, value, delta=None, color="green"):
    """Renders a metric card using external HTML template."""
    html_template = load_html("metric_card_simple.html")
    if not html_template:
        st.error("Metric card template missing")
        return

    # Replace placeholders
    card_html = html_template.replace("{label}", str(label)) \
                             .replace("{value}", str(value)) \
                             .replace("{delta}", str(delta) if delta else "") \
                             .replace("{color}", color)
    
    st.markdown(card_html.replace("\n", " ").strip(), unsafe_allow_html=True)

def get_status_color(status):
    """Returns a color hex code based on the vessel status."""
    if pd.isna(status):
        return "#9b59b6" # Amethyst Purple
    
    status = str(status).lower()
    
    if any(x in status for x in ["active", "operational", "running", "on_duty"]):
        return "#2ecc71" # Emerald Green
    elif any(x in status for x in ["berthed", "anchored", "docked"]):
        return "#3498db" # Peter River Blue
    elif any(x in status for x in ["inactive", "idle", "off_duty", "parked"]):
        return "#95a5a6" # Concrete Gray
    elif any(x in status for x in ["maintenance", "repair"]):
        return "#e67e22" # Carrot Orange
    elif any(x in status for x in ["warning", "alert", "slow"]):
        return "#f1c40f" # Sunflower Yellow
    elif any(x in status for x in ["emergency", "distress", "broken", "accident", "danger"]):
        return "#e74c3c" # Alizarin Red
    else:
        return "#9b59b6" # Default Purple

def create_google_arrow_icon(heading, fill_color, size=15):
    """Creates a rotated arrow icon SVG for Folium."""
    width = size * 2
    height = size * 2
    
    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));">
        <g transform="rotate({heading}, {width/2}, {height/2})">
             <path d="M {width/2},{0} L {width},{height} L {width/2},{height*0.75} L {0},{height} Z"
                   fill="{fill_color}" 
                   stroke="white" 
                   stroke-width="1.5"
                   stroke-linejoin="round"/>
             <circle cx="{width/2}" cy="{height*0.75}" r="{width*0.05}" fill="white" opacity="0.8"/>
        </g>
    </svg>
    """
    
    return folium.DivIcon(
        html=svg,
        icon_size=(width, height),
        icon_anchor=(width/2, height/2)
    )

def create_circle_icon(fill_color, size=10):
    """Creates a circle icon SVG for Folium."""
    diameter = size * 2
    svg = f"""
    <svg width="{diameter}" height="{diameter}" viewBox="0 0 {diameter} {diameter}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));">
        <circle cx="{diameter/2}" cy="{diameter/2}" r="{diameter/2-2}" 
                fill="{fill_color}" 
                stroke="white" 
                stroke-width="2"/>
    </svg>
    """
    return folium.DivIcon(
        html=svg,
        icon_size=(diameter, diameter),
        icon_anchor=(diameter/2, diameter/2)
    )
