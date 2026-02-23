import os
import streamlit as st
import pandas as pd
import folium

def load_html(filename):
    """Memuat template HTML dari folder assets, dikompresi ke satu baris
    agar st.markdown(unsafe_allow_html=True) merender HTML dengan benar."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        file_path   = os.path.join(project_dir, "assets", "html", filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Collapse multi-line HTML to single line — required by Streamlit's
        # CommonMark parser so it doesn't escape the HTML tags.
        import re
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    except FileNotFoundError:
        return ""

def render_metric_card(label, value, delta=None, color="green", help_text=None):
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

    if help_text:
        # Hacky CSS to position the info icon top-right of the card
        # Note: This relies on Streamlit's structure.
        css = """
        <style>
        div[data-testid="column"] { position: relative; }
        div[data-testid="column"] .stPopover {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 10;
        }
        div[data-testid="column"] .stPopover button {
            background: transparent;
            border: none;
            color: #64748b;
            padding: 0.2rem;
            font-size: 1.2rem;
        }
        div[data-testid="column"] .stPopover button:hover {
            color: #38bdf8;
            background: rgba(255,255,255,0.05);
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        with st.popover("ℹ️"):
            st.markdown(f"**Info Metrik**\n\n{help_text}")

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
    """
    Menerapkan tema 'Professional Analyst' pada grafik Plotly.
    Optimized for Dark Mode with Vibrant/Neon palette.
    """
    # Vibrant Neon Palette (Cyan, Violet, Hot Pink, Lime, Amber)
    colors = ["#22d3ee", "#a78bfa", "#f472b6", "#a3e635", "#fbbf24"]
    
    layout_args = dict(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", size=12, color="#94a3b8"), # Slate-400
        
        # Consistent Axis Styling
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(family="Plus Jakarta Sans", size=11, color="#cbd5e1")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="rgba(255, 255, 255, 0.05)", 
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(family="Plus Jakarta Sans", size=11, color="#cbd5e1")
        ),
        
        # Polished Legend
        legend=dict(
            orientation="h", 
            y=1.1, 
            x=0, 
            xanchor="left",
            font=dict(family="Plus Jakarta Sans", size=11, color="#cbd5e1"),
            bgcolor="rgba(0,0,0,0)"
        ),
        
        # Spacing & Colorway
        margin=dict(t=60, l=10, r=10, b=10), 
        hovermode="x unified",
        colorway=colors
    )
    
    if title:
        layout_args["title"] = dict(
            text=title, 
            font=dict(family="Outfit", size=18, weight=600, color="#f8fafc"),
            x=0,
            xanchor="left"
        )
    else:
        layout_args["title"] = dict(text="", font=dict(size=1))

    fig.update_layout(**layout_args)
    
    # Update traces for better hover interactions
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.9)",
            bordercolor="rgba(148, 163, 184, 0.2)",
            font=dict(family="Plus Jakarta Sans", color="#ffffff")
        )
    )
    
    return fig

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
    
    if st.button("📍 Lokasi", key=f"btn_{v_id}_{row.get('Last Update', '')}", width='stretch'):
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
    from core.database import get_path_vessel
    v_name = str(row.get('code_vessel', 'Unknown'))
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
    
    path_df = get_path_vessel(v_id)
    if not path_df.empty:
        path_df = path_df[['created_at', 'latitude', 'longitude', 'speed', 'heading']]
        path_df.columns = ['Waktu', 'Latitude', 'Longitude', 'Kecepatan (kn)', 'Heading (°)']
        st.dataframe(path_df, width='stretch', hide_index=True)
    else:
        st.info("Belum ada data riwayat perjalanan.")
