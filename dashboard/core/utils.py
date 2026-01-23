import streamlit as st
import pandas as pd
import folium
from dashboard.core_pkg.config import load_css

def load_html(filename):
    """Memuat template HTML dari folder assets."""
    try:
        with open(f"dashboard/assets/html/{filename}", "r", encoding="utf-8") as f: return f.read()
    except FileNotFoundError:
        try:
             with open(f"assets/html/{filename}", "r", encoding="utf-8") as f: return f.read()
        except: return ""

def render_metric_card(label, value, delta=None, color="green"):
    """Merender kartu metrik."""
    html_template = load_html("metric_card_simple.html")
    if not html_template:
        st.error("Template kartu metrik hilang")
        return

    card_html = html_template.replace("{label}", str(label)) \
                             .replace("{value}", str(value)) \
                             .replace("{delta}", str(delta) if delta else "") \
                             .replace("{color}", color)
    st.markdown(card_html.replace("\n", " ").strip(), unsafe_allow_html=True)

def get_status_color(status):
    """Mengembalikan kode hex warna berdasarkan status kapal."""
    if pd.isna(status): return "#9b59b6"
    status = str(status).lower()
    if any(x in status for x in ["active", "operational", "running", "on_duty", "operating"]): return "#2ecc71"
    elif any(x in status for x in ["berthed", "anchored", "docked"]): return "#3498db"
    elif any(x in status for x in ["inactive", "idle", "off_duty", "parked"]): return "#95a5a6"
    elif any(x in status for x in ["maintenance", "repair", "mtc"]): return "#e67e22"
    elif any(x in status for x in ["warning", "alert", "slow"]): return "#f1c40f"
    elif any(x in status for x in ["emergency", "distress", "broken", "accident", "danger"]): return "#e74c3c"
    else: return "#9b59b6"

def create_google_arrow_icon(heading, fill_color, size=15):
    """Membuat ikon panah berputar."""
    width = size * 2
    height = size * 2
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><g transform="rotate({heading}, {width/2}, {height/2})"><path d="M {width/2},{0} L {width},{height} L {width/2},{height*0.75} L {0},{height} Z" fill="{fill_color}" stroke="white" stroke-width="1.5" stroke-linejoin="round"/><circle cx="{width/2}" cy="{height*0.75}" r="{width*0.05}" fill="white" opacity="0.8"/></g></svg>"""
    return folium.DivIcon(html=svg, icon_size=(width, height), icon_anchor=(width/2, height/2))

def create_circle_icon(fill_color, size=10):
    """Membuat ikon lingkaran."""
    d = size * 2
    svg = f"""<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><circle cx="{d/2}" cy="{d/2}" r="{d/2-2}" fill="{fill_color}" stroke="white" stroke-width="2"/></svg>"""
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))

def apply_chart_style(fig, title=None):
    """Menerapkan gaya pada grafik Plotly."""
    fig.update_layout(
        title=dict(text=title, font=dict(family="Outfit", size=18, color="#FFFFFF")) if title else None,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit", color="#94a3b8"),
        xaxis=dict(showgrid=False, showline=True, linecolor="rgba(148, 163, 184, 0.2)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.05)", showline=False),
        legend=dict(orientation="h", y=1.02, x=1), margin=dict(t=50, l=10, r=10, b=10), hovermode="x unified"
    )
    return fig
