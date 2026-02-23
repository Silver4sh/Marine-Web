from core.utils import get_status_color, create_google_arrow_icon
import numpy as np
from core.database import get_vessel_position
from core.config import inject_custom_css
from folium.plugins import TimestampedGeoJson, MarkerCluster, HeatMap
from streamlit_folium import st_folium

import folium
import pandas as pd
import streamlit as st

def add_history_path_to_map(m, path_df, fill_color, v_id_str, show_timelapse=False):
    if path_df.empty: return
    
    # 2. Marker Akhir (Last Position) - Static
    # 2. Marker Akhir (Last Position) - Static
    last_row = path_df.iloc[0]
    
    # 2b. Garis Histori (Static Track Line)
    # Ensure points are ordered by time (ascending) for the line to be drawn correctly
    path_sorted = path_df.sort_values("created_at")
    path_points = path_sorted[['latitude', 'longitude']].values.tolist()
    
    folium.PolyLine(
        path_points,
        color=fill_color,
        weight=3,
        opacity=0.7,
        tooltip=f"Jalur {v_id_str}"
    ).add_to(m)

    folium.Marker(
        [last_row['latitude'], last_row['longitude']],
        icon=create_google_arrow_icon(last_row.get('heading', 0), fill_color),
        popup=f"Posisi Terakhir: {last_row['created_at']}"
    ).add_to(m)

    if show_timelapse and len(path_df) > 1:
        from folium import Element
        
        path_sorted = path_df.sort_values("created_at")
        
        # Build JS data array
        rute_js = []
        for _, row in path_sorted.iterrows():
            time_str = row['created_at'].strftime("%H:%M:%S") if pd.notnull(row['created_at']) else "Unknown"
            speed_str = f"Speed: {row.get('speed', 0)} kn | Hdg: {row.get('heading', 0)}&deg;"
            rute_js.append(f"{{ latlng: [{row['latitude']}, {row['longitude']}], time: '{time_str}', loc: '{speed_str}' }}")
            
        rute_js_str = ",\\n                        ".join(rute_js)
        # Set total animation duration to roughly 15-20 seconds for smooth playback
        total_anim_ms = 20000
        point_ms = total_anim_ms // max(1, len(rute_js) - 1)
        durations = [point_ms] * (len(rute_js) - 1)
        durations_js_str = ", ".join(map(str, durations))
        
        # 1. Add moving marker plugin script
        m.get_root().html.add_child(Element('<script src="https://ewoken.github.io/Leaflet.MovingMarker/MovingMarker.js"></script>'))
        
        # 2. Setup custom tactical UI for the map
        custom_ui = f"""
        <style>
            .hud-controls-container {{
                position: absolute;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(10, 16, 32, 0.85);
                padding: 15px 25px;
                border: 1px solid {fill_color}80;
                border-radius: 12px;
                z-index: 9999;
                width: 70%;
                max-width: 600px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
                font-family: 'Courier New', monospace;
                color: #8ba3c0;
                backdrop-filter: blur(8px);
            }}
            .hud-time-display {{
                text-align: center;
                font-size: 1.2rem;
                font-weight: bold;
                color: {fill_color};
                margin-bottom: 5px;
                text-shadow: 0 0 10px {fill_color}80;
            }}
            .hud-location-info {{
                text-align: center;
                margin-bottom: 15px;
                font-size: 0.85rem;
                opacity: 0.8;
            }}
            .hud-slider {{
                width: 100%;
                accent-color: {fill_color};
                cursor: pointer;
            }}
            .hud-btn-group {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }}
            .hud-btn {{
                padding: 8px 20px;
                border: 1px solid {fill_color}50;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                transition: 0.3s;
                background: transparent;
                color: {fill_color};
                text-transform: uppercase;
                font-size: 0.8rem;
            }}
            .hud-btn:hover {{
                background: {fill_color}30;
                box-shadow: 0 0 10px {fill_color}40;
            }}
            .hud-speed-active {{
                background: {fill_color};
                color: #0b1120 !important;
                border-color: {fill_color};
            }}
        </style>

        <div class="hud-controls-container">
            <div class="hud-time-display" id="hudTime">--:--:--</div>
            <div class="hud-location-info" id="hudLoc">Sinkronisasi memuat map plugin...</div>
            <input type="range" class="hud-slider" id="hudSlider" min="0" max="100" value="0" disabled>
            <div class="hud-btn-group" style="align-items: center;">
                <button class="hud-btn hud-btn-active" id="btnPlay" onclick="window.startTacticalAnim(event)">▶ Play</button>
                <button class="hud-btn" onclick="window.stopTacticalAnim(event)">⏸ Pause</button>
                <button class="hud-btn" onclick="window.resetTacticalAnim(event)">🔄 Reset</button>
                
                <div style="border-left: 1px solid {fill_color}50; height: 24px; margin: 0 10px;"></div>
                
                <select id="speedSelect" onchange="window.setParamSpeed(this.value)" style="
                    background: transparent; 
                    color: {fill_color}; 
                    border: 1px solid {fill_color}50; 
                    border-radius: 6px; 
                    padding: 6px 10px; 
                    font-size: 0.8rem;
                    font-family: inherit;
                    font-weight: bold;
                    cursor: pointer;
                    outline: none;
                ">
                    <option value="1" style="background:#0b1120;">Speed x1</option>
                    <option value="2" style="background:#0b1120;">Speed x2</option>
                    <option value="3" style="background:#0b1120;">Speed x3</option>
                    <option value="4" style="background:#0b1120;">Speed x4</option>
                </select>
            </div>
        </div>
        """
        m.get_root().html.add_child(Element(custom_ui))
        
        map_id = m.get_name()
        
        custom_js = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                function initMovingMarker() {{
                    // Wait for Leaflet.MovingMarker to load completely
                    if (typeof L === 'undefined' || typeof L.Marker === 'undefined' || typeof L.Marker.movingMarker === 'undefined') {{
                        setTimeout(initMovingMarker, 200);
                        return;
                    }}
                    
                    // Dapatkan instance map dari variabel global leaflet
                    let mapInstance = null;
                    try {{ mapInstance = {map_id}; }} catch(e) {{
                        for (let k in window) {{
                            if (window[k] && window[k]._leaflet_id) {{
                                mapInstance = window[k]; break;
                            }}
                        }}
                    }}
                    
                    if (!mapInstance) return;

                    const dataTrip = [
                        {rute_js_str}
                    ];
                    const rute = dataTrip.map(d => d.latlng);
                    const baseDurations = [{durations_js_str}];
                    
                    const marker = L.Marker.movingMarker(rute, [...baseDurations], {{ autostart: false }});
                    
                    const carIcon = L.icon({{
                        iconUrl: 'https://cdn-icons-png.flaticon.com/512/3448/3448339.png',
                        iconSize: [40, 40], iconAnchor: [20, 20]
                    }});
                    marker.setIcon(carIcon).addTo(mapInstance);
                    
                    const timeLabel = document.getElementById('hudTime');
                    const locLabel = document.getElementById('hudLoc');
                    const slider = document.getElementById('hudSlider');
                    
                    marker.on('checkpoint', function (result) {{
                        const index = result.index;
                        if (dataTrip[index]) {{
                            timeLabel.innerText = dataTrip[index].time;
                            locLabel.innerText = dataTrip[index].loc;
                            slider.value = (index / (dataTrip.length - 1)) * 100;
                        }}
                    }});
                    
                    let followInterval;
                    window.startTacticalAnim = function(e) {{
                        if (e) e.preventDefault();
                        marker.start();
                        followInterval = setInterval(() => {{
                            if (marker.isRunning()) mapInstance.panTo(marker.getLatLng());
                        }}, 100);
                    }};
                    
                    window.stopTacticalAnim = function(e) {{
                        if (e) e.preventDefault();
                        marker.pause();
                        clearInterval(followInterval);
                    }};
                    
                    window.setParamSpeed = function(factor) {{
                        let isRunning = marker.isRunning();
                        if (isRunning) marker.pause();
                        
                        // Konversi string dari dropdown ke angka
                        factor = parseFloat(factor);
                        if(isNaN(factor) || factor <= 0) factor = 1;

                        marker._durations = baseDurations.map(d => Math.floor(d / factor));
                        
                        if (isRunning) window.startTacticalAnim();
                    }};
                    
                    window.resetTacticalAnim = function(e) {{
                        if (e) e.preventDefault();
                        marker.stop();
                        marker.setLatLng(rute[0]);
                        timeLabel.innerText = dataTrip[0].time;
                        locLabel.innerText = "Standby...";
                        slider.value = 0;
                        clearInterval(followInterval);
                        mapInstance.setView(rute[0], Math.max(mapInstance.getZoom(), 8));
                    }};
                    
                    marker.on('end', () => {{
                        clearInterval(followInterval);
                        timeLabel.innerText = dataTrip[dataTrip.length - 1].time;
                        locLabel.innerText = "Lintasan Selesai";
                        slider.value = 100;
                    }});
                    
                    // Init display
                    timeLabel.innerText = dataTrip[0].time;
                    locLabel.innerText = dataTrip[0].loc;
                }}
                
                // Mulai inisialisasi looping pengecekan
                initMovingMarker();
            }});
        </script>
        """
        m.get_root().html.add_child(Element(custom_js))

def render_map_content():
    st.title("🗺️ Peta Posisi Kapal")
    inject_custom_css()
    
    # Init search state
    if "search_select" not in st.session_state:
        st.session_state["search_select"] = None

    df = get_vessel_position()
    
    # Filter Logic
    maint_df = pd.DataFrame()
    active_df = pd.DataFrame()
    
    if not df.empty:
        # Normalize status for filtering
        df['status_lower'] = df['Status'].astype(str).str.lower()
        maint_df = df[df['status_lower'].str.contains('maintenance|repair|mtc', na=False)]
        active_df = df[~df['status_lower'].str.contains('maintenance|repair|mtc', na=False)]
    
    # Layout 3 Columns: Maintenance List | Map | Active List
    c_left, c_center, c_right = st.columns([1, 3, 1])
    
    with c_left:
        from core.utils import render_vessel_list_column
        render_vessel_list_column("Active", active_df, "⚓")

        
    with c_center:
        # Search Bar
        vessel_options = df['code_vessel'].tolist() if not df.empty else []
        search_idx = 0
        
        current_selection = st.session_state.get("search_select")
        if current_selection in vessel_options:
            search_idx = vessel_options.index(current_selection)
            
        selected_vessel = st.selectbox(
            "🔍 Cari Kapal / ID:", 
            options=["Semua Kapal"] + vessel_options, 
            index=search_idx + 1 if current_selection else 0,
        )
        
        # Sync selection
        if selected_vessel != "Semua Kapal":
            st.session_state["search_select"] = selected_vessel
        elif selected_vessel == "Semua Kapal" and current_selection:
             st.session_state["search_select"] = None # Clear/Reset

        # Check if a vessel is selected via "Locate" button OR Search Bar
        center_loc = [-1.2, 108.5]
        zoom = 5
        
        final_selected = st.session_state.get("search_select")
        if final_selected == "Semua Kapal": final_selected = None # Double check
        
        if final_selected and not df.empty:
            target = df[df['code_vessel'] == final_selected]
            if not target.empty:
                center_loc = [target.iloc[0]['latitude'], target.iloc[0]['longitude']]
                zoom = 10
                # st.toast(f"📍 Menemukan: {target.iloc[0].get('Vessel Name', final_selected)}")
        
        m = folium.Map(location=center_loc, zoom_start=zoom, tiles="CartoDB Dark Matter")
        cluster = MarkerCluster().add_to(m)
        
        # Filter markers: Show ONLY selected vessel if one is selected
        map_view_df = df.copy()
        if final_selected:
            map_view_df = df[df['code_vessel'] == final_selected]

        if not map_view_df.empty:
            for _, row in map_view_df.iterrows():
                try:
                    # Determine color
                    v_id = row.get('code_vessel')
                    is_selected = (v_id == final_selected)
                    color = get_status_color(row.get('Status'))
                    
                    folium.Marker(
                        [row['latitude'], row['longitude']], 
                        icon=create_google_arrow_icon(row.get('heading',0), color), 
                        popup=f"<b>{v_id}</b><br>{row.get('Status')}"
                    ).add_to(cluster)
                    
                    # If selected, show path history
                    if is_selected:
                         from core.database import get_path_vessel
                         path = get_path_vessel(v_id)
                         add_history_path_to_map(m, path, color, v_id, show_timelapse=True)
                         
                except: continue
                
        st_folium(m, height=650, width="stretch")
        
        # Detail Section below Map
        if final_selected and not df.empty:
            target = df[df['code_vessel'] == final_selected]
            if not target.empty:
                st.markdown("---")
                from core.utils import render_vessel_detail_section
                render_vessel_detail_section(target.iloc[0])

    with c_right:
        from core.utils import render_vessel_list_column
        render_vessel_list_column("Maintenance", maint_df, "🛠️")

def page_heatmap(df, indikator):
    if df.empty or indikator not in df.columns: return
    data = df[['latitude', 'longitude', indikator]].dropna().values.tolist()
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5, tiles="CartoDB Dark Matter")
    HeatMap(data, radius=25, blur=20).add_to(m)
    st_folium(m, height=400, width="stretch")
