import streamlit as st
import pandas as pd
import altair as alt
from streamlit.core import get_data_water, page_heatmap
from streamlit.core.database import get_buoy_fleet, get_buoy_history

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
    st.markdown("## 🔥 Enviro Heatmap")
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


@st.dialog("Detail Buoy", width="large")
def view_buoy_detail(b_id, name):
    st.write(f"### {name}")
    st.write(f"**ID Buoy:** {b_id}")
    
    # Fetch Data First to determine Min/Max Date
    hist_df = get_buoy_history(b_id)
    
    if not hist_df.empty:
        hist_df['created_at'] = pd.to_datetime(hist_df['created_at'])
        min_date = hist_df['created_at'].min()
        max_date = hist_df['created_at'].max()
        
        # Filter Date (Default to All Time)
        st.markdown("#### Filter Tanggal")
        d = st.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)
        
        # Apply Filter
        filtered_df = hist_df.copy()
        if isinstance(d, tuple) and len(d) == 2:
            start_date, end_date = pd.to_datetime(d[0]), pd.to_datetime(d[1])
             # Adjust end_date to end of day
            filtered_df = hist_df[(hist_df['created_at'] >= start_date) & (hist_df['created_at'] < end_date + pd.Timedelta(days=1))]
        
        # Render Detailed Charts
        if not filtered_df.empty:
            st.divider()
            st.subheader("📈 Grafik Detail")
            
            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)
            
            with c1: 
                st.caption("Salinitas")
                render_chart(filtered_df, 'created_at', 'salinitas', 'id_buoy', None)
            with c2: 
                st.caption("Kekeruhan")
                render_chart(filtered_df, 'created_at', 'turbidity', 'id_buoy', None)
            with c3: 
                st.caption("Oksigen")
                render_chart(filtered_df, 'created_at', 'oxygen', 'id_buoy', None)
            with c4:
                st.caption("Densitas")
                render_chart(filtered_df, 'created_at', 'density', 'id_buoy', None)
            
            st.divider()
            st.subheader("📄 Data Mentah")
            st.dataframe(filtered_df, use_container_width=True)
        else:
             st.info("Tidak ada data dalam rentang tanggal yang dipilih.")
    else:
        st.warning("Belum ada data historis.")
        
def render_buoy_monitoring():
    st.markdown("## 📡 Pemantauan Buoy")
    
    # Fetch real buoy data
    buoys_df = get_buoy_fleet()
    
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
    
    # Grid Layout (4 Columns)
    cols_per_row = 4
    rows = [buoys_df.iloc[i:i+cols_per_row] for i in range(0, len(buoys_df), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, buoy) in zip(cols, row.iterrows()):
            with col:
                with st.container(border=True):
                    b_id = buoy['code_buoy']
                    loc = buoy.get('location') or 'Lokasi ?'
                    status = buoy['status']
                    batt = buoy.get('battery', '-')
                    last_up = buoy.get('last_update')
                    
                    # Formatting
                    fmt_update = last_up.strftime("%d %b %H:%M") if pd.notnull(last_up) else "-"
                    status_hex = "#22c55e" if status == "Active" else "#f97316" if status == "Maintenance" else "#9ca3af"
                    
                    # Centered Layout using HTML with specific Sizes
                    st.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 2px;'>{b_id}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; color: gray; font-size: 12px; margin-bottom: 8px;'>{loc}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 14px; font-weight: bold; color: {status_hex}; margin-bottom: 12px;'>● {status}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 11px; color: #555; margin-bottom: 10px;'>🔋 {batt} | 🕒 {fmt_update}</div>", unsafe_allow_html=True)
                    
                    if st.button("Detail 🔍", key=f"btn_detail_{b_id}", use_container_width=True):
                        view_buoy_detail(b_id, f"Buoy {b_id} - {loc}")
                


def render_environment_page():
    st.markdown("# 🌊 Enviro Control")
    tab1, tab2 = st.tabs(["🔥 Grafik Heatmap", "📡 Pemantauan Buoy"])
    
    with tab1:
        render_environ_heatmap()
        
    with tab2:
        render_buoy_monitoring()
