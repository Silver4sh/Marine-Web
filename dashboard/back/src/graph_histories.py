import pandas as pd
import altair as alt
import streamlit as st
from back.query.queries import (
    get_buoy_history, 
    get_buoy_list, 
    get_buoy_date_range,
    get_global_date_range, 
    get_aggregated_buoy_history
)

@st.cache_data(ttl=3600)
def load_buoy_list():
    return get_buoy_list()
    
@st.cache_data(ttl=3600)
def load_date_ranges(buoy_id):
    if buoy_id == "All":
        return get_global_date_range()
    return get_buoy_date_range(buoy_id)

def render_history_config(buoy_list, selected_buoy):
    st.subheader("🛠️ Konfigurasi")
    
    st.markdown("---")
    st.write("**Parameter**")
    cols = st.columns(2)
    with cols[0]:
        salinitas = st.checkbox("Salinitas", value=True)
        turbidity = st.checkbox("Kekeruhan")
        current = st.checkbox("Arus")
    with cols[1]:
        oxygen = st.checkbox("Oksigen")
        tide = st.checkbox("Pasang Surut")
        density = st.checkbox("Densitas")
    
    indikator = []
    if salinitas: indikator.append("salinitas")
    if turbidity: indikator.append("turbidity")
    if current: indikator.append("current")
    if oxygen: indikator.append("oxygen")
    if tide: indikator.append("tide")
    if density: indikator.append("density")
    
    return indikator

def render_history_chart(df, indikator, selected_buoy):
    df["created_at"] = pd.to_datetime(df["created_at"])
    
    rename_map = {
        "salinitas": "Salinitas",
        "turbidity": "Kekeruhan",
        "current": "Arus",
        "oxygen": "Oksigen",
        "tide": "Pasang Surut",
        "density": "Densitas"
    }
    df = df.rename(columns=rename_map)
    indikator_labels = [rename_map.get(x, x) for x in indikator]

    left_indicators = [ind for ind in indikator_labels if ind != 'Densitas']
    right_indicators = [ind for ind in indikator_labels if ind == 'Densitas']
    
    base = alt.Chart(df).encode(
        x=alt.X("created_at:T", title="Waktu", 
                axis=alt.Axis(format="%b %d %H:%M", labelAngle=-45))
    )
    
    layers = []
    
    if left_indicators:
        left_chart = base.transform_fold(
            left_indicators,
            as_=["parameter", "value"]
        ).mark_line(
            strokeWidth=2.5,
            opacity=0.9
        ).encode(
            y=alt.Y("value:Q", title="Nilai Sensor", 
                    axis=alt.Axis(titleColor='#38bdf8')),
            color=alt.Color("parameter:N", title="Metrik",
                           scale=alt.Scale(range=['#38bdf8', '#2dd4bf', '#818cf8', '#f472b6', '#fbbf24'])),         
            tooltip=["created_at:T", "parameter:N", "value:Q"]
        )
        layers.append(left_chart)
    
    if right_indicators:
        right_chart = base.transform_fold(
            right_indicators,
            as_=["parameter", "value"]
        ).mark_line(
            strokeWidth=2.5,
            strokeDash=[5, 5],
            color='#f472b6'
        ).encode(
            y=alt.Y("value:Q", title="Densitas",
                    axis=alt.Axis(titleColor='#f472b6', orient='right')),
            tooltip=["created_at:T", "parameter:N", "value:Q"]
        )
        layers.append(right_chart)
        
    if layers:
        final_chart = alt.layer(*layers).resolve_scale(
            y='independent'
        ).properties(
            title=f"Telemetri: {selected_buoy}",
            height=450
        ).configure(
            background='transparent'
        ).configure_axis(
            labelFontSize=11,
            titleFontSize=12,
            labelColor='#94a3b8',
            titleColor='#f8fafc',
            gridColor='rgba(148, 163, 184, 0.1)',
            domainColor='rgba(148, 163, 184, 0.1)'
        ).configure_legend(
            titleFontSize=12,
            labelFontSize=11,
            labelColor='#f8fafc',
            titleColor='#f8fafc',
            padding=10,
            cornerRadius=5,
            fillColor='rgba(0,0,0,0.5)',
            strokeColor='rgba(255,255,255,0.1)'
        ).configure_title(
            fontSize=16,
            font='Plus Jakarta Sans',
            color='#38bdf8',
            anchor='start'
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(final_chart, use_container_width=True)
        
        with st.expander("📊 Ringkasan Statistik", expanded=True):
            stats = df[indikator_labels].describe().T[['mean', 'min', 'max', 'std']]
            stats.columns = ['Rata-rata', 'Min', 'Max', 'Std']
            stats.index = [x.title() for x in stats.index]
            st.dataframe(stats, use_container_width=True)

def page_history_graph():
    buoy_df = load_buoy_list()
    
    if buoy_df.empty:
        st.warning("⚠️ Koneksi database terputus atau tidak ada buoy yang ditemukan.")
        return
        
    buoy_list = ["All"] + buoy_df["id_buoy"].tolist()
    
    col1, col2 = st.columns([1, 4]) # Adjusted ratio for better fit
    
    with col1:
        # Configuration Section
        selected_buoy = st.selectbox("Pilih Node Buoy", buoy_list)
        range_df = load_date_ranges(selected_buoy)
        
        is_data_avail = not (range_df.empty or pd.isna(range_df.iloc[0]['min_date']))
        
        if is_data_avail:
            indikator = render_history_config(buoy_list, selected_buoy)
        else:
             st.info("Tidak ada data tersedia untuk buoy ini.")
             indikator = []

    with col2:
        if not is_data_avail: return

        if not indikator:
            st.warning("Pilih setidaknya satu parameter untuk divisualisasikan.")
            return

        min_date_db = pd.to_datetime(range_df.iloc[0]['min_date']).date()
        max_date_db = pd.to_datetime(range_df.iloc[0]['max_date']).date()
        
        if min_date_db == max_date_db:
            min_date_db = min_date_db - pd.Timedelta(days=1)

        st.write("#### 📅 Rentang Waktu")
        date_range = st.slider(
            "Pilih range tanggal", 
            min_value=min_date_db,
            max_value=max_date_db,
            value=(min_date_db, max_date_db),
            format="DD/MM/YY",
            label_visibility="collapsed"
        )
        
        with st.spinner(f"Mengambil data untuk {selected_buoy}..."):
            if selected_buoy == "All":
                df = get_aggregated_buoy_history(date_range[0], date_range[1])
            else:
                df = get_buoy_history(selected_buoy, date_range[0], date_range[1])
        
        if df.empty:
            st.warning("Tidak ada data ditemukan dalam rentang waktu yang dipilih.")
            return
            
        render_history_chart(df, indikator, selected_buoy)

if __name__ == "__main__":
    page_history_graph()