import streamlit as st
import pandas as pd
import altair as alt
from dashboard.core import get_data_water, page_heatmap
from dashboard.core.database import get_buoy_list, get_buoy_history

def render_chart(df, x_col, y_col, color_col, title):
    if df.empty or y_col not in df.columns:
        st.info("Tidak ada data untuk ditampilkan.")
        return
    
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X(x_col, title="Waktu"),
        y=alt.Y(y_col, title=""), # Empty String for No Title
        color=alt.Color(color_col, legend=None),
        tooltip=[x_col, y_col, color_col]
    ).properties(height=300)
    
    if title:
        chart = chart.properties(title=title)
    
    chart = chart.interactive()
    
    st.altair_chart(chart, use_container_width=True)

def render_sparkline(df, y_col, title, color="#0ea5e9"):
    if df.empty or y_col not in df.columns: return
    
    # Simple Area Chart for "Sparkline" effect
    chart = alt.Chart(df).mark_area(
        line={'color': color},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color=color, offset=0),
                   alt.GradientStop(color='white', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('created_at', axis=alt.Axis(labels=False, grid=False, title="")),
        y=alt.Y(y_col, axis=alt.Axis(labels=True, grid=True, title="")),
        tooltip=['created_at', y_col]
    ).properties(
        title=title,
        height=150
    )
    st.altair_chart(chart, use_container_width=True)

def render_environ_heatmap():
    st.markdown("## 🔥 Peta Panas Lingkungan")
    df = get_data_water()
    
    if not df.empty and 'latest_timestamp' in df.columns:
        df['latest_timestamp'] = pd.to_datetime(df['latest_timestamp'])
        
        # Global Filter: Last 7 Days (1 Week)
        max_date = df['latest_timestamp'].max()
        start_date = max_date - pd.Timedelta(days=7)
        df = df[df['latest_timestamp'] >= start_date]

    cat = st.radio("Pilih Kategori", ["Kualitas Air", "Oseanografi"], horizontal=True)
    c1, c2 = st.columns(2)
    
    if cat == "Kualitas Air":
         with c1: st.write("**Salinitas**"); page_heatmap(df, "salinitas")
         with c2: st.write("**Kekeruhan**"); page_heatmap(df, "turbidity")
         st.write("**Oksigen**"); page_heatmap(df, "oxygen")
    else:
         # Auto-filter logic removed as df is already filtered
         chart_df = df.copy()
         if not chart_df.empty and 'latest_timestamp' in chart_df.columns:
            # Calculate Daily Average (Spatial Average across all buoys)
            chart_df['date'] = chart_df['latest_timestamp'].dt.date
            # Ensure numeric columns are numeric before grouping
            chart_df['current'] = pd.to_numeric(chart_df['current'], errors='coerce')
            chart_df['tide'] = pd.to_numeric(chart_df['tide'], errors='coerce')
            
            # Group by DATE only (Average across all buoys)
            chart_df = chart_df.groupby(['date'])[['current', 'tide']].mean().reset_index()
            chart_df['id_buoy'] = 'Rata-rata Wilayah'
            
            # Convert date back to string or datetime for Altair compatibility
            chart_df['latest_timestamp'] = pd.to_datetime(chart_df['date'])

         # Prepare data for charts (ensure sorted by time)
         chart_df = chart_df.sort_values("latest_timestamp") if not chart_df.empty else pd.DataFrame()
         
         st.subheader("Rerata Arus (Current)")
         render_chart(chart_df, 'latest_timestamp', 'current', 'id_buoy', None)
         
         st.subheader("Rerata Pasang Surut (Tide)")
         render_chart(chart_df, 'latest_timestamp', 'tide', 'id_buoy', None)

         st.markdown("### Densitas")

         page_heatmap(df, "density")

def render_buoy_monitoring():
    st.markdown("## 📡 Pemantauan Buoy")
    
    # Fetch real buoy data
    buoys_df = get_buoy_list()
    
    if buoys_df.empty:
        st.info("Belum ada data buoy yang aktif.")
        return

    # Metrics
    total = len(buoys_df)
    active = len(buoys_df[buoys_df['status'] == 'Active'])
    maint = total - active
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Buoy", total)
    with c2: st.metric("Buoy Aktif", active)
    with c3: st.metric("Perlu Perawatan", maint)
    
    st.markdown("### Daftar Buoy")
    
    for _, buoy in buoys_df.iterrows():
        b_id = buoy['code_buoy']
        loc = buoy.get('location') or 'Lokasi Tidak Diketahui'
        status = buoy['status']
        batt = buoy.get('battery', 'N/A')
        last_up = buoy.get('last_update')
        
        with st.expander(f"Buoy {b_id} - {loc}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.write(f"**Status:** {status}")
            with col2: st.write(f"**Baterai:** {batt}")
            with col3: st.write(f"**Update:** {last_up}")
            with col4: 
                if st.button("Refresh Data", key=f"btn_refresh_{b_id}"):
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("#### 📊 Data Historis")
            # Fetch history for this buoy
            hist_df = get_buoy_history(b_id)
            
            if not hist_df.empty:
                hist_df['created_at'] = pd.to_datetime(hist_df['created_at'])
                
                # Filter 7 days (Added Logic)
                start_h = hist_df['created_at'].max() - pd.Timedelta(days=7)
                hist_df = hist_df[hist_df['created_at'] >= start_h]

            if not hist_df.empty:
                # Requested: Salinitas, Kekeruhan, Oksigen, Densitas
                g1, g2 = st.columns(2)
                with g1: render_sparkline(hist_df, 'salinitas', 'Salinitas (ppt)', '#3b82f6')
                with g2: render_sparkline(hist_df, 'turbidity', 'Kekeruhan (NTU)', '#f59e0b')
                
                g3, g4 = st.columns(2)
                with g3: render_sparkline(hist_df, 'oxygen', 'Oksigen Terlarut (mg/L)', '#10b981')
                with g4: render_sparkline(hist_df, 'density', 'Densitas (kg/m³)', '#8b5cf6')
            else:
                st.warning("Data historis tidak tersedia untuk periode ini (7 hari terakhir).")

def render_environment_page():
    st.markdown("# 🌊 Pemantauan Lingkungan")
    tab1, tab2 = st.tabs(["🔥 Peta Panas & Grafik", "📡 Pemantauan Buoy"])
    
    with tab1:
        render_environ_heatmap()
        
    with tab2:
        render_buoy_monitoring()