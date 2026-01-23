import streamlit as st
import folium
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import numpy as np
from folium.plugins import MarkerCluster, MiniMap, Fullscreen, HeatMap, TimestampedGeoJson
from streamlit_folium import st_folium

from dashboard.config import load_css
from dashboard.utils import (
    get_status_color, create_google_arrow_icon, create_circle_icon, 
    load_html, load_css, render_vessel_detail_section, render_vessel_list_column,
    render_vessel_card
)
from dashboard.data_manager import (
    get_vessel_position, get_vessel_list, get_path_vessel,
    get_buoy_list, get_buoy_date_range, get_global_date_range, 
    get_aggregated_buoy_history, get_buoy_history
)

REFRESH_INTERVAL = 600

@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def load_vessel_data():
    df = get_vessel_position()
    return pd.DataFrame() if df.empty else df

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_vessel_list():
    df = get_vessel_list()
    return pd.DataFrame() if df.empty else df

def add_history_path_to_map(m, path_df, fill_color, v_id_str, show_timelapse=False):
    if path_df.empty: return

    # 1. Garis Statis
    path_coords = path_df[['latitude', 'longitude']].values.tolist()
    folium.PolyLine(
        locations=path_coords, color=fill_color, weight=2, opacity=0.6,
        dash_array='3, 8', tooltip=f"Jalur {v_id_str}"
    ).add_to(m)

    # 2. Marker Riwayat
    for _, p_row in path_df.iterrows():
        folium.CircleMarker(
            location=[p_row['latitude'], p_row['longitude']], radius=2,
            color=fill_color, fill=True, fill_color=fill_color, fill_opacity=1.0,
            tooltip=f"{p_row['created_at']}"
        ).add_to(m)

    # 3. Timelapse Playback
    if show_timelapse:
        sim_df = path_df.sort_values(by='created_at', ascending=True).tail(300)
        if len(sim_df) > 1:
            features = []
            recs = sim_df.to_dict('records')
            for i, row in enumerate(recs):
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [row['longitude'], row['latitude']]},
                    "properties": {
                        "time": str(row['created_at']),
                        "style": {"color": fill_color},
                        "icon": "circle",
                        "iconstyle": {"fillColor": fill_color, "fillOpacity": 0.9, "stroke": "true", "radius": 5},
                        "popup": f"Waktu: {row['created_at']}<br>Kecepatan: {row['speed']} kn"
                    },
                })
            
            TimestampedGeoJson(
                { "type": "FeatureCollection", "features": features },
                period="PT1M", add_last_point=True, auto_play=False, loop=False,
                max_speed=50, loop_button=True, date_options='YYYY/MM/DD HH:mm:ss',
                time_slider_drag_update=True
            ).add_to(m)

