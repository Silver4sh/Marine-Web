import streamlit as st
import pandas as pd
from components.helpers import load_html, get_status_color

def render_metric_card(label, value, delta=None, color="green", help_text=None, sparkline_data=None):
    """Merender kartu metrik dengan opsi sparkline (line chart mini)."""
    html_template = load_html("metric_card_simple.html")
    if not html_template:
        st.error("Template kartu metrik hilang")
        return

    # Generate SVG Sparkline if data is provided
    sparkline_svg = ""
    if sparkline_data and len(sparkline_data) > 1:
        # Simple SVG line chart generation
        width, height = 80, 24
        mx, mn = max(sparkline_data), min(sparkline_data)
        rng = (mx - mn) if (mx - mn) != 0 else 1
        
        points = []
        for i, val in enumerate(sparkline_data):
            x = (i / (len(sparkline_data) - 1)) * width
            y = height - (((val - mn) / rng) * height)
            points.append(f"{x},{y}")
            
        pts_str = " ".join(points)
        sparkline_svg = f"""
        <svg width="100%" height="100%" viewBox="-2 -2 {width+4} {height+4}" preserveAspectRatio="none">
            <polyline fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{pts_str}" 
                      style="filter: drop-shadow(0px 2px 4px {color}66);"/>
        </svg>
        """

    card_html = html_template.replace("{label}", str(label)) \
                             .replace("{value}", str(value)) \
                             .replace("{delta}", str(delta) if delta else "") \
                             .replace("{color}", color) \
                             .replace("{sparkline}", sparkline_svg) \
                             .replace("{help_text}", help_text if help_text else "") \
                             .replace("{display_info}", "block" if help_text else "none")

    st.markdown(card_html.replace("\n", " ").strip(), unsafe_allow_html=True)

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
    
    if st.button("📍 Lokasi", key=f"btn_{v_id}_{row.get('Last Update', '')}"):
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
    from db.repositories.fleet_repo import get_path_vessel
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
        st.dataframe(path_df, hide_index=True)
    else:
        st.info("Belum ada data riwayat perjalanan.")
