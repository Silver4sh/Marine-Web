import streamlit as st
import pandas as pd
from core.ui.helpers import load_html, get_status_color

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
    
    # Wrap the button and add spacer
    if st.button("📍 Lokasi", key=f"btn_{v_id}_{row.get('Last Update', '')}", width='stretch'):
        st.session_state["search_select"] = v_id
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

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
    last_update = row.get('Last Update', pd.Timestamp.now(tz='UTC'))
    try:
        if pd.isna(last_update):
            last_update = pd.Timestamp.now(tz='UTC')
        mins_ago = int((pd.Timestamp.now(tz='UTC') - last_update).total_seconds() / 60)
    except Exception:
        mins_ago = 0
    
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


# ──────────────────────────────────────────────────────────────────────────────
# Dredging Operations KPI Cards
# ──────────────────────────────────────────────────────────────────────────────

def render_dredging_kpi(
    volume_m3: float = 0.0,
    volume_target_m3: float = 5000.0,
    depth_actual_m: float = 0.0,
    depth_target_m: float = 7.0,
    pump_efficiency_pct: float = 0.0,
    pump_downtime_pct: float = 0.0,
    turbidity_ntu: float = 0.0,
    turbidity_limit_ntu: float = 50.0,
):
    """
    Render 4 KPI cards khusus operasional pengerukan sedimentasi.

    Cards:
      1. Volume Sedimen Terangkat (m³)  + wave-bar progress harian
      2. Kedalaman Aktual vs Target (m LWS) + depth-chip status
      3. Efisiensi Pompa Pasir (Dredger) + sonar-badge status
      4. Kekeruhan Air (Turbidity NTU)  + compliance indicator

    Usage:
        from components.cards import render_dredging_kpi
        render_dredging_kpi(volume_m3=1240, volume_target_m3=5000, ...)
    """
    # ── Computed helpers ─────────────────────────────────────────────────────
    vol_pct  = min(100, int((volume_m3 / max(volume_target_m3, 1)) * 100))
    dep_pct  = min(100, int((abs(depth_actual_m) / max(abs(depth_target_m), 0.1)) * 100))
    eff_pct  = min(100, int(pump_efficiency_pct))

    # Turbidity: green ≤50, warning 50-80, danger >80
    if turbidity_ntu <= turbidity_limit_ntu:
        turb_color = "#2DD4BF";  turb_label = "Aman";       turb_badge = "sonar-badge--active"
    elif turbidity_ntu <= turbidity_limit_ntu * 1.6:
        turb_color = "#FACC15";  turb_label = "Waspada";    turb_badge = "sonar-badge--warning"
    else:
        turb_color = "#F97316";  turb_label = "Melanggar";  turb_badge = "sonar-badge--danger"

    # Depth chip class
    if dep_pct < 50:
        depth_chip_cls = "depth-chip--shallow"
        depth_status   = f"⚠️ {dep_pct}% dari target"
    elif dep_pct < 85:
        depth_chip_cls = "depth-chip--silt"
        depth_status   = f"🔄 {dep_pct}% dari target"
    else:
        depth_chip_cls = "depth-chip--target"
        depth_status   = f"✅ {dep_pct}% dari target"

    # Efficiency chip
    if eff_pct >= 80:
        eff_badge = "sonar-badge--active";  eff_label = "Optimal"
    elif eff_pct >= 55:
        eff_badge = "sonar-badge--warning"; eff_label = "Normal"
    else:
        eff_badge = "sonar-badge--danger";  eff_label = "Rendah"

    # ── Render 4 columns ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="small")

    # ── Card 1: Volume Sedimen Terangkat ─────────────────────────────────────
    with c1:
        st.markdown(f"""
        <div class="marine-card" style="min-height:148px;">
            <div style="font-size:0.70rem;color:#8fafc5;font-family:'Inter',sans-serif;
                        letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;">
                🪣 Volume Sedimen Terangkat
            </div>
            <div style="font-family:'Outfit',sans-serif;font-size:1.80rem;font-weight:800;
                        color:#e2eff8;line-height:1;margin-bottom:2px;">
                {volume_m3:,.0f}
                <span style="font-size:.85rem;color:#8fafc5;font-weight:400;">m³</span>
            </div>
            <div style="font-size:0.72rem;color:#4a6882;margin-bottom:10px;">
                Target harian: <b style="color:#E9C46A;">{volume_target_m3:,.0f} m³</b>
            </div>
            <div class="wave-bar" style="--pct:{vol_pct}%;"></div>
            <div style="font-size:.68rem;color:#8fafc5;margin-top:4px;text-align:right;">
                {vol_pct}% tercapai
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Card 2: Kedalaman Aktual vs Target ───────────────────────────────────
    with c2:
        st.markdown(f"""
        <div class="marine-card" style="min-height:148px;">
            <div style="font-size:0.70rem;color:#8fafc5;font-family:'Inter',sans-serif;
                        letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;">
                ⚓ Kedalaman Aktual vs Target
            </div>
            <div style="font-family:'Outfit',sans-serif;font-size:1.80rem;font-weight:800;
                        color:#e2eff8;line-height:1;margin-bottom:2px;">
                {depth_actual_m:.1f}
                <span style="font-size:.85rem;color:#8fafc5;font-weight:400;">m LWS</span>
            </div>
            <div style="font-size:0.72rem;color:#4a6882;margin-bottom:10px;">
                Target: <b style="color:#2DD4BF;">{depth_target_m:.1f} m LWS</b>
            </div>
            <div style="background:rgba(12,22,38,0.60);border-radius:8px;
                        padding:6px 10px;border:1px solid rgba(45,212,191,0.10);">
                <span class="depth-chip {depth_chip_cls}">{depth_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Card 3: Efisiensi Pompa (Dredger) ───────────────────────────────────
    with c3:
        st.markdown(f"""
        <div class="marine-card" style="min-height:148px;">
            <div style="font-size:0.70rem;color:#8fafc5;font-family:'Inter',sans-serif;
                        letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;">
                ⚙️ Efisiensi Pompa Pasir
            </div>
            <div style="font-family:'Outfit',sans-serif;font-size:1.80rem;font-weight:800;
                        color:#e2eff8;line-height:1;margin-bottom:2px;">
                {eff_pct}
                <span style="font-size:.85rem;color:#8fafc5;font-weight:400;">%</span>
            </div>
            <div style="font-size:0.72rem;color:#4a6882;margin-bottom:10px;">
                Downtime: <b style="color:#F97316;">{pump_downtime_pct:.1f}%</b>
            </div>
            <span class="sonar-badge {eff_badge}">{eff_label}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Card 4: Turbidity / Kekeruhan Air ────────────────────────────────────
    with c4:
        st.markdown(f"""
        <div class="marine-card" style="min-height:148px;border-top-color:{turb_color};">
            <div style="font-size:0.70rem;color:#8fafc5;font-family:'Inter',sans-serif;
                        letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;">
                💧 Kekeruhan Air (Turbidity)
            </div>
            <div style="font-family:'Outfit',sans-serif;font-size:1.80rem;font-weight:800;
                        color:{turb_color};line-height:1;margin-bottom:2px;">
                {turbidity_ntu:.1f}
                <span style="font-size:.85rem;color:#8fafc5;font-weight:400;">NTU</span>
            </div>
            <div style="font-size:0.72rem;color:#4a6882;margin-bottom:10px;">
                Batas: <b style="color:#8fafc5;">{turbidity_limit_ntu:.0f} NTU</b>
            </div>
            <span class="sonar-badge {turb_badge}">{turb_label}</span>
        </div>
        """, unsafe_allow_html=True)