def render_map_content():
    st.title("🗺️ Peta Posisi Kapal")
    
    map_css = load_css("map_style.css")
    if map_css:
        st.markdown(f"<style>{map_css}</style>", unsafe_allow_html=True)

    lat1, lat2, lon1, lon2 = -3.139, -3.179, 108.549, 108.619
    df = load_vessel_data()

    if df.empty:
        st.warning("Data database kosong. Menampilkan data dummy.")
        # Dummy generation skipped for brevity
        
    search_col, refresh_col = st.columns([4, 1])
    with search_col:
        vessel_options = ["Semua Kapal"]
        if not df.empty and 'code_vessel' in df.columns:
            live_ids = sorted(df['code_vessel'].dropna().astype(str).unique().tolist())
            vessel_options.extend(live_ids)
        selected_vessel = st.selectbox("🔍 Cari Kapal (ID):", options=vessel_options, index=0, key="search_select")
        
    with refresh_col:
        st.write("") 
        st.write("") 
        if st.button("🔄", help="Segarkan Data"):
            st.cache_data.clear()
            st.rerun()
            
    filtered_df = df
    if selected_vessel and selected_vessel != "Semua Kapal":
        filtered_df = df[df['code_vessel'] == selected_vessel]

    # Map Creation
    if selected_vessel and selected_vessel != "Semua Kapal":
        # Single View
        st.button("⬅️ Kembali ke Semua Kapal", type="secondary", on_click=lambda: st.session_state.update(search_select="Semua Kapal"))
        c_title, c_tog = st.columns([3, 1])
        with c_title: st.markdown("<h4 style='text-align: center;'>🗺️ Lokasi Kapal</h4>", unsafe_allow_html=True)
        with c_tog: show_timelapse = st.toggle("⏱️ Timelapse", value=False)
        
        m = folium.Map(location=[-1.2, 108.5], zoom_start=7.4, tiles="CartoDB Dark Matter")
        m.add_child(MiniMap())
        Fullscreen().add_to(m)
        folium.Rectangle(bounds=[[lat1, lon1], [lat2, lon2]], color="yellow", fill=True, fill_opacity=0.1).add_to(m)
        
        if not filtered_df.empty:
             row = filtered_df.iloc[0]
             lat, lon = row.get('latitude', 0), row.get('longitude', 0)
             color = get_status_color(row.get('Status', 'active'))
             v_id = row.get('code_vessel', 'Unknown')
             add_history_path_to_map(m, get_path_vessel(v_id), color, v_id, show_timelapse)
             folium.Marker([lat, lon], icon=create_google_arrow_icon(row.get('heading', 0), color), popup=row.get('Vessel Name')).add_to(m)
             m.location = [lat, lon]
             m.zoom_start = 12
             
        st_folium(m, height=500, use_container_width=True)
        if not filtered_df.empty:
            render_vessel_detail_section(filtered_df.iloc[0])
            
    else:
        # All View
        c1, c2, c3 = st.columns([1, 2.8, 1])
        
        maint_mask = filtered_df['Status'].astype(str).str.lower().str.contains('maintenance|repair|docked')
        active_mask = ~maint_mask & ~filtered_df['Status'].astype(str).str.lower().str.contains('idle|inactive')
        maint_df = filtered_df[maint_mask]
        active_df = filtered_df[active_mask]

        with c1: render_vessel_list_column("Maintenance", maint_df, "🛠️")
        with c3: render_vessel_list_column("Aktif", active_df, "⚓")
        
        with c2:
             m = folium.Map(location=[-1.2, 108.5], zoom_start=7.4, tiles="CartoDB Dark Matter")
             cluster = MarkerCluster().add_to(m)
             for _, row in filtered_df.iterrows():
                 try:
                     color = get_status_color(row.get('Status'))
                     folium.Marker([row['latitude'], row['longitude']], icon=create_google_arrow_icon(row.get('heading',0), color), popup=row.get('Vessel Name')).add_to(cluster)
                 except: continue
             st_folium(m, height=650, use_container_width=True)


def page_heatmap(df, indikator):
    if df.empty:
        st.warning("⚠️ Data tidak tersedia.")
        return
    if indikator not in df.columns:
        st.error(f"❌ Indikator '{indikator}' tidak ditemukan.")
        return
    df_agg = df.groupby(['latitude', 'longitude'], as_index=False)[indikator].mean()
    heat_data = df_agg[['latitude', 'longitude', indikator]].dropna().values.tolist()
    if not heat_data:
        st.warning(f"Data {indikator} kosong.")
        return
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5, tiles="CartoDB Dark Matter")
    HeatMap(heat_data, radius=25, blur=20, gradient={0.4: '#1e3a8a', 0.65: '#2dd4bf', 1: '#38bdf8'}).add_to(m)
    st_folium(m, height=400, use_container_width=True)

def render_history_chart(df, indikator, selected_buoy):
    df["created_at"] = pd.to_datetime(df["created_at"])
    rename_map = {"salinitas": "Salinitas", "turbidity": "Kekeruhan", "current": "Arus", "oxygen": "Oksigen", "tide": "Pasang Surut", "density": "Densitas"}
    df = df.rename(columns=rename_map)
    labels = [rename_map.get(x, x) for x in indikator]

    base = alt.Chart(df).encode(x=alt.X("created_at:T", title="Waktu", axis=alt.Axis(format="%d %b %H:%M")))
    lines = base.transform_fold(labels).mark_line().encode(y=alt.Y("value:Q", title="Nilai"), color=alt.Color("key:N", title="Parameter"), tooltip=["created_at:T", "key:N", "value:Q"])
    
    st.altair_chart(lines, use_container_width=True)
    
    with st.expander("📊 Ringkasan Statistik", expanded=True):
        stats = df[labels].describe().T[['mean', 'min', 'max', 'std']]
        stats.columns = ['Rata-rata', 'Min', 'Max', 'Std']
        st.dataframe(stats, use_container_width=True)
