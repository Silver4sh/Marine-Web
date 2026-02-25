"""
views/monitoring.py
===================
UI layer untuk halaman Monitoring.

Tanggung jawab:
  - Merender metrik, chart, dan AI insights
  - TIDAK memanggil database secara langsung
  - Semua data didapat dari core.services.load_monitoring_data()
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from core import (
    render_metric_card, apply_chart_style,
    render_vessel_list_column, get_status_color,
    get_revenue_analysis, load_monitoring_data,
    compute_order_insight, compute_fleet_health_pct,
)
from core.ai_analyst import MarineAIAnalyst
from core.config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS


# ---------------------------------------------------------------------------
# UI helpers (private)
# ---------------------------------------------------------------------------

def _render_ai_insight(insight: dict) -> None:
    """Merender satu baris AI insight sebagai alert Streamlit yang sesuai tipe."""
    text = f"**{insight['title']}**\n\n{insight['desc']}"
    itype = insight.get('type', 'info')
    if itype == 'critical':
        st.error(text)
    elif itype == 'warning':
        st.warning(text)
    elif itype == 'positive':
        st.success(text)
    else:
        st.info(text)


def _render_revenue_chart(rev_df: pd.DataFrame) -> None:
    """Merender bar chart arus pendapatan bulanan."""
    fig = px.bar(
        rev_df, x='month', y='revenue',
        title="Arus Pendapatan Bulanan",
        template="plotly_dark",
        color='revenue',
        color_continuous_scale=['#0f172a', '#38bdf8'],
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    apply_chart_style(fig)
    st.plotly_chart(fig, width='stretch')

    # Revenue growth insight
    if len(rev_df) > 1:
        last  = rev_df.iloc[-1]['revenue']
        prev  = rev_df.iloc[-2]['revenue']
        growth = ((last - prev) / prev * 100) if prev > 0 else 0
        insight = MarineAIAnalyst.analyze_financials(
            {'delta_revenue': growth}
        )['insights'][0]['desc']
        st.caption(f"🤖 {insight}")


def _render_order_chart(orders: dict) -> None:
    """Merender pie chart distribusi status pesanan."""
    order_df = pd.DataFrame([
        {"Status": "Selesai",  "Count": orders.get('completed', 0)},
        {"Status": "Terbuka",  "Count": orders.get('open', 0)},
        {"Status": "Berjalan", "Count": orders.get('on_progress', 0)},
    ])
    fig = px.pie(
        order_df, values='Count', names='Status', hole=0.7,
        title="Distribusi Pesanan", template="plotly_dark",
        color_discrete_sequence=['#2dd4bf', '#f472b6', '#fbbf24'],
    )
    apply_chart_style(fig)
    st.plotly_chart(fig, width='stretch')
    st.caption(f"🤖 {compute_order_insight(orders)}")


# ---------------------------------------------------------------------------
# Metric cards row
# ---------------------------------------------------------------------------

def _render_metrics(fleet: dict, orders: dict, financial: dict, role: str) -> None:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric_card(
            "Kapal Beroperasi", fleet.get('operating', 0),
            f"{fleet.get('maintenance', 0)} dalam Perawatan", "#fbbf24",
            help_text="Jumlah kapal yang aktif beroperasi saat ini.",
        )

    with c2:
        pending = orders.get('on_progress', 0) + orders.get('in_completed', 0)
        render_metric_card(
            "Pesanan Tertunda", pending, "Perlu Tindakan", "#f472b6",
            help_text="Total pesanan yang sedang berjalan atau belum selesai.",
        )

    with c3:
        if role in (ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM):
            revenue = financial.get('total_revenue', 0)
            delta   = financial.get('delta_revenue', 0.0)
            rev_str = f"Rp {revenue:,.0f}" if revenue < 1e9 else f"Rp {revenue/1e9:.1f}M"
            color   = "#ef4444" if delta < 0 else "#38bdf8"
            render_metric_card(
                "Pendapatan", rev_str, f"{delta:+.1f}% vs bulan lalu", color,
                help_text="Total pendapatan kotor bulan ini dibandingkan bulan lalu.",
            )
        else:
            health = compute_fleet_health_pct(fleet)
            render_metric_card(
                "Kesehatan Armada", f"{health}%", "Operasional", "#38bdf8",
                help_text="Persentase kapal yang siap beroperasi.",
            )

    with c4:
        util_pct = (fleet.get('operating', 0) / max(fleet.get('total_vessels', 1), 1)) * 100
        ai_desc  = MarineAIAnalyst.analyze_fleet(util_pct)['insights'][0]['desc']
        render_metric_card(
            "Task Selesai", orders.get('completed', 0), "Analisis AI Aktif", "#2dd4bf",
            help_text=f"Analisis AI: {ai_desc}",
        )


# ---------------------------------------------------------------------------
# Main sections
# ---------------------------------------------------------------------------

def _render_operational_section(fleet: dict, orders: dict, financial: dict, role: str) -> None:
    """Merender kolom kiri: chart tren operasional."""
    st.subheader("📊 Tren Operasional")

    if role in (ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM):
        rev_df = get_revenue_analysis()
        if not rev_df.empty:
            _render_revenue_chart(rev_df)
        else:
            st.info("Data pendapatan tidak tersedia.")
    else:
        if orders:
            _render_order_chart(orders)


def _render_quick_actions(fleet: dict, role: str) -> None:
    """Merender kolom kanan: tombol aksi cepat dan ringkasan armada."""
    st.subheader("⚡ Tindakan Cepat")

    if role == ROLE_ADMIN:
        if st.button("👨‍💼 Manajemen Pengguna", width='stretch'):
            st.session_state.current_page = "👨‍💼 Manajemen Pengguna"
            st.rerun()
        if st.button("🔧 Konfigurasi Sistem", width='stretch'):
            st.session_state.current_page = "🔧 Pengaturan"
            st.rerun()
    elif role == ROLE_OPERATIONS:
        if st.button("🗺️ Buka Peta Kapal", width='stretch'):
            st.session_state.current_page = "🗺️ Peta Kapal"
            st.rerun()

    st.markdown("### 🚢 Ringkasan Armada")

    fleet_data = pd.DataFrame([
        {"Status": "Beroperasi", "Count": fleet.get('operating', 0)},
        {"Status": "Idle",       "Count": fleet.get('idle', 0)},
        {"Status": "Perawatan",  "Count": fleet.get('maintenance', 0)},
    ])
    max_val = int(max(fleet.get('total_vessels', 10), 1))
    st.dataframe(
        fleet_data,
        hide_index=True,
        width='stretch',
        column_config={
            "Status": "Status",
            "Count": st.column_config.ProgressColumn(
                "Jumlah", format="%d", min_value=0, max_value=max_val
            ),
        },
    )


def render_overview_tab(fleet: dict, orders: dict, financial: dict, role: str) -> None:
    st.markdown("## 📊 Overview")

    _render_metrics(fleet, orders, financial, role)
    st.markdown("<br>", unsafe_allow_html=True)

    c_left, c_right = st.columns([2, 1])
    with c_left:
        _render_operational_section(fleet, orders, financial, role)
    with c_right:
        _render_quick_actions(fleet, role)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_monitoring_view() -> None:
    """Entry point halaman Monitoring — dipanggil dari main.py."""
    role = st.session_state.user_role

    with st.spinner("🚀 Sinkronisasi data..."):
        data = load_monitoring_data(role)

    render_overview_tab(data['fleet'], data['orders'], data['financial'], role)

    # --- AI Cognitive Layer ---
    rev_growth   = data['financial'].get('delta_revenue', 0) if data['financial'] else 0
    util         = (data['fleet'].get('operating', 0) / max(data['fleet'].get('total_vessels', 1), 1)) * 100
    anomaly_count = 0

    churn_count = 0
    clients = data.get('clients')
    if hasattr(clients, 'empty') and not clients.empty and 'churn_risk' in clients.columns:
        churn_count = int((clients['churn_risk'] == 'Tinggi').sum())

    holistic = MarineAIAnalyst.analyze_holistic(
        {'delta_revenue': rev_growth},
        {'utilization': util},
        anomaly_count,
        churn_count,
    )

    if holistic['insights']:
        st.markdown("---")
        st.subheader("🧠 Analisis Kognitif (Cross-Domain)")
        for insight in holistic['insights']:
            _render_ai_insight(insight)
