import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor, as_completed

from core import (
    render_metric_card, apply_chart_style, render_vessel_list_column, get_status_color, render_vessel_card,
    get_fleet_status, get_order_stats, get_financial_metrics, get_revenue_analysis,
    get_clients_summary, get_system_settings
)
from core.ai_analyst import MarineAIAnalyst
from core.config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS


# --- Parallel Data Loading (Thread-Safe for Streamlit) ---
_executor = ThreadPoolExecutor(max_workers=4)


def _load_dashboard_data(role):
    """Load all dashboard data in parallel using threads (Streamlit-safe)."""
    tasks = {
        "fleet":    _executor.submit(get_fleet_status),
        "orders":   _executor.submit(get_order_stats),
        "settings": _executor.submit(get_system_settings),
        "clients":  _executor.submit(get_clients_summary),
    }
    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        tasks["financial"] = _executor.submit(get_financial_metrics)
    else:
        tasks["financial"] = None

    results = {"fleet": {}, "orders": {}, "financial": {}, "settings": {}, "clients": pd.DataFrame()}
    for key, future in tasks.items():
        if future is None:
            continue
        try:
            results[key] = future.result(timeout=10)
        except Exception as e:
            print(f"[monitoring] Failed to load {key}: {e}")
    return results


def _ai_insight_banner(insight: dict):
    """Renders a single AI insight as an inline banner card."""
    icon_map = {"critical": "🚨", "warning": "⚠️", "positive": "✅", "info": "🤖"}
    color_map = {
        "critical": ("#f43f5e", "rgba(244,63,94,0.12)", "rgba(244,63,94,0.3)"),
        "warning":  ("#f59e0b", "rgba(245,158,11,0.12)", "rgba(245,158,11,0.3)"),
        "positive": ("#22c55e", "rgba(34,197,94,0.12)",  "rgba(34,197,94,0.3)"),
        "info":     ("#0ea5e9", "rgba(14,165,233,0.1)",  "rgba(14,165,233,0.25)"),
    }
    itype = insight.get("type", "info")
    icon = icon_map.get(itype, "🤖")
    accent, bg, border = color_map.get(itype, color_map["info"])

    st.markdown(f"""
        <div style="
            background: {bg};
            border: 1px solid {border};
            border-left: 4px solid {accent};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 10px;
            display: flex; gap: 12px; align-items: flex-start;
            animation: slideDown 0.4s ease forwards;
        ">
            <div style="font-size:1.4rem; flex-shrink:0;">{icon}</div>
            <div>
                <div style="font-weight:700; color:#f0f6ff; font-family:'Outfit',sans-serif; margin-bottom:3px; font-size:0.9rem;">{insight['title']}</div>
                <div style="color:#8ba3c0; font-size:0.85rem; line-height:1.5;">{insight['desc']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_overview_tab(fleet, orders, financial, role):
    # Page Header
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">🏠</div>
            <div>
                <p class="page-header-title">Monitoring</p>
                <p class="page-header-subtitle">Real-time fleet & operational overview</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Metric Cards Row ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Kapal Beroperasi", fleet.get('operating', 0),
                           f"{fleet.get('maintenance', 0)} dalam Perawatan", "#fbbf24",
                           help_text="Jumlah kapal yang aktif beroperasi saat ini.")
    with c2:
        pending = orders.get('on_progress', 0) + orders.get('in_completed', 0)
        render_metric_card("Pesanan Tertunda", pending, "Perlu Tindakan", "#f472b6",
                           help_text="Total pesanan yang sedang berjalan atau belum selesai.")
    with c3:
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            revenue = financial.get('total_revenue', 0)
            delta = financial.get('delta_revenue', 0.0)
            rev_str = f"Rp {revenue:,.0f}" if revenue < 1e9 else f"Rp {revenue/1e9:.1f}M"
            render_metric_card("Pendapatan", rev_str, f"{delta:+.1f}% vs bulan lalu",
                               "#ef4444" if delta < 0 else "#38bdf8",
                               help_text="Total pendapatan kotor bulan ini dibandingkan bulan lalu.")
        else:
            maint = fleet.get('maintenance', 0)
            total = max(fleet.get('total_vessels', 1), 1)
            render_metric_card("Kesehatan Armada", f"{100 - round((maint/total)*100)}%", "Operasional", "#38bdf8",
                               help_text="Persentase kapal yang siap beroperasi.")
    with c4:
        comp_val = orders.get('completed', 0)
        total_v = max(fleet.get('total_vessels', 1), 1)
        util_pct = (fleet.get('operating', 0) / total_v) * 100
        fleet_analysis = MarineAIAnalyst.analyze_fleet(util_pct)
        ai_desc = fleet_analysis['insights'][0]['desc']
        render_metric_card("Task Selesai", comp_val, "Analisis AI Aktif", "#2dd4bf",
                           help_text=f"Analisis AI: {ai_desc}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Main Content ---
    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown("""
            <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700; color:#f0f6ff; margin-bottom:12px; letter-spacing:-0.01em;">
                📊 Tren Operasional
            </div>
        """, unsafe_allow_html=True)

        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            rev_df = get_revenue_analysis()
            if not rev_df.empty:
                fig = px.bar(rev_df, x='month', y='revenue',
                             title="Arus Pendapatan Bulanan",
                             template="plotly_dark",
                             color='revenue',
                             color_continuous_scale=['#0f172a', '#38bdf8'])
                apply_chart_style(fig)
                st.plotly_chart(fig, use_container_width=True)

                last_month = rev_df.iloc[-1]
                prev_month = rev_df.iloc[-2] if len(rev_df) > 1 else last_month
                growth = ((last_month['revenue'] - prev_month['revenue']) / prev_month['revenue']) * 100 \
                    if prev_month['revenue'] > 0 else 0
                rev_insight = MarineAIAnalyst.analyze_financials({'delta_revenue': growth})['insights'][0]['desc']
                st.caption(f"🤖 {rev_insight}")
            else:
                st.info("Data pendapatan tidak tersedia.")
        else:
            if orders:
                order_df = pd.DataFrame([
                    {"Status": "Selesai",  "Count": orders.get('completed', 0)},
                    {"Status": "Terbuka",  "Count": orders.get('open', 0)},
                    {"Status": "Berjalan", "Count": orders.get('on_progress', 0)}
                ])
                fig = px.pie(order_df, values='Count', names='Status', hole=0.7,
                             title="Distribusi Pesanan", template="plotly_dark",
                             color_discrete_sequence=['#2dd4bf', '#f472b6', '#fbbf24'])
                apply_chart_style(fig)
                st.plotly_chart(fig, use_container_width=True)

                completed = orders.get('completed', 0)
                open_orders = orders.get('open', 0)
                ratio = completed / (completed + open_orders) if (completed + open_orders) > 0 else 0

                if ratio > 0.8:
                    ord_insight = "✅ **Efisiensi Tinggi**: Mayoritas pesanan telah diselesaikan dengan cepat."
                elif open_orders > completed:
                    ord_insight = "⏳ **Bottleneck**: Jumlah pesanan terbuka melebihi kapasitas penyelesaian."
                else:
                    ord_insight = "⚖️ **Seimbang**: Alur masuk dan keluar pesanan terjaga."
                st.caption(f"🤖 {ord_insight}")

    with c_right:
        st.markdown("""
            <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700; color:#f0f6ff; margin-bottom:12px; letter-spacing:-0.01em;">
                ⚡ Tindakan Cepat
            </div>
        """, unsafe_allow_html=True)

        if role == ROLE_ADMIN:
            if st.button("🗺️ Buka Peta Kapal", use_container_width=True):
                st.session_state.current_page = "🗺️ Peta Kapal"
                st.rerun()
        elif role == ROLE_OPERATIONS:
            if st.button("🗺️ Buka Peta Kapal", use_container_width=True):
                st.session_state.current_page = "🗺️ Peta Kapal"
                st.rerun()

        st.markdown("""
            <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700; color:#f0f6ff; margin: 14px 0 8px 0;">
                🚢 Ringkasan Armada
            </div>
        """, unsafe_allow_html=True)

        # Use the already-loaded fleet data (no second query)
        fleet_data = pd.DataFrame([
            {"Status": "Beroperasi", "Count": fleet.get('operating', 0)},
            {"Status": "Idle",       "Count": fleet.get('idle', 0)},
            {"Status": "Perawatan",  "Count": fleet.get('maintenance', 0)},
        ])
        max_val = int(max(fleet.get('total_vessels', 10), 1))

        st.dataframe(
            fleet_data,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Status": "Status",
                "Count": st.column_config.ProgressColumn(
                    "Jumlah", format="%d", min_value=0, max_value=max_val
                )
            }
        )


def render_monitoring_view():
    role = st.session_state.user_role
    with st.spinner("🚀 Sinkronisasi data langsung..."):
        data = _load_dashboard_data(role)

    render_overview_tab(data['fleet'], data['orders'], data['financial'], role)

    # --- AI COGNITIVE LAYER ---
    rev_growth = data['financial'].get('delta_revenue', 0) if data['financial'] else 0
    util = (data['fleet'].get('operating', 0) / max(data['fleet'].get('total_vessels', 1), 1)) * 100
    anomaly_count = 0

    churn_count = 0
    if not data['clients'].empty and 'churn_risk' in data['clients'].columns:
        churn_count = len(data['clients'][data['clients']['churn_risk'] == 'Tinggi'])

    holistic_analysis = MarineAIAnalyst.analyze_holistic(
        {'delta_revenue': rev_growth},
        {'utilization': util},
        anomaly_count,
        churn_count
    )

    if holistic_analysis['insights']:
        st.divider()
        st.markdown("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <span style="font-size:1.5rem;">🧠</span>
                <div>
                    <div style="font-family:'Outfit',sans-serif; font-size:1.05rem; font-weight:800; color:#f0f6ff; letter-spacing:-0.01em;">Analisis Kognitif</div>
                    <div style="font-size:0.78rem; color:#8ba3c0;">Cross-domain AI insights</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for insight in holistic_analysis['insights']:
            _ai_insight_banner(insight)
