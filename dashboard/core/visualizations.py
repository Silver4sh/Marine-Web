import streamlit as st
import folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen, HeatMap, TimestampedGeoJson
from streamlit_folium import st_folium
from dashboard.core_pkg.utils import (
    get_status_color, create_google_arrow_icon, invite_custom_css=None, 
    render_vessel_detail_section=None, render_vessel_list_column=None, render_vessel_card=None 
)
# Note: utils circular dependency avoidance might be needed if we move render_x there
# Actually utils.py has render_vessel_card etc.
from dashboard.core_pkg.utils import get_status_color, create_google_arrow_icon
from dashboard.core_pkg.database importget_vessel_position, get_path_vessel
from dashboard.core_pkg.config import inject_custom_css

def add_history_path_to_map(m, path_df, fill_color, v_id_str, show_timelapse=False):
    if path_df.empty: return
    folium.PolyLine(path_df[['latitude', 'longitude']].values.tolist(), color=fill_color, weight=2, opacity=0.6, dash_array='3, 8').add_to(m)
    for _, p in path_df.iterrows(): folium.CircleMarker([p['latitude'], p['longitude']], radius=2, color=fill_color, fill=True).add_to(m)

def render_map_content():
    st.title("🗺️ Peta Posisi Kapal")
    inject_custom_css()
    df = get_vessel_position()
    
    m = folium.Map(location=[-1.2, 108.5], zoom_start=7.4, tiles="CartoDB Dark Matter")
    cluster = MarkerCluster().add_to(m)
    
    if not df.empty:
        for _, row in df.iterrows():
            try:
                folium.Marker(
                    [row['latitude'], row['longitude']], 
                    icon=create_google_arrow_icon(row.get('heading',0), get_status_color(row.get('Status'))), 
                    popup=row.get('code_vessel')
                ).add_to(cluster)
            except: continue
    st_folium(m, height=600, use_container_width=True)

def page_heatmap(df, indikator):
    if df.empty or indikator not in df.columns: return
    data = df[['latitude', 'longitude', indikator]].dropna().values.tolist()
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5, tiles="CartoDB Dark Matter")
    HeatMap(data, radius=25, blur=20).add_to(m)
    st_folium(m, height=400, use_container_width=True)
