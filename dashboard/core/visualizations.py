import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap, TimestampedGeoJson
from streamlit_folium import st_folium
from dashboard.core.utils import (
    get_status_color, create_google_arrow_icon,     invite_custom_css=None, 
    render_vessel_detail_section=None, render_vessel_list_column=None, render_vessel_card=None 
)

from dashboard.core.database import get_vessel_position
from dashboard.core.config import inject_custom_css

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
                
                # Simple Arrow SVG
                svg_arrow = f"""
                <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                    <g transform="rotate({heading}, 20, 20)">
                        <path d="M 20,0 L 32,32 L 20,24 L 8,32 Z" fill="{fill_color}" stroke="white" stroke-width="2"/>
                    </g>
                </svg>
                """
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
                            "iconAnchor": [15, 15], # Center of 30x30
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
