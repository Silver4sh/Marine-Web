"""core/views/kpi_dashboard.py — Executive KPI Dashboard"""
import streamlit as st
import pandas as pd
from core.ui.charts import gauge_chart, apply_chart_style
from db.repos.settings import get_system_settings


def _section_header(icon: str, title: str, subtitle: str = "") -> None:
    sub = f'<div style="font-size:0.78rem;color:#8ba3c0;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;margin-top:4px;">
            <span style="font-size:1.15rem;">{icon}</span>
            <div>
                <div style="font-family:'Outfit',sans-serif;font-size:0.95rem;font-weight:800;color:#f0f6ff;">{title}</div>
                {sub}
            </div>
        </div>
    """, unsafe_allow_html=True)


def _demo_kpi_data() -> dict:
    return {
        "revenue": 4_200_000_000,
        "revenue_target": 5_000_000_000,
        "otd_rate": 88.5,
        "utilization_rate": 75.0,
        "vessel_perf": pd.DataFrame([
            {"Kapal": "KM Nusantara", "OTD": 95, "Util": 80, "Margin (%)": 25},
            {"Kapal": "KM Bahari",    "OTD": 82, "Util": 65, "Margin (%)": 18},
            {"Kapal": "KM Sabuk",     "OTD": 90, "Util": 70, "Margin (%)": 22},
        ])
    }


def render_kpi_dashboard():
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">📊</div>
            <div>
                <p class="page-header-title">Executive KPI Dashboard</p>
                <p class="page-header-subtitle">High-level metrics · revenue · fleet performance</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    data = _demo_kpi_data()
    settings = get_system_settings()
    target = float(settings.get("revenue_target_monthly", data["revenue_target"]))

    # Main Gauges
    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        rev_pct = min((data["revenue"] / target) * 100, 150) if target else 0
        st.plotly_chart(
            gauge_chart(round(rev_pct, 1), "Target Revenue", 100, "%", (60, 90)),
            use_container_width=True, config={"displayModeBar": False}
        )
    with g2:
        st.plotly_chart(
            gauge_chart(data["otd_rate"], "On-Time Delivery", 100, "%", (70, 90)),
            use_container_width=True, config={"displayModeBar": False}
        )
    with g3:
        st.plotly_chart(
            gauge_chart(data["utilization_rate"], "Utilisasi Armada", 100, "%", (50, 80)),
            use_container_width=True, config={"displayModeBar": False}
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Financial breakdown pseudo-chart
    _section_header("💰", "Performa Finansial & Margin", "Trend mingguan")
    
    import plotly.express as px
    trend_df = pd.DataFrame({
        "Minggu": ["M1", "M2", "M3", "M4"],
        "Revenue": [1.1, 0.9, 1.2, 1.0] # dalam miliar
    })
    fig = px.bar(trend_df, x="Minggu", y="Revenue", title="Revenue (Miliar Rp)",
                 color_discrete_sequence=["#38bdf8"])
    apply_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)

    # Vessel side-by-side
    _section_header("🚢", "Perbandingan Performa Armada")
    from core.ui.helpers import render_beautiful_table
    df = data["vessel_perf"]
    
    render_beautiful_table(df, col_config={
        "OTD": {"type": "progress", "max_val": 100, "color_map": {"Kapal": "#22c55e"}},
        "Util": {"type": "progress", "max_val": 100, "color_map": {"Kapal": "#fbbf24"}},
        "Margin (%)": {"type": "progress", "max_val": 50, "color_map": {"Kapal": "#818cf8"}}
    })
