import streamlit as st
import pandas as pd
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor

from components.cards import render_metric_card, render_vessel_list_column, render_vessel_card
from components.charts import apply_chart_style, gauge_chart, kpi_progress_bar
from components.helpers import get_status_color
from db.repositories.fleet_repo import get_fleet_status, get_operational_anomalies, get_fleet_daily_activity
from db.repositories.finance_repo import get_order_stats, get_financial_metrics, get_revenue_analysis, get_revenue_cycle_metrics
from db.repositories.client_repo import get_clients_summary
from db.repositories.settings_repo import get_system_settings
from services.ai_service import MarineAIAnalyst
from config.settings import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS

import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

def _load_dashboard_data(role: str) -> dict:
    """Fire off all data fetches in parallel for maximum responsiveness."""
    results = {
        "fleet": {}, "orders": {}, "financial": {}, "settings": {},
        "clients": pd.DataFrame(), "anomalies": pd.DataFrame(), "revenue": pd.DataFrame()
    }

    task_defs = {
        "fleet":     get_fleet_status,
        "orders":    get_order_stats,
        "settings":  get_system_settings,
        "clients":   get_clients_summary,
        "anomalies": get_operational_anomalies,
        "fleet_daily": get_fleet_daily_activity,
    }
    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        task_defs["financial"] = get_financial_metrics
        task_defs["revenue"]   = get_revenue_analysis
        task_defs["rev_cycle"] = get_revenue_cycle_metrics

    # Capture the Streamlit script context from the main thread so it can
    # be propagated to worker threads — prevents "missing ScriptRunContext" warnings.
    ctx = get_script_run_ctx()

    def _run(fn):
        """Wrap fn so the worker thread inherits the Streamlit script context."""
        def _inner():
            add_script_run_ctx(threading.current_thread(), ctx)
            return fn()
        return _inner

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {key: pool.submit(_run(fn)) for key, fn in task_defs.items()}
        for key, future in futures.items():
            try:
                results[key] = future.result(timeout=15)
            except Exception as e:
                print(f"[monitoring] Failed to load {key}: {e}")

    return results


# ── AI insight banner ──────────────────────────────────────────────────────────
def _ai_banner(insight: dict) -> None:
    icon_map  = {"critical": "🚨", "warning": "⚠️", "positive": "✅", "info": "🤖"}
    color_map = {
        "critical": ("#ef4444", "rgba(239,68,68,0.10)",  "rgba(239,68,68,0.28)"),
        "warning":  ("#f59e0b", "rgba(245,158,11,0.10)", "rgba(245,158,11,0.28)"),
        "positive": ("#22c55e", "rgba(34,197,94,0.10)",  "rgba(34,197,94,0.28)"),
        "info":     ("#60a5fa", "rgba(96,165,250,0.08)",  "rgba(96,165,250,0.22)"),
    }
    itype  = insight.get("type", "info")
    icon   = icon_map.get(itype, "🤖")
    accent, bg, border = color_map.get(itype, color_map["info"])
    st.markdown(f"""
        <div style="
            background:{bg}; border:1px solid {border}; border-left:4px solid {accent};
            border-radius:12px; padding:14px 18px; margin-bottom:10px;
            display:flex; gap:12px; align-items:flex-start;
            animation:slideDown 0.4s ease forwards;
        ">
            <div style="font-size:1.4rem; flex-shrink:0;">{icon}</div>
            <div>
                <div style="font-weight:700; color:#f0f6ff; font-family:'Outfit',sans-serif;
                            margin-bottom:3px; font-size:0.9rem;">{insight['title']}</div>
                <div style="color:#8ba3c0; font-size:0.85rem; line-height:1.5;">{insight['desc']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ── Anomaly feed panel ─────────────────────────────────────────────────────────
def _render_anomaly_feed(anomaly_df: pd.DataFrame) -> None:
    """Live operational anomaly feed — shows a styled row per anomaly vessel."""
    st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <span style="font-size:1.1rem;">🔴</span>
            <div style="font-family:'Outfit',sans-serif; font-size:0.95rem;
                        font-weight:800; color:#f0f6ff;">Live Anomaly Feed</div>
            <div style="font-size:0.7rem; color:#f43f5e; font-weight:600;
                        background:rgba(244,63,94,0.12); padding:2px 8px;
                        border-radius:99px; border:1px solid rgba(244,63,94,0.3);">
                LIVE
            </div>
        </div>
    """, unsafe_allow_html=True)

    if anomaly_df is None or anomaly_df.empty:
        st.markdown("""
            <div style="
                text-align:center; padding:20px; color:#22c55e;
                background:rgba(34,197,94,0.06); border:1px solid rgba(34,197,94,0.15);
                border-radius:12px;
            ">
                ✅ Tidak ada anomali aktif
            </div>
        """, unsafe_allow_html=True)
        return

    for _, row in anomaly_df.iterrows():
        a_type  = str(row.get("anomaly_type", "Unknown"))
        v_name  = str(row.get("vessel_name", row.get("id_vessel", "—")))
        v_spd   = float(row.get("speed", 0) or 0)
        v_stat  = str(row.get("reported_status", "—"))
        is_ghost = "Ghost" in a_type or "hantu" in a_type.lower()
        badge_c = "#f43f5e" if is_ghost else "#f59e0b"

        st.markdown(f"""
        <div style="
            background:rgba(244,63,94,0.07); border:1px solid rgba(244,63,94,0.2);
            border-left:4px solid {badge_c};
            border-radius:10px; padding:10px 14px; margin-bottom:7px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-family:'Outfit',sans-serif; font-weight:700;
                            color:#f0f6ff; font-size:0.88rem;">{v_name}</div>
                <span style="
                    background:{badge_c}22; color:{badge_c};
                    border:1px solid {badge_c}55; border-radius:99px;
                    font-size:0.68rem; font-weight:700; padding:2px 8px;
                ">{a_type}</span>
            </div>
            <div style="font-size:0.78rem; color:#8ba3c0; margin-top:4px;">
                Status: <strong style="color:#cbd5e1;">{v_stat}</strong>
                &nbsp;·&nbsp; Speed: <strong style="color:#fbbf24;">{v_spd:.1f} kn</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Overview tab ───────────────────────────────────────────────────────────────
def render_overview_tab(fleet, orders, financial, role, settings, anomaly_df, fleet_daily=None, rev_cycle=None):
    # Page header
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">🏠</div>
            <div>
                <p class="page-header-title">Monitoring</p>
                <p class="page-header-subtitle">Real-time fleet & operational intelligence</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Top metric cards ───────────────────────────────────────────────────────
    # --- Kalkulasi Trend Historis (Sparklines) ---
    fleet_trend, order_trend, rev_trend = None, None, None
    if fleet_daily is not None and not fleet_daily.empty:
        fleet_trend = fleet_daily.groupby("day_num")["code_vessel"].nunique().tolist()
    if rev_cycle is not None and not rev_cycle.empty:
        df_rev = rev_cycle.sort_values("month")
        order_trend = df_rev["total_orders"].tolist()[-6:]
        rev_trend = df_rev["realized_revenue"].tolist()[-6:]

    c1, c2, c3, c4 = st.columns(4)
    total_v = max(fleet.get("total_vessels", 1), 1)
    oper    = fleet.get("operating", 0)
    maint   = fleet.get("maintenance", 0)
    util_pct = (oper / total_v) * 100

    with c1:
        render_metric_card(
            "Kapal Beroperasi", oper,
            f"{maint} dalam Perawatan", "#fbbf24",
            help_text="Jumlah kapal aktif saat ini berdasarkan status terakhir.",
            sparkline_data=fleet_trend
        )
    with c2:
        pending = orders.get("on_progress", 0) + orders.get("in_completed", 0)
        render_metric_card(
            "Pesanan Aktif", pending, "Perlu Tindakan", "#f472b6",
            help_text="Total pesanan yang sedang berjalan atau belum diselesaikan.",
            sparkline_data=order_trend
        )
    with c3:
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            cur_rev = financial.get("current_revenue", financial.get("total_revenue", 0))
            delta   = financial.get("delta_revenue", 0.0)
            rev_str = f"Rp {cur_rev/1e9:.1f}M" if cur_rev >= 1e9 else f"Rp {cur_rev:,.0f}"
            delta_clr = "#ef4444" if delta < 0 else "#38bdf8"
            render_metric_card(
                "Pendapatan Bulan Ini", rev_str, f"{delta:+.1f}% vs bulan lalu",
                delta_clr,
                help_text="Pendapatan bulan berjalan dibanding bulan lalu.",
                sparkline_data=rev_trend
            )
        else:
            health = 100 - round((maint / total_v) * 100)
            render_metric_card(
                "Kesehatan Armada", f"{health}%", "Siap Operasi", "#38bdf8",
                help_text="Persentase kapal yang tidak dalam perawatan.",
                sparkline_data=fleet_trend  # Menggunakan trend operasi kapal sebagai proxy kesehatan
            )
    with c4:
        anomaly_count = len(anomaly_df) if anomaly_df is not None and not anomaly_df.empty else 0
        anom_clr = "#f43f5e" if anomaly_count > 0 else "#22c55e"
        render_metric_card(
            "Anomali Aktif", anomaly_count,
            "Ghost / Pergerakan Tak Sah", anom_clr,
            help_text="Kapal yang menunjukkan perilaku operasional tidak wajar dalam 2 jam terakhir."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Gauges Row ─────────────────────────────────────────────────────────
    st.markdown("""
        <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700;
                    color:#f0f6ff; margin-bottom:6px;">
            📊 KPI Dashboard
        </div>
    """, unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(
            gauge_chart(round(util_pct, 1), "Utilisasi Armada", 100, "%",
                        thresholds=(40, 70), height=180), config={"displayModeBar": False}
        )
    with g2:
        comp     = orders.get("completed", 0)
        tot_ord  = max(orders.get("total_orders", 1), 1)
        comp_pct = (comp / tot_ord) * 100
        st.plotly_chart(
            gauge_chart(round(comp_pct, 1), "Penyelesaian Pesanan", 100, "%",
                        thresholds=(60, 80), height=180), config={"displayModeBar": False}
        )
    with g3:
        health_pct = 100 - round((maint / total_v) * 100)
        st.plotly_chart(
            gauge_chart(float(health_pct), "Kesehatan Armada", 100, "%",
                        thresholds=(60, 85), height=180), config={"displayModeBar": False}
        )
    with g4:
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            rev_target = float(settings.get("revenue_target_monthly", 5_000_000_000) or 5_000_000_000)
            cur_rev    = financial.get("current_revenue", 0)
            rev_pct    = min((cur_rev / rev_target) * 100 if rev_target > 0 else 0, 150)
            st.plotly_chart(
                gauge_chart(round(rev_pct, 1), "Pencapaian Revenue", 150, "%",
                            thresholds=(50, 100), height=180), config={"displayModeBar": False}
            )
        else:
            open_pct = min((orders.get("open", 0) / tot_ord) * 100, 100)
            st.plotly_chart(
                gauge_chart(round(open_pct, 1), "Pesanan Terbuka", 100, "%",
                            thresholds=(30, 60), height=180), config={"displayModeBar": False}
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main content grid ──────────────────────────────────────────────────────
    c_main, c_side = st.columns([2, 1])

    with c_main:
        st.markdown("""
            <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700;
                        color:#f0f6ff; margin-bottom:12px;">
                📈 Tren Operasional
            </div>
        """, unsafe_allow_html=True)

        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            rev_df = get_revenue_analysis()
            if not rev_df.empty:
                fig = px.bar(
                    rev_df, x="month", y="revenue",
                    title="Arus Pendapatan Bulanan",
                    template="plotly_dark",
                    color="revenue",
                    color_continuous_scale=["#1a0a0a", "#ef4444"]
                )
                fig.update_layout(showlegend=False, coloraxis_showscale=False)
                apply_chart_style(fig)
                st.plotly_chart(fig, width='stretch')

                # Revenue target progress bar
                if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
                    cur = financial.get("current_revenue", 0)
                    tgt = float(settings.get("revenue_target_monthly", 5_000_000_000) or 5_000_000_000)
                    kpi_progress_bar("Progress Target Bulanan", cur, tgt)
            else:
                st.info("Data pendapatan tidak tersedia.")
        else:
            if orders:
                order_df = pd.DataFrame([
                    {"Status": "Selesai",  "Count": orders.get("completed",   0)},
                    {"Status": "Terbuka",  "Count": orders.get("open",        0)},
                    {"Status": "Berjalan", "Count": orders.get("on_progress",  0)},
                    {"Status": "Gagal",    "Count": orders.get("failed",       0)},
                ])
                fig = px.pie(
                    order_df, values="Count", names="Status", hole=0.7,
                    title="Distribusi Pesanan", template="plotly_dark",
                    color_discrete_sequence=["#ef4444", "#f59e0b", "#fb923c", "#22c55e"]
                )
                apply_chart_style(fig)
                st.plotly_chart(fig, width='stretch')

    with c_side:
        # Fleet summary table
        st.markdown("""
            <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700;
                        color:#f0f6ff; margin-bottom:8px;">
                🚢 Ringkasan Armada
            </div>
        """, unsafe_allow_html=True)
        fleet_df = pd.DataFrame([
            {"Status": "Beroperasi", "Count": fleet.get("operating",    0)},
            {"Status": "Idle",       "Count": fleet.get("idle",         0)},
            {"Status": "Perawatan",  "Count": fleet.get("maintenance",  0)},
        ])
        max_v = max(fleet.get("total_vessels", 10), 1)
        st.dataframe(
            fleet_df, hide_index=True,
            column_config={
                "Count": st.column_config.ProgressColumn(
                    "Jumlah", format="%d", min_value=0, max_value=max_v
                )
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Task summary tabel
        st.markdown("""
            <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:700;
                        color:#f0f6ff; margin-bottom:8px;">
                📋 Ringkasan Task
            </div>
        """, unsafe_allow_html=True)
        
        # Taking data from order_stats if accessible
        task_df = pd.DataFrame([
            {"Status": "Selesai", "Count": orders.get("completed", 0)},
            {"Status": "Sedang berjalan", "Count": orders.get("on_progress", 0) + orders.get("in_completed", 0)},
            {"Status": "Gagal", "Count": orders.get("failed", 0)},
        ])
        max_t = max(orders.get("total_orders", 10), 1)
        st.dataframe(
            task_df, hide_index=True,
            column_config={
                "Count": st.column_config.ProgressColumn(
                    "Jumlah", format="%d", min_value=0, max_value=max_t
                )
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Live anomaly feed ──────────────────────────────────────────────────
        _render_anomaly_feed(anomaly_df)

        st.markdown("<br>", unsafe_allow_html=True)
        if role in [ROLE_ADMIN, ROLE_OPERATIONS]:
            if st.button("🗺️ Buka Peta Kapal", type="primary", width='stretch'):
                st.session_state.current_page = "🗺️ Peta Kapal"
                st.rerun()


# ── Main page entry ────────────────────────────────────────────────────────────
def render_monitoring_view():
    role = st.session_state.user_role

    with st.spinner("🚀 Sinkronisasi data langsung..."):
        data = _load_dashboard_data(role)

    render_overview_tab(
        data["fleet"], data["orders"], data["financial"],
        role, data["settings"], data["anomalies"],
        data.get("fleet_daily"), data.get("rev_cycle")
    )

    # ── AI Cognitive Analysis section ──────────────────────────────────────────
    rev_growth   = data["financial"].get("delta_revenue", 0) if data["financial"] else 0
    total_v      = max(data["fleet"].get("total_vessels", 1), 1)
    util         = (data["fleet"].get("operating", 0) / total_v) * 100
    anomaly_count = len(data["anomalies"]) if not data["anomalies"].empty else 0

    churn_count = 0
    if not data["clients"].empty and "churn_risk" in data["clients"].columns:
        churn_count = len(data["clients"][data["clients"]["churn_risk"] == "Tinggi"])

    all_insights = []

    # Holistic cross-domain
    holistic = MarineAIAnalyst.analyze_holistic(
        {"delta_revenue": rev_growth}, {"utilization": util},
        anomaly_count, churn_count
    )
    all_insights.extend(holistic["insights"])

    # Anomaly-specific
    if anomaly_count > 0:
        anom_ai = MarineAIAnalyst.analyze_anomalies(data["anomalies"])
        all_insights.extend(anom_ai["insights"])

    # KPI & target
    if data["financial"] and role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        settings = data["settings"]
        cur_rev  = data["financial"].get("current_revenue", 0)
        tgt      = float(settings.get("revenue_target_monthly", 5_000_000_000) or 5_000_000_000)
        pct      = (cur_rev / tgt * 100) if tgt > 0 else 0.0
        all_insights.extend(MarineAIAnalyst.analyze_kpi(pct)["insights"])
        all_insights.extend(MarineAIAnalyst.analyze_target_progress(pct)["insights"])

    if all_insights:
        st.divider()
        st.markdown("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <span style="font-size:1.5rem;">🧠</span>
                <div>
                    <div style="font-family:'Outfit',sans-serif; font-size:1.05rem;
                                font-weight:800; color:#f0f6ff;">Analisis Kognitif AI</div>
                    <div style="font-size:0.78rem; color:#8ba3c0;">
                        Cross-domain intelligence · Real-time
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(min(len(all_insights), 3))
        for i, ins in enumerate(all_insights[:6]):
            with cols[i % len(cols)]:
                _ai_banner(ins)
