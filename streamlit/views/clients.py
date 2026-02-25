"""
views/clients.py
================
UI layer untuk halaman Portofolio Klien Strategis.

Tanggung jawab:
  - Enrichment data klien (churn risk scoring)
  - Scatter matrix nilai klien
  - Peta sebaran geografis (Folium)
  - Direktori klien dengan search & sort
  - AI strategic insights
"""
import hashlib

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from core import apply_chart_style, get_clients_summary, render_metric_card
from core.ai_analyst import MarineAIAnalyst


# ---------------------------------------------------------------------------
# Data enrichment (business logic — no UI)
# ---------------------------------------------------------------------------

def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Tambahkan kolom projects_active dan churn_risk ke dataframe klien."""
    if df.empty:
        return df

    df = df.copy()
    df['projects_active'] = df['total_orders']
    df['ltv']             = df['ltv'].astype(float)

    conditions = [df['projects_active'] >= 4, df['projects_active'] >= 2, df['projects_active'] < 2]
    choices    = ['Rendah', 'Menengah', 'Tinggi']
    df['churn_risk'] = np.select(conditions, choices, default='Menengah')
    return df


def _stable_jitter(seed_str: str, scale: float = 5.0) -> tuple[float, float]:
    """Hasilkan offset lat/lon deterministik dari string seed — bukan random tiap render."""
    digest = hashlib.md5(seed_str.encode()).digest()
    lat_off = (digest[0] / 255.0 - 0.5) * scale * 2
    lon_off = (digest[1] / 255.0 - 0.5) * scale * 2
    return lat_off, lon_off


# ---------------------------------------------------------------------------
# Chart builders (private)
# ---------------------------------------------------------------------------

def _build_growth_matrix(df: pd.DataFrame):
    """Scatter chart: proyek aktif vs LTV, ukuran & warna = churn risk."""
    fig = px.scatter(
        df, x="projects_active", y="ltv",
        size="ltv", color="churn_risk",
        hover_name="name", text="name",
        title="Matriks Nilai Klien",
        labels={
            "projects_active": "Proyek Aktif",
            "ltv":             "Nilai Seumur Hidup (IDR)",
            "churn_risk":      "Profil Risiko",
        },
        color_discrete_map={"Rendah": "#2ecc71", "Menengah": "#f1c40f", "Tinggi": "#e74c3c"},
        template="plotly_dark",
        size_max=40,
    )
    fig.update_traces(textposition='top center')
    apply_chart_style(fig)
    fig.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),
        xaxis_title="Proyek Aktif",
        yaxis_title="Nilai Seumur Hidup (IDR)",
    )
    return fig


_REGION_CENTERS: dict[str, list[float]] = {
    "Asia Pacific":  [-2.5, 120.0],
    "Europe":        [48.0, 10.0],
    "North America": [40.0, -100.0],
    "Middle East":   [25.0, 45.0],
    "SE Asia":       [3.0, 101.0],
    "Africa":        [0.0, 20.0],
    "South America": [-15.0, -60.0],
}
_ICON_COLORS = {"Rendah": "green", "Menengah": "orange", "Tinggi": "red"}


@st.cache_data(ttl=600, show_spinner=False)
def _build_client_map(df_json: str) -> folium.Map:
    """
    Membuat Folium map dengan marker cluster klien.
    Menggunakan df_json (JSON string) agar cache berfungsi dengan benar.
    Posisi marker deterministik (hashlib seed) — tidak berubah tiap refresh.
    """
    df  = pd.read_json(df_json)
    m   = folium.Map(location=[20, 10], zoom_start=2, tiles="CartoDB Dark Matter")
    mc  = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        region = row.get('region', 'Asia Pacific')
        center = _REGION_CENTERS.get(region, _REGION_CENTERS["Asia Pacific"])
        seed   = f"{row['name']}_{region}"
        d_lat, d_lon = _stable_jitter(seed)

        folium.Marker(
            location=[center[0] + d_lat, center[1] + d_lon],
            popup=f"<b>{row['name']}</b><br>LTV: Rp {row['ltv']/1e9:.1f}M",
            tooltip=f"{row['name']} ({row.get('industry', '-')})",
            icon=folium.Icon(
                color=_ICON_COLORS.get(row.get('churn_risk', 'Menengah'), 'blue'),
                icon="user", prefix="fa",
            ),
        ).add_to(mc)

    return m


# ---------------------------------------------------------------------------
# Section renderers (private UI helpers)
# ---------------------------------------------------------------------------

def _render_ai_banner(df: pd.DataFrame) -> None:
    analysis = MarineAIAnalyst.analyze_clients(df)
    if not analysis['insights']:
        return
    with st.expander("🤖 AI Strategic Analyst", expanded=True):
        cols = st.columns(len(analysis['insights']))
        for col, insight in zip(cols, analysis['insights']):
            with col:
                st.success(f"**{insight['title']}**")
                st.caption(insight['desc'])


def _render_kpi_row(df: pd.DataFrame) -> None:
    c1, c2, c3, c4 = st.columns(4)

    avg_prj        = df['projects_active'].mean()
    high_val_sum   = df[df['ltv'] > 3_000_000_000]['ltv'].sum()
    at_risk        = int((df['churn_risk'] == 'Tinggi').sum())

    with c1:
        render_metric_card("Total Klien",     len(df),                      "+3% MoM",           "#38bdf8",
                           help_text="Total klien aktif dalam portofolio.")
    with c2:
        render_metric_card("Rata-rata Proyek", f"{avg_prj:.1f}",            "Beban Operasional",  "#fbbf24",
                           help_text="Rata-rata jumlah proyek aktif per klien.")
    with c3:
        render_metric_card("Pipeline Premium", f"Rp {high_val_sum/1e9:.1f}M", "Akun Utama",       "#2dd4bf",
                           help_text="Total LTV klien prioritas tinggi.")
    with c4:
        render_metric_card("Risiko Churn",    at_risk,                      "Perlu Atensi",       "#ef4444",
                           help_text="Klien dengan aktivitas rendah yang perlu tindak lanjut.")


def _render_matrix_tab(df: pd.DataFrame) -> None:
    c_chart, c_insight = st.columns([3, 1])
    with c_chart:
        st.plotly_chart(_build_growth_matrix(df), width='stretch')
    with c_insight:
        st.markdown("#### 💡 Audit Strategi")
        st.info("**Mitra Kunci**: Klien dengan banyak proyek aktif dan LTV tinggi.")
        st.warning("**Potensi Upsell**: Klien dengan LTV tinggi tetapi sedikit proyek aktif.")


def _render_map_tab(df: pd.DataFrame) -> None:
    st.subheader("Jejak Klien Global")
    m = _build_client_map(df.to_json())
    st_folium(m, height=500, width='stretch')


def _render_directory_tab(df: pd.DataFrame) -> None:
    col_search, col_sort = st.columns([3, 1])
    search   = col_search.text_input("🔍 Cari Klien", placeholder="Ketik nama...")
    sort_opt = col_sort.selectbox("Urutkan", ["LTV (Tinggi-Rendah)", "Proyek (Tinggi-Rendah)", "Nama (A-Z)"])

    filtered = df.copy()
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]

    if sort_opt == "LTV (Tinggi-Rendah)":
        filtered = filtered.sort_values('ltv', ascending=False)
    elif sort_opt == "Proyek (Tinggi-Rendah)":
        filtered = filtered.sort_values('projects_active', ascending=False)
    else:
        filtered = filtered.sort_values('name')

    st.dataframe(
        filtered[['name', 'industry', 'region', 'projects_active', 'ltv', 'churn_risk']],
        width='stretch',
        hide_index=True,
        column_config={
            "name":            "Nama Klien",
            "industry":        "Industri",
            "region":          "Region",
            "projects_active": st.column_config.Column("Proyek Aktif"),
            "ltv":             st.column_config.ProgressColumn(
                                   "Nilai Seumur Hidup (IDR)",
                                   min_value=0,
                                   max_value=int(df['ltv'].max()) if not df.empty else 1,
                                   format="Rp %d",
                               ),
            "churn_risk":      st.column_config.Column("Profil Risiko", width="small"),
        },
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_clients_page() -> None:
    """Entry point halaman Klien — dipanggil dari main.py."""
    st.markdown("## 🤝 Portofolio Klien Strategis")
    st.caption("Analisis & Distribusi CRM Tingkat Lanjut")

    raw = get_clients_summary()
    if raw.empty:
        st.info("Tidak ada data klien.")
        return

    df = _enrich(raw)

    _render_ai_banner(df)
    st.markdown("---")
    _render_kpi_row(df)
    st.markdown("---")

    tab_matrix, tab_map, tab_list = st.tabs([
        "🚀 Matriks Nilai",
        "🌍 Kehadiran Geografis",
        "📋 Direktori",
    ])

    with tab_matrix:
        _render_matrix_tab(df)
    with tab_map:
        _render_map_tab(df)
    with tab_list:
        _render_directory_tab(df)
