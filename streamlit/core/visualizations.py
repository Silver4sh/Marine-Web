from core.utils import get_status_color, create_google_arrow_icon
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
    last_row = path_df.iloc[0]
    folium.Marker(
        [last_row['latitude'], last_row['longitude']],
        icon=create_google_arrow_icon(last_row.get('heading', 0), fill_color),
        popup=f"Posisi Terakhir: {last_row['created_at']}"
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
