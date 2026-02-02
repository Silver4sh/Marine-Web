from core.utils import get_status_color, create_google_arrow_icon
from core.database import get_vessel_position
from core.config import inject_custom_css
from folium.plugins import TimestampedGeoJson, MarkerCluster, HeatMap
from streamlit_folium import st_folium

import folium

def add_history_path_to_map(m, path_df, fill_color, v_id_str, show_timelapse=False):
    if path_df.empty: return
    
    # 1. Garis Statis (Static Line)
    folium.PolyLine(
        path_df[['latitude', 'longitude']].values.tolist(), 
        color=fill_color, weight=2, opacity=0.4, dash_array='3, 8'
    ).add_to(m)
    
    # 2. Marker Akhir (Last Position) - Static
    last_row = path_df.iloc[0]
    folium.Marker(
        [last_row['latitude'], last_row['longitude']],
        icon=create_google_arrow_icon(last_row.get('heading', 0), fill_color),
        popup=f"Posisi Terakhir: {last_row['created_at']}"
    ).add_to(m)

    # 3. Timelapse Playback (Smooth Arrow Animation)
    if show_timelapse:
        sim_df = path_df.sort_values(by='created_at', ascending=True).tail(300) # Limit to last 300 points for performance
        if len(sim_df) > 1:
            features = []
            recs = sim_df.to_dict('records')
            
            import base64
            
            for row in recs:
                # Generate Rotated SVG Arrow per Point
                heading = row.get('heading', 0)
                speed = row.get('speed', 0)
                
                # Simple Arrow SVG (Compact)
                svg_arrow = (
                    f'<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">'
                    f'<g transform="rotate({heading}, 20, 20)">'
                    f'<path d="M 20,0 L 32,32 L 20,24 L 8,32 Z" fill="{fill_color}" stroke="white" stroke-width="2"/>'
                    f'</g></svg>'
                )
                
                # Encode to Data URI
                b64_arrow = base64.b64encode(svg_arrow.encode('utf-8')).decode('utf-8')
                icon_url = f"data:image/svg+xml;base64,{b64_arrow}"
                
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [row['longitude'], row['latitude']]},
                    "properties": {
                        "time": str(row['created_at']),
                        "icon": "marker",
                        "iconstyle": {
                            "iconUrl": icon_url,
                            "iconSize": [30, 30],
                            "iconAnchor": [15, 15],
                            "popupAnchor": [0, -15],
                            "shadowUrl": "",
                            "shadowSize": [0, 0],
                        },
                        "popup": f"🕒 {row['created_at']}<br>🚀 {speed} kn<br>🧭 {heading}°"
                    },
                })
            
            TimestampedGeoJson(
                { "type": "FeatureCollection", "features": features },
                period="PT1M", 
                add_last_point=False, # Don't stick valid markers
                auto_play=True, 
                loop=True,
                max_speed=20, 
                loop_button=True, 
                date_options='YYYY/MM/DD HH:mm:ss',
                time_slider_drag_update=True,
                duration="PT1M", # Set Duration to match Period for continuous flow
                transition_time=500 # Smooth transition in ms
            ).add_to(m)

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
        render_vessel_list_column("Maintenance", maint_df, "🛠️")

        
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
        
        if not df.empty:
            for _, row in df.iterrows():
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
                
        st_folium(m, height=650, use_container_width=True)
        
        # Detail Section below Map
        if final_selected and not df.empty:
            target = df[df['code_vessel'] == final_selected]
            if not target.empty:
                st.markdown("---")
                from core.utils import render_vessel_detail_section
                render_vessel_detail_section(target.iloc[0])

    with c_right:
        from core.utils import render_vessel_list_column
        render_vessel_list_column("Active", active_df, "⚓")

def page_heatmap(df, indikator):
    if df.empty or indikator not in df.columns: return
    data = df[['latitude', 'longitude', indikator]].dropna().values.tolist()
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5, tiles="CartoDB Dark Matter")
    HeatMap(data, radius=25, blur=20).add_to(m)
    st_folium(m, height=400, use_container_width=True)
