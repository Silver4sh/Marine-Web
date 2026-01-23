from datetime import datetime
import os
import pandas as pd
import streamlit as st
import folium
from dashboard.config import load_css

# --- Helper Functions ---
def inject_custom_css():
    """Menyematkan gaya CSS global."""
    css = load_css("global.css")
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def load_html(filename):
    """Memuat template HTML dari folder assets."""
    try:
        with open(f"dashboard/assets/html/{filename}", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        try:
             with open(f"assets/html/{filename}", "r", encoding="utf-8") as f:
                return f.read()
        except:
             return ""

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

# --- UI Rendering Functions ---
def render_vessel_card(row, status_color, highlighted=False):
    v_name = row.get('Vessel Name', 'Unknown')
    v_id = row.get('code_vessel', 'Unknown')
    v_speed = row.get('speed', 0)
    bg_color = f"linear-gradient(135deg, {status_color}22 0%, rgba(17, 24, 39, 0.9) 100%)"
    border_color = status_color if highlighted else f"{status_color}40"
    box_shadow = f"0 4px 15px {status_color}25" if highlighted else "none"
    status_bg = f"{status_color}20"
    
    html = load_html("vessel_card.html")
    if html:
        status_text = str(row.get("Status", "")).upper()
        card_html = html.replace("{bg_color}", bg_color).replace("{border_color}", border_color)\
                        .replace("{box_shadow}", box_shadow).replace("{v_id}", str(v_id))\
                        .replace("{v_name}", str(v_name)).replace("{status_bg}", status_bg)\
                        .replace("{status_color}", status_color).replace("{status_text}", status_text)\
                        .replace("{v_speed}", str(v_speed))
        st.markdown(card_html, unsafe_allow_html=True)
    
    if st.button("📍 Lokasi", key=f"btn_{v_id}_{row.get('Last Update', '')}", use_container_width=True):
        st.session_state["search_select"] = v_id

def render_vessel_list_column(title, df, icon="⚓", height=650):
    st.markdown(f"<h4 style='text-align: center; margin-bottom: 10px;'>{icon} {title}</h4>", unsafe_allow_html=True)
    if not df.empty:
        with st.container(height=height):
            for _, row in df.iterrows():
                render_vessel_card(row, get_status_color(row.get('Status', 'active')), highlighted=False)
    else:
        with st.container(height=height):
             st.info(f"Tidak ada kapal {title.lower()}.")

def render_vessel_detail_section(row):
    """Merender tampilan detail untuk satu kapal yang dipilih."""
    # Imports needed here to avoid circular dependency if data_manager imports utils
    from dashboard.data_manager import get_path_vessel
    
    v_name = str(row.get('code_vessel', 'Unknown')) # row keys might be lower case from data_manager
    if 'Vessel Name' in row: v_name = str(row.get('Vessel Name'))
    
    v_id = str(row.get('code_vessel', 'N/A'))
    v_flag = "🇮🇩 Indonesia"
    status = str(row.get('Status', 'Unknown')).capitalize()
    speed = row.get('speed', 0)
    heading = row.get('heading', '-')
    lat = row.get('latitude', 0)
    lon = row.get('longitude', 0)
    last_update = row.get('Last Update', pd.Timestamp.now())
    mins_ago = int((pd.Timestamp.now() - last_update).total_seconds() / 60)
    
    st.markdown("### 📋 Ringkasan")
    
    c1, c2 = st.columns(2)
    with c1:
        html = load_html("vessel_detail_general.html")
        if html:
            st.markdown(html.replace("{v_name}", v_name).replace("{v_flag}", v_flag)
                            .replace("{v_id}", v_id).replace("{v_mmsi}", "-")
                            .replace("{v_callsign}", "-").replace("{v_type}", "-"), unsafe_allow_html=True)
    with c2:
        html = load_html("vessel_detail_ais.html")
        if html:
            st.markdown(html.replace("{status}", status).replace("{mins_ago}", str(mins_ago))
                            .replace("{lat:.4f}", f"{lat:.4f}").replace("{lon:.4f}", f"{lon:.4f}")
                            .replace("{speed}", str(speed)).replace("{course}", str(heading))
                            .replace("{draught}", "-").replace("{destination}", "-").replace("{eta}", "-"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Riwayat Perjalanan
    path_df = get_path_vessel(v_id)
    if not path_df.empty:
        path_df = path_df[['created_at', 'latitude', 'longitude', 'speed', 'heading']]
        path_df.columns = ['Waktu', 'Latitude', 'Longitude', 'Kecepatan (kn)', 'Heading (°)']
        st.dataframe(path_df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data riwayat perjalanan.")
