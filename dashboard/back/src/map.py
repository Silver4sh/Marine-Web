import folium
import branca
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen
from back.query.queries import get_vessel_position, get_financial_metrics, get_order_stats
from back.src.styles import inject_custom_css
from back.src.utils import get_status_color, create_google_arrow_icon, create_circle_icon
from back.query.queries import get_vessel_list

REFRESH_INTERVAL = 600

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_vessel_data():
    df = get_vessel_position()
    return pd.DataFrame() if df.empty else df

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_vessel_list():
    df = get_vessel_list()
    return pd.DataFrame() if df.empty else df

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_additional_metrics():

    fin = get_financial_metrics()
    orders = get_order_stats()
    return fin, orders

def render_vessel_card(row, status_color, highlighted=False):
    v_name = row.get('Vessel Name', 'Unknown')
    v_id = row.get('code_vessel', 'Unknown')
    v_speed = row.get('speed', 0)
    
    bg_color = "rgba(17, 24, 39, 0.95)" if highlighted else "rgba(17, 24, 39, 0.8)"
    border_color = status_color if highlighted else f"{status_color}30"
    box_shadow = f"0 0 15px {status_color}30" if highlighted else "none"
    
    status_bg = f"{status_color}15"
    
    card_html = f'''
    <div class="vessel-card" style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; padding: 10px; margin-bottom: 8px; box-shadow: {box_shadow}; backdrop-filter: blur(8px);">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
            <div style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 65%;">
                <div style="font-weight: 700; color: #e2e8f0; font-size: 0.85rem; margin-bottom: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{v_id}</div>
                <div style="font-size: 0.65rem; color: #94a3b8;">{v_name}</div>
            </div>
            <div style="text-align: right; flex-shrink: 0;">
                <span style="background: {status_bg}; color: {status_color}; padding: 2px 6px; border-radius: 4px; font-size: 0.6rem; font-weight: 600; border: 1px solid {status_color}30;">{str(row.get("Status", "")).upper()}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 4px 8px; border-radius: 6px;">
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="font-size: 0.75rem;">🚀</span>
                <span style="font-size: 0.75rem; color: #cbd5e1; font-family: monospace;">{v_speed} kn</span>
            </div>
            <div style="font-size: 0.65rem; color: #64748b; cursor: pointer;">Details &rarr;</div>
        </div>
    </div>
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)

def page_map_vessel():
    inject_custom_css()
    st.title("🗺️ Peta Posisi Kapal")
    
    #with st.spinner("Syncing metrics..."):
    #    financial, orders = load_additional_metrics()
    #    
    #m1, m2 = st.columns(2)
    #with m1:
    #    rev = financial.get('total_revenue', 0)
    #    delta_rev = financial.get('delta_revenue', 0.0)
    #    rev_str = f"IDR {rev:,.0f}"
    #    if rev > 1000000: rev_str = f"IDR {rev/1000000:.1f}M"
    #    elif rev > 1000: rev_str = f"IDR {rev/1000:.0f}K"    
    #    delta_str = f"{delta_rev:+.1f}% vs last month"
    #    delta_color = "#ef4444" if delta_rev < 0 else "#38bdf8"
    #    render_metric_card("Revenue", rev_str, delta_str, delta_color)
    #
    #with m2:
    #    completed = orders.get('completed', 0)
    #    render_metric_card("Completed Missions", completed, "All Time High", "#2dd4bf")
    #
    #st.markdown("---")

    lat1, lat2, lon1, lon2 = -3.139, -3.179, 108.549, 108.619
    
    with st.sidebar:
        st.header("🎨 Kustomisasi Marker")
        color_mode = st.radio("Mode Warna:", ["Status", "Kecepatan"], index=0)
        if color_mode == "Kecepatan":
            st.info("🟢 ≤5 Knot | 🟠 5-15 Knot | 🔴 >15 Knot")
    
    with st.spinner("Memuat data..."):
        df = load_vessel_data()

    if df.empty:
        st.warning("Data database kosong. Menampilkan data dummy untuk visualisasi.")
        df = pd.DataFrame({
            "code_vessel": ["DUMMY-01", "DUMMY-02"],
            "Vessel Name": ["Alpha Explorer", "Beta Voyager"],
            "Status": ["active", "idle"],
            "latitude": [-3.159, -3.169],
            "longitude": [108.589, 108.569],
            "speed": [12.5, 0.0],
            "heading": [45, 0],
            "Last Update": [pd.Timestamp.now()] * 2
        })

    search_col, refresh_col = st.columns([4, 1])
    with search_col:
        vessel_options = ["All Vessels"]
        if not df.empty and 'code_vessel' in df.columns:
            live_ids = sorted(df['code_vessel'].dropna().astype(str).unique().tolist())
            vessel_options.extend(live_ids)
        
        vessel_db = load_vessel_list()
        if not vessel_db.empty and 'code_vessel' in vessel_db.columns:
            db_codes = sorted(vessel_db['code_vessel'].astype(str).unique().tolist())
            new_codes = [c for c in db_codes if c not in vessel_options]
            vessel_options.extend(new_codes)
            
        selected_vessel = st.selectbox("🔍 Cari kapal (ID):", options=vessel_options, index=0, key="search_select")
        
    with refresh_col:
        st.write("") 
        st.write("") 
        if st.button("🔄", help="Refresh data"):
            st.cache_data.clear()
            st.rerun()
    
    filtered_df = df
    if selected_vessel and selected_vessel != "All Vessels":
        filtered_df = df[df['code_vessel'] == selected_vessel]
        
        if filtered_df.empty:
            st.warning(f"⚠️ Vessel '{selected_vessel}' terdaftar di database tetapi tidak memiliki data posisi aktif saat ini.")
    
    if not filtered_df.empty:
        filtered_df.columns = [c.lower() for c in filtered_df.columns]
        
        if 'status' not in filtered_df.columns:
            filtered_df['status'] = 'active' 
        s_lower = filtered_df['status'].astype(str).str.lower()
        
        emergency_mask = s_lower.str.contains('emergency|distress|broken|accident|danger')
        maint_mask = s_lower.str.contains('maintenance|repair|docked|berthed') & ~emergency_mask
        idle_mask = s_lower.str.contains('idle|inactive|off_duty|parked') & ~emergency_mask & ~maint_mask
        active_mask = ~emergency_mask & ~maint_mask & ~idle_mask
        
        emergency_df = filtered_df[emergency_mask]
        maint_df = filtered_df[maint_mask]
        idle_df = filtered_df[idle_mask]
        active_df = filtered_df[active_mask]
    else:
        emergency_df = maint_df = idle_df = active_df = pd.DataFrame()

    # --- TOP SECTION: Emergency ---
    if not emergency_df.empty:
        st.markdown("### 🚨 Emergency / Distress")
        cols = st.columns(4)
        for idx, row in emergency_df.head(4).iterrows():
            with cols[idx % 4]:
                render_vessel_card(row, "#e74c3c", False)
        st.markdown("---")

    # --- MAIN 3-COLUMN LAYOUT ---
    col_maint, col_map, col_active = st.columns([1, 2.8, 1])
    
    # Middle: Map
    with col_map:
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>🗺️ Maps</h4>", unsafe_allow_html=True)
        m = folium.Map(location=[-1.2, 108.5], zoom_start=7.4, tiles="CartoDB Dark Matter", control_scale=True)
        m.add_child(MiniMap())
        Fullscreen().add_to(m)
        
        folium.Rectangle(
            bounds=[[lat1, lon1], [lat2, lon2]],
            color="yellow",
            fill=True,
            fill_color="yellow",
            fill_opacity=0.1,
            popup="Designated Area"
        ).add_to(m)
        
        cluster = MarkerCluster(options={'maxClusterRadius': 80, 'disableClusteringAtZoom': 15}).add_to(m)
        
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                try:
                    v_name = str(row.get('Vessel Name', 'Unknown'))
                    v_id_str = str(row.get('code_vessel', 'Unknown'))
                    status = str(row.get('Status', 'active')).lower()
                    speed = float(row.get('speed', 0))
                    lat, lon = float(row.get('latitude', 0)), float(row.get('longitude', 0))
                    heading = float(row.get('heading', 0))
                    
                    if color_mode == "Status": 
                        fill_color = get_status_color(status)
                    else: 
                        fill_color = "red" if speed > 15 else "orange" if speed > 5 else "green"
                    
                    if any(x in status for x in ["idle", "inactive", "parked"]):
                        icon = create_circle_icon(fill_color, 12)
                        marker_icon = "⭕"
                    else:
                        icon = create_google_arrow_icon(heading, fill_color, 15)
                        marker_icon = "➤"

                    # Calculate time since last update
                    last_update = row.get('Last Update', pd.Timestamp.now())
                    mins_ago = int((pd.Timestamp.now() - last_update).total_seconds() / 60)
                    
                    # Detailed Popup HTML
                    popup_html = f"""
                    <div style="font-family: 'Arial', sans-serif; width: 280px; background: white; color: #333; border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <div style="padding: 10px 12px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.2rem;">🇮🇩</span>
                            <div>
                                <div style="font-weight: 700; font-size: 14px; color: #1e293b;">{v_id_str}</div>
                                <div style="font-size: 10px; color: #64748b;">{v_name}</div>
                            </div>
                            <div style="margin-left: auto; color: #94a3b8; cursor: pointer;">✕</div>
                        </div>

                        <!-- Image Placeholder -->
                        <div style="background: #f1f5f9; height: 120px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #eee;">
                            <div style="text-align: center; color: #cbd5e1;">
                                <div style="font-size: 30px;">🚢</div>
                                <div style="font-size: 10px;">No Image</div>
                            </div>
                        </div>

                        <!-- Content -->
                        <div style="padding: 12px;">
                            <!-- Actions -->
                            <div style="display: flex; gap: 8px; margin-bottom: 15px;">
                                <button style="flex: 1; padding: 6px; border: 1px solid #cbd5e1; background: white; border-radius: 4px; font-size: 11px; font-weight: 600; color: #475569; cursor: pointer;">Add to fleet</button>
                                <button style="flex: 1; padding: 6px; border: none; background: #0ea5e9; border-radius: 4px; font-size: 11px; font-weight: 600; color: white; cursor: pointer;">Vessel details</button>
                            </div>

                            <!-- Route Info -->
                            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                                <div style="font-size: 16px; font-weight: 700; color: #0f172a;">{str(row.get('code_vessel', 'N/A'))}</div>
                                <div style="text-align: right;">
                                    <div style="font-size: 11px; color: #64748b;">DESTINATION</div>
                                    <div style="font-size: 12px; font-weight: 600; color: #0ea5e9;">-</div>
                                </div>
                            </div>

                            <!-- Times -->
                            <div style="display: flex; justify-content: space-between; font-size: 10px; color: #334155; margin-bottom: 15px;">
                                <div><b>ATD:</b> -</div>
                                <div><b>ATA:</b> -</div>
                            </div>

                            <!-- Progress Bar Mockup -->
                            <div style="position: relative; height: 4px; background: #e2e8f0; border-radius: 2px; margin-bottom: 20px;">
                                <div style="position: absolute; left: 0; top: 0; height: 100%; width: 60%; background: #0ea5e9; border-radius: 2px;"></div>
                                <div style="position: absolute; left: 60%; top: -6px; margin-left: -6px; color: #0ea5e9; font-size: 12px;">➤</div>
                            </div>

                            <!-- Bottom Actions -->
                            <div style="display: flex; gap: 8px; margin-bottom: 15px;">
                                <button style="padding: 4px 8px; background: #334155; color: white; border: none; border-radius: 3px; font-size: 10px;">Last track</button>
                                <button style="padding: 4px 8px; background: white; color: #334155; border: 1px solid #cbd5e1; border-radius: 3px; font-size: 10px;">Use route tool</button>
                            </div>
                        </div>

                        <!-- Footer Stats -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; border-top: 1px solid #eee; background: #f8fafc;">
                            <div style="padding: 8px; border-right: 1px solid #eee;">
                                <div style="font-size: 9px; color: #64748b;">Nav Status</div>
                                <div style="font-size: 11px; font-weight: 600; color: #334155;">{status.capitalize()}</div>
                            </div>
                            <div style="padding: 8px; border-right: 1px solid #eee;">
                                <div style="font-size: 9px; color: #64748b;">Speed/Course</div>
                                <div style="font-size: 11px; font-weight: 600; color: #334155;">{speed} kn / {heading}°</div>
                            </div>
                            <div style="padding: 8px;">
                                <div style="font-size: 9px; color: #64748b;">Draught</div>
                                <div style="font-size: 11px; font-weight: 600; color: #334155;">-</div>
                            </div>
                        </div>

                        <!-- Timestamp -->
                        <div style="padding: 6px 12px; font-size: 9px; color: #94a3b8; border-top: 1px solid #eee;">
                            Received: <b>{mins_ago} min ago</b> (AIS Source)
                        </div>
                    </div>
                    """
                    
                    folium.Marker(
                        [lat, lon], icon=icon, popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{marker_icon} {v_id_str}"
                    ).add_to(cluster)
                except: continue
                
        try:
            # Disable return objects to prevent reload on click
            st_folium(m, width=None, height=650, use_container_width=True, returned_objects=[])
        except Exception as e:
            st.error(f"Map Error: {e}")

    # Left: Maintenance
    with col_maint:
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>🛠️ Maintenance</h4>", unsafe_allow_html=True)
        if not maint_df.empty:
            with st.container(height=650):
                for _, row in maint_df.iterrows():
                    render_vessel_card(row, get_status_color(row.get('Status')), highlighted=False)
        else:
            with st.container(height=650):
                 st.info("No vessels in maintenance.")

    # Right: Active
    with col_active:
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>⚓ Active</h4>", unsafe_allow_html=True)
        if not active_df.empty:
            with st.container(height=650):
                for _, row in active_df.iterrows():
                    render_vessel_card(row, get_status_color(row.get('Status')), highlighted=False)
        else:
             with st.container(height=650):
                st.info("No active vessels.")

    # Bottom: Idle
    if not idle_df.empty:
        st.markdown("### 💤 Idle / Inactive")
        cols = st.columns(4)
        for idx, row in idle_df.head(4).iterrows():
            with cols[idx % 4]:
                render_vessel_card(row, get_status_color(row.get('Status')), highlighted=False)
    
    with st.expander("📋 Legenda", expanded=False):
        st.write("Legend info here...")

if __name__ == "__main__":
    page_map_vessel()