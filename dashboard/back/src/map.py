import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster, MiniMap, Fullscreen
from streamlit_folium import st_folium
from back.src.styles import inject_custom_css
from back.query.queries import get_vessel_position, get_financial_metrics, get_order_stats, get_vessel_list, get_path_vessel
from back.src.utils import get_status_color, create_google_arrow_icon, create_circle_icon

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

def update_search_select(v_id):
    st.session_state["search_select"] = v_id

def render_vessel_card(row, status_color, highlighted=False):
    v_name = row.get('Vessel Name', 'Unknown')
    v_id = row.get('code_vessel', 'Unknown')
    v_speed = row.get('speed', 0)
    
    bg_color = f"linear-gradient(135deg, {status_color}22 0%, rgba(17, 24, 39, 0.9) 100%)"
    border_color = status_color if highlighted else f"{status_color}40"
    box_shadow = f"0 4px 15px {status_color}25" if highlighted else "none"
    
    status_bg = f"{status_color}20"
    
    # Card HTML
    card_html = f'''
    <div class="vessel-card" style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 12px; margin-bottom: 8px; box-shadow: {box_shadow}; backdrop-filter: blur(8px); transition: all 0.3s ease;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <div style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 65%;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.9rem; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.5px;">{v_id}</div>
                <div style="font-size: 0.7rem; color: #cbd5e1;">{v_name}</div>
            </div>
            <div style="text-align: right; flex-shrink: 0;">
                <span style="background: {status_bg}; color: {status_color}; padding: 3px 8px; border-radius: 6px; font-size: 0.6rem; font-weight: 700; border: 1px solid {status_color}40; letter-spacing: 0.5px;">{str(row.get("Status", "")).upper()}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); padding: 6px 10px; border-radius: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.8rem;">🚀</span>
                <span style="font-size: 0.8rem; color: #e2e8f0; font-family: monospace; font-weight: 600;">{v_speed} kn</span>
            </div>
        </div>
    </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Invisible button that covers the card area is hard in pure Streamlit.
    # We will add a small styled button below it or use the key mechanism.
    # For better UX, we just add a small "Locate" button.
    
    st.button("📍 Locate", key=f"btn_{v_id}_{row.get('Last Update', '')}", 
              on_click=update_search_select, args=(v_id,), use_container_width=True)

def render_vessel_detail_section(row):
    """
    Renders the detailed view for a single selected vessel.
    """
    v_name = str(row.get('Vessel Name', 'Unknown'))
    v_id = str(row.get('code_vessel', 'N/A'))
    status = str(row.get('Status', 'Unknown')).capitalize()
    speed = row.get('speed', 0)
    course = row.get('heading', '-')
    lat = row.get('latitude', 0)
    lon = row.get('longitude', 0)
    last_update = row.get('Last Update', pd.Timestamp.now())
    mins_ago = int((pd.Timestamp.now() - last_update).total_seconds() / 60)
    
    # --- Summary Section ---
    st.markdown("### Summary")
    
    # --- Details Cards ---
    col_gen, col_ais = st.columns([1, 1])
    
    # General Card
    with col_gen:
        st.markdown(f"""
        <div style="background: rgba(17, 24, 39, 0.8); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
            <h4 style="margin-top: 0; color: #f8fafc; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">General</h4>
            <div style="background: rgba(255,255,255,0.05); height: 200px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; border-radius: 8px;">
                <div style="text-align: center; color: #94a3b8;">
                    <div style="font-size: 40px;">🚢</div>
                    <div>No Image Available</div>
                </div>
            </div>
            <table style="width: 100%; font-size: 14px;">
                <tr><td style="color: #94a3b8; padding: 8px 0;">Name</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{v_name}</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Flag</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">🇮🇩 Indonesia</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">ID/Code</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{v_id}</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">MMSI</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">-</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Call sign</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">-</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">General vessel type</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">Cargo</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # AIS Info Card
    with col_ais:
        st.markdown(f"""
        <div style="background: rgba(17, 24, 39, 0.8); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
            <h4 style="margin-top: 0; color: #f8fafc; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Latest AIS information</h4>
            <table style="width: 100%; font-size: 14px;">
                <tr><td style="color: #94a3b8; padding: 8px 0;">Navigational status</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{status}</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Position received</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{mins_ago} mins ago</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Latitude/Longitude</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{lat:.4f} / {lon:.4f}</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Speed</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{speed} kn</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Course</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">{course} °</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Draught</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">-</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Reported destination</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">-</td></tr>
                <tr style="border-top: 1px solid rgba(255,255,255,0.1);"><td style="color: #94a3b8; padding: 8px 0;">Reported ETA</td> <td style="font-weight: 600; text-align: right; color: #f1f5f9;">-</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # History Table (Full Width below cards)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
        <div style="background: rgba(17, 24, 39, 0.8); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
            <h4 style="margin-top: 0; color: #f8fafc; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Riwayat Perjalanan (Travel History)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Fetch history data
        path_df = get_path_vessel(v_id)
        if not path_df.empty:
            # Format for display
            display_df = path_df[['created_at', 'latitude', 'longitude', 'speed', 'heading']].copy()
            display_df.columns = ['Waktu', 'Latitude', 'Longitude', 'Speed (kn)', 'Heading (°)']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Waktu": st.column_config.DatetimeColumn("Waktu", format="D MMM YYYY, HH:mm:ss"),
                    "Latitude": st.column_config.NumberColumn("Latitude", format="%.5f"),
                    "Longitude": st.column_config.NumberColumn("Longitude", format="%.5f"),
                    "Speed (kn)": st.column_config.NumberColumn("Speed (kn)", format="%.1f"),
                    "Heading (°)": st.column_config.NumberColumn("Heading (°)", format="%d"),
                }
            )
        else:
            st.info("Belum ada data riwayat perjalanan.")

def page_map_vessel():
    inject_custom_css()
    
    # Custom CSS for Video-Style Simulation Controls (Leaflet TimestampedGeoJson)
    st.markdown("""
    <style>
        /* Container Position & Style */
        .leaflet-control-timecontrol {
            position: absolute !important;
            bottom: 25px !important;
            left: 20px !important;
            right: 20px !important;
            width: auto !important;
            margin: 0 !important;
            border: none !important;
            background: rgba(15, 23, 42, 0.9) !important; /* Dark Slate 900 */
            backdrop-filter: blur(8px);
            border-radius: 12px !important;
            padding: 8px 16px !important;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            z-index: 1000 !important;
        }

        /* Remove default borders and backgrounds from inner bars */
        .leaflet-bar-timecontrol {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            width: 100% !important;
        }
        
        /* Play/Forward/Backward Buttons */
        .leaflet-bar-timecontrol a {
            background-color: transparent !important;
            border: none !important;
            color: #f8fafc !important; /* White-ish */
            font-size: 14px !important;
            width: 30px !important;
            height: 30px !important;
            line-height: 30px !important;
            border-radius: 50% !important;
            transition: background 0.2s;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .leaflet-bar-timecontrol a:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #3b82f6 !important; /* Blue highlight */
        }
        
        /* Slider Styling */
        .timecontrol-slider {
            flex-grow: 1 !important;
            margin: 0 15px !important;
            border: none !important;
        }
        .timecontrol-slider .slider {
            width: 100% !important;
            margin: 0 !important;
        }

        /* Date/Time Display */
        .timecontrol-date {
            font-family: 'Inter', sans-serif !important;
            font-size: 12px !important;
            color: #cbd5e1 !important; /* Slate 300 */
            min-width: 130px !important;
            text-align: right !important;
            margin-left: 10px !important;
            font-variant-numeric: tabular-nums;
        }
        
        /* Hide Speed Control (optional, keeps it clean) */
        .timecontrol-speed {
            display: none !important; 
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🗺️ Peta Posisi Kapal")

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

    # --- LAYOUT LOGIC ---
    if selected_vessel and selected_vessel != "All Vessels":
        # === SINGLE VESSEL VIEW ===
        
        # 1. Full Width Map
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>🗺️ Vessel Location</h4>", unsafe_allow_html=True)
        m = folium.Map(location=[-1.2, 108.5], zoom_start=7.4, min_zoom=2, max_bounds=True, tiles="CartoDB Dark Matter", control_scale=True)
        m.add_child(MiniMap())
        Fullscreen().add_to(m)
        
        folium.Rectangle(
            bounds=[[lat1, lon1], [lat2, lon2]],
            color="yellow", fill=True, fill_color="yellow", fill_opacity=0.1, popup="Designated Area"
        ).add_to(m)
        
        cluster = MarkerCluster(options={'maxClusterRadius': 80, 'disableClusteringAtZoom': 15}).add_to(m)
        
        # Add ONLY the selected vessel to the map (or all, but focus on one? User request implies "auto full" map. 
        # Usually user still wants to see others around, but let's stick to showing the fleet but optimizing view for single if needed.
        # For now, we render ALL vessels on the map, but the layout is full width.)
        
        if not filtered_df.empty: 
            # Note: filtered_df already filtered to SINGLE vessel if selected! 
            
            for _, row in filtered_df.iterrows():
                try:
                    v_name = str(row.get('Vessel Name', 'Unknown'))
                    v_id_str = str(row.get('code_vessel', 'Unknown'))
                    status = str(row.get('Status', 'active')).lower()
                    speed = float(row.get('speed', 0))
                    lat, lon = float(row.get('latitude', 0)), float(row.get('longitude', 0))
                    heading = float(row.get('heading', 0))
                    
                    if color_mode == "Status": fill_color = get_status_color(status)
                    else: fill_color = "red" if speed > 15 else "orange" if speed > 5 else "green"
                    
                    if any(x in status for x in ["idle", "inactive", "parked"]):
                        icon = create_circle_icon(fill_color, 12)
                        marker_icon = "⭕"
                    else:
                        icon = create_google_arrow_icon(heading, fill_color, 15)
                        marker_icon = "➤"

                    # Draw History Path
                    path_df = get_path_vessel(v_id_str)
                    if not path_df.empty:
                        # 1. Static PolyLine (The dashed line showing the full path)
                        path_coords = path_df[['latitude', 'longitude']].values.tolist()
                        folium.PolyLine(
                            locations=path_coords,
                            color=fill_color,
                            weight=2,
                            opacity=0.6,
                            dash_array='3, 8', # Dotted look
                            tooltip=f"Path of {v_id_str}"
                        ).add_to(m)

                        # 2. History Markers (Small Dots at each point)
                        for _, p_row in path_df.iterrows():
                            p_lat, p_lon = p_row['latitude'], p_row['longitude']
                            
                            folium.CircleMarker(
                                location=[p_lat, p_lon],
                                radius=2,
                                color=fill_color,
                                fill=True,
                                fill_color=fill_color,
                                fill_opacity=1.0,
                                tooltip=f"{p_row['created_at']}"
                            ).add_to(m)

                        # 3. Simulation Playback (TimestampedGeoJson)
                        features = []
                        
                        # A. Moving Marker (Point)
                        for _, p_row in path_df.iterrows():
                            features.append({
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [p_row['longitude'], p_row['latitude']],
                                },
                                "properties": {
                                    "time": str(p_row['created_at']),
                                    "style": {"color": fill_color},
                                    "icon": "circle",
                                    "iconstyle": {
                                        "fillColor": fill_color,
                                        "fillOpacity": 0.9,
                                        "stroke": "true",
                                        "radius": 6,
                                    },
                                },
                            })

                        # B. Animated Path (LineString)
                        # Create a single LineString feature that grows over time
                        # We need coordinates ordered by time (created_at ASC) for the line to draw correctly
                        path_df_asc = path_df.sort_values(by='created_at', ascending=True)
                        coords_asc = path_df_asc[['longitude', 'latitude']].values.tolist()
                        times_asc = [str(t) for t in path_df_asc['created_at']]
                        
                        features.append({
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": coords_asc,
                            },
                            "properties": {
                                "times": times_asc, # Array of timestamps for each coordinate
                                "style": {
                                    "color": fill_color,
                                    "weight": 4,
                                    "opacity": 0.8
                                }
                            }
                        })

                        from folium.plugins import TimestampedGeoJson
                        
                        TimestampedGeoJson(
                            {
                                "type": "FeatureCollection",
                                "features": features,
                            },
                            period="PT1M", 
                            add_last_point=True,
                            auto_play=False,
                            loop=False,
                            max_speed=10,
                            loop_button=True,
                            date_options='YYYY/MM/DD HH:mm:ss',
                            time_slider_drag_update=True,
                            duration="PT1H" 
                        ).add_to(m)

                    folium.Marker(
                        [lat, lon], icon=icon, popup=v_name, tooltip=f"{marker_icon} {v_id_str}"
                    ).add_to(cluster)
                    
                    # Auto-center map on this vessel
                    m.location = [lat, lon]
                    m.zoom_start = 12
                except: continue
        
        st_folium(m, width=None, height=500, use_container_width=True, returned_objects=[])
        
        # 2. Detailed Info Section below map
        if not filtered_df.empty:
            render_vessel_detail_section(filtered_df.iloc[0])
            
    else:
        # === DEFAULT 3-COLUMN VIEW (All Vessels) ===
        
        col_maint, col_map, col_active = st.columns([1, 2.8, 1])
        
        # Middle: Map
        with col_map:
            st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>🗺️ Maps</h4>", unsafe_allow_html=True)
            m = folium.Map(location=[-1.2, 108.5], zoom_start=7.4, min_zoom=2, max_bounds=True, tiles="CartoDB Dark Matter", control_scale=True)
            m.add_child(MiniMap())
            Fullscreen().add_to(m)
            
            folium.Rectangle(
                bounds=[[lat1, lon1], [lat2, lon2]],
                color="yellow", fill=True, fill_color="yellow", fill_opacity=0.1, popup="Designated Area"
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
                        
                        # Detailed Popup HTML (Keeping the original rich popup for the main map view)
                        popup_html = f"""
                        <div style="font-family: 'Arial', sans-serif; width: 280px; background: white; color: #333; border-radius: 8px; overflow: hidden;">
                            <div style="padding: 10px 12px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 1.2rem;">🇮🇩</span>
                                <div>
                                    <div style="font-weight: 700; font-size: 14px; color: #1e293b;">{v_id_str}</div>
                                    <div style="font-size: 10px; color: #64748b;">{v_name}</div>
                                </div>
                            </div>
                            <div style="padding: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                                    <div style="font-size: 16px; font-weight: 700; color: #0f172a;">{v_id_str}</div>
                                </div>
                                <div style="display: flex; gap: 8px; margin-bottom: 15px;">
                                    <span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 10px; color: #475569;">{status}</span>
                                    <span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 10px; color: #475569;">{speed} kn</span>
                                </div>
                            </div>
                        </div>
                        """
                        
                        folium.Marker(
                            [lat, lon], icon=icon, popup=folium.Popup(popup_html, max_width=300),
                            tooltip=f"{marker_icon} {v_id_str}"
                        ).add_to(cluster)
                    except: continue
                    
            try:
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
            with st.container(height=200):
                cols = st.columns(4)
                for idx, row in idle_df.iterrows():
                    with cols[idx % 4]:
                        render_vessel_card(row, get_status_color(row.get('Status')), highlighted=False)

if __name__ == "__main__":
    page_map_vessel()