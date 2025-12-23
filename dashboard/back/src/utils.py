import folium
import pandas as pd
import streamlit as st

def render_metric_card(label, value, delta=None, color="green"):
    """Renders a metric card using minified HTML."""
    card_html = f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <span style="font-size: 0.85rem; color: #94a3b8; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase;">
                {label}
            </span>
            <div style="width: 8px; height: 8px; border-radius: 50%; background-color: {color}; box-shadow: 0 0 10px {color};">
            </div>
        </div>
        <div style="font-size: 2.2rem; font-weight: 700; color: #e2e8f0; font-family: 'Inter', sans-serif; margin-bottom: 4px;">
            {value}
        </div>
        <div style="font-size: 0.85rem; display: flex; align-items: center; gap: 6px; color: #94a3b8;">
            <span style="color: {color}; background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 6px; font-weight: 600; font-family: monospace;">
                {delta if delta else ""}
            </span>
        </div>
    </div>
    """
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
