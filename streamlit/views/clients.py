import streamlit as st
import numpy as np
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import random

from core import get_clients_summary, apply_chart_style, render_metric_card
from core.ai_analyst import MarineAIAnalyst

def enrich_client_data(df):
    if df.empty: return df
    df['projects_active'] = df['total_orders']
    df['ltv'] = df['ltv'].astype(float)
    
    conditions = [(df['projects_active'] >= 4), (df['projects_active'] >= 2), (df['projects_active'] < 2)]
    choices = ['Rendah', 'Menengah', 'Tinggi']
    df['churn_risk'] = np.select(conditions, choices, default='Menengah')
    return df

def render_growth_matrix(df):
    fig = px.scatter(
        df, x="projects_active", y="ltv", size="ltv", color="churn_risk",
        hover_name="name", text="name", title="Matriks Nilai Klien",
        labels={"projects_active": "Proyek Aktif", "ltv": "Nilai Seumur Hidup (IDR)", "churn_risk": "Profil Risiko"},
        color_discrete_map={"Rendah": "#2ecc71", "Menengah": "#f1c40f", "Tinggi": "#e74c3c"},
        template="plotly_dark", size_max=40
    )
    fig.update_traces(textposition='top center')
    apply_chart_style(fig)
    fig.update_layout(xaxis=dict(tickmode='linear', dtick=1), xaxis_title="Proyek Aktif", yaxis_title="Nilai Seumur Hidup (IDR)")
    return fig

@st.cache_resource
def generate_client_map(df):
    m = folium.Map(location=[20, 10], zoom_start=2, tiles="CartoDB Dark Matter")
    marker_cluster = MarkerCluster().add_to(m)
    
    region_centers = {
        "Asia Pacific": [-2.5, 120.0], "Europe": [48.0, 10.0], "North America": [40.0, -100.0],
        "Middle East": [25.0, 45.0], "SE Asia": [3.0, 101.0], "Africa": [0.0, 20.0], "South America": [-15.0, -60.0]
    }
    
    for _, row in df.iterrows():
        region = row.get('region', 'Asia Pacific')
        center = region_centers.get(region, region_centers["Asia Pacific"])
        lat = center[0] + random.uniform(-5.0, 5.0)
        lon = center[1] + random.uniform(-5.0, 5.0)
        
        color_map = {"Rendah": "green", "Menengah": "orange", "Tinggi": "red"}
        icon_color = color_map.get(row['churn_risk'], "blue")
        
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{row['name']}</b><br>LTV: Rp {row['ltv']/1e9:.1f}M",
            tooltip=f"{row['name']} ({row['industry']})",
            icon=folium.Icon(color=icon_color, icon="user", prefix="fa")
        ).add_to(marker_cluster)
    return m

def render_map(df):
    m = generate_client_map(df)
    st_folium(m, height=500, use_container_width=True)

def render_clients_page():
    st.markdown("## 🤝 Portofolio Klien Strategis")
    st.caption("Analisis & Distribusi CRM Tingkat Lanjut")
    
    raw_df = get_clients_summary()
    if raw_df.empty:
        st.info("Tidak ada data klien dimuat.")
        return
        
    df = enrich_client_data(raw_df)

    # --- AI Analyst Section ---
    with st.expander("🤖 AI Strategic Analyst", expanded=True):
        analysis = MarineAIAnalyst.analyze_clients(df)
        
        # Display Insights
        if analysis['insights']:
            cols = st.columns(len(analysis['insights']))
            for idx, insight in enumerate(analysis['insights']):
                with cols[idx]:
                    st.success(f"**{insight['title']}**")
                    st.caption(insight['desc'])
        else:
            st.info("AI belum menemukan pola signifikan saat ini.")
    
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Total Klien", len(df), "+3% MoM", "#38bdf8", help_text="Total klien aktif dalam portofolio saat ini.")
    
    avg_prj = df['projects_active'].mean()
    with c2: render_metric_card("Rata-rata Proyek", f"{avg_prj:.1f}", "Beban Operasional", "#fbbf24", help_text="Rata-rata jumlah proyek aktif per klien.")
    
    high_value_sum = df[df['ltv'] > 3000000000]['ltv'].sum()
    with c3: render_metric_card("Pipeline Premium", f"Rp {high_value_sum/1e9:.1f}M", "Akun Utama", "#2dd4bf", help_text="Total nilai LTV dari klien dengan status prioritas tinggi.")
    
    at_risk = len(df[df['churn_risk'] == 'Tinggi'])
    with c4: render_metric_card("Risiko Churn", at_risk, "Perlu Atensi", "#ef4444", help_text="Klien dengan aktivitas rendah yang memerlukan tindak lanjut segera.")
    
    st.markdown("---")
    
    tab_matrix, tab_map, tab_list = st.tabs(["🚀 Matriks Nilai", "🌍 Kehadiran Geografis", "📋 Direktori"])
    
    with tab_matrix:
        c_chart, c_insight = st.columns([3, 1])
        with c_chart: st.plotly_chart(render_growth_matrix(df), use_container_width=True)
        with c_insight:
            st.markdown("#### 💡 Audit Strategi")
            st.info("**Mitra Kunci**: Klien dengan banyak proyek aktif dan LTV tinggi.")
            st.warning("**Potensi Upsell**: Klien dengan LTV tinggi tetapi sedikit proyek aktif.")
            
    with tab_map:
        st.subheader("Jejak Klien Global")
        render_map(df)
        
    with tab_list:
        col_search, col_sort = st.columns([3, 1])
        text_search = col_search.text_input("🔍 Cari Klien", placeholder="Ketik nama...")
        sort_opt = col_sort.selectbox("Urutkan Berdasarkan", ["LTV (Tinggi-Rendah)", "Proyek (Tinggi-Rendah)", "Nama (A-Z)"])

        filtered_df = df.copy()
        if text_search:
            filtered_df = filtered_df[filtered_df['name'].str.contains(text_search, case=False)]
            
        if sort_opt == "LTV (Tinggi-Rendah)": filtered_df = filtered_df.sort_values('ltv', ascending=False)
        elif sort_opt == "Proyek (Tinggi-Rendah)": filtered_df = filtered_df.sort_values('projects_active', ascending=False)
        else: filtered_df = filtered_df.sort_values('name')
            
        st.dataframe(
            filtered_df[['name', 'industry', 'region', 'projects_active', 'ltv', 'churn_risk']],
            use_container_width=True, hide_index=True,
            column_config={
                "name": "Nama Klien",
                "ltv": st.column_config.ProgressColumn("Nilai Seumur Hidup (IDR)", min_value=0, max_value=int(df['ltv'].max()), format="Rp %d"),
                "churn_risk": st.column_config.Column("Profil Risiko", width="small"),
                "projects_active": st.column_config.Column("Proyek Aktif")
            }
        )
