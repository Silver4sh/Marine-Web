
import streamlit as st
import pandas as pd
from dashboard.core import get_data_water, page_heatmap

def render_environ_heatmap():
    st.markdown("## 🔥 Peta Panas Lingkungan")
    df = get_data_water()
    
    if not df.empty and 'latest_timestamp' in df.columns:
        # Date Logic
        valid_dates = pd.to_datetime(df['latest_timestamp'], errors='coerce').dropna()
        if not valid_dates.empty:
            df['latest_timestamp'] = pd.to_datetime(df['latest_timestamp'])
            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
            if min_d == max_d: min_d -= pd.Timedelta(days=1)
            
            st.markdown("### 🗓️ Filter Tanggal")
            dr = st.slider("Rentang:", min_value=min_d, max_value=max_d, value=(min_d, max_d), format="DD/MM/YY")
            df = df[(df['latest_timestamp'].dt.date >= dr[0]) & (df['latest_timestamp'].dt.date <= dr[1])]

    cat = st.radio("Pilih Kategori", ["Kualitas Air", "Oseanografi"], horizontal=True)
    c1, c2 = st.columns(2)
    if cat == "Kualitas Air":
         with c1: st.write("**Salinitas**"); page_heatmap(df, "salinitas")
         with c2: st.write("**Kekeruhan**"); page_heatmap(df, "turbidity")
         st.write("**Oksigen**"); page_heatmap(df, "oxygen")
    else:
         with c1: st.write("**Arus**"); page_heatmap(df, "current")
         with c2: st.write("**Pasang Surut**"); page_heatmap(df, "tide")
         st.write("**Densitas**"); page_heatmap(df, "density")

def render_buoy_monitoring():
    st.markdown("## 📡 Pemantauan Buoy")
    
    # Mock data for buoys since we don't have a specific backend function yet
    buoys = [
        {"id": "B-001", "location": "Selat Sunda", "status": "Active", "battery": "85%", "last_update": "Baru saja"},
        {"id": "B-002", "location": "Teluk Jakarta", "status": "Active", "battery": "92%", "last_update": "5 mnt lalu"},
        {"id": "B-003", "location": "Laut Jawa", "status": "Maintenance", "battery": "12%", "last_update": "1 jam lalu"},
        {"id": "B-004", "location": "Selat Bali", "status": "Active", "battery": "78%", "last_update": "10 mnt lalu"},
    ]
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Buoy", len(buoys))
    with c2: st.metric("Buoy Aktif", len([b for b in buoys if b['status'] == 'Active']))
    with c3: st.metric("Perlu Perawatan", len([b for b in buoys if b['status'] != 'Active']))
    
    st.markdown("### Daftar Buoy")
    
    for buoy in buoys:
        with st.expander(f"Buoy {buoy['id']} - {buoy['location']}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.write(f"**Status:** {buoy['status']}")
            with col2: st.write(f"**Baterai:** {buoy['battery']}")
            with col3: st.write(f"**Update:** {buoy['last_update']}")
            with col4: st.button("Detail", key=f"btn_buoy_{buoy['id']}")

def render_environment_page():
    st.markdown("# 🌊 Pemantauan Lingkungan")
    tab1, tab2 = st.tabs(["🔥 Peta Panas", "📡 Pemantauan Buoy"])
    
    with tab1:
        render_environ_heatmap()
        
    with tab2:
        render_buoy_monitoring()
