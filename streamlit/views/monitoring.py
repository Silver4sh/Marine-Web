import streamlit as st
import asyncio
import pandas as pd
import datetime
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor
import random

from core import (
    render_metric_card, apply_chart_style, render_vessel_list_column, get_status_color, render_vessel_card,
    get_fleet_status, get_order_stats, get_financial_metrics, get_revenue_analysis, 
    get_clients_summary, get_system_settings
)
from core.ai_analyst import MarineAIAnalyst
from core.config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS


# --- Async Data Loading ---
class AsyncDataManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def get_dashboard_data(self, role):
        loop = asyncio.get_event_loop()
        tasks = []
        tasks.append(loop.run_in_executor(self.executor, get_fleet_status)) # 0
        tasks.append(loop.run_in_executor(self.executor, get_order_stats)) # 1
        
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
             tasks.append(loop.run_in_executor(self.executor, get_financial_metrics)) # 2
        else:
             tasks.append(loop.run_in_executor(self.executor, lambda: {}))

        tasks.append(loop.run_in_executor(self.executor, get_system_settings)) # 3
        tasks.append(loop.run_in_executor(self.executor, get_clients_summary)) # 4
        
        results = await asyncio.gather(*tasks)
        return {
            "fleet": results[0],
            "orders": results[1],
            "financial": results[2],
            "settings": results[3],
            "clients": results[4]
        }

data_manager_async = AsyncDataManager()


def render_overview_tab(fleet, orders, financial, role):
    st.markdown("## 📊 Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Kapal Beroperasi", fleet.get('operating', 0), f"{fleet.get('maintenance', 0)} dalam Perawatan", "#fbbf24", help_text="Jumlah kapal yang aktif beroperasi saat ini.")
    with c2: 
        pending = orders.get('on_progress', 0) + orders.get('in_completed', 0)
        render_metric_card("Pesanan Tertunda", pending, "Perlu Tindakan", "#f472b6", help_text="Total pesanan yang sedang berjalan atau belum selesai.")
    with c3:
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            revenue = financial.get('total_revenue', 0)
            delta = financial.get('delta_revenue', 0.0)
            rev_str = f"Rp {revenue:,.0f}" if revenue < 1e9 else f"Rp {revenue/1e9:.1f}M"
            render_metric_card("Pendapatan", rev_str, f"{delta:+.1f}% vs bulan lalu", "#ef4444" if delta < 0 else "#38bdf8", help_text="Total pendapatan kotor bulan ini dibandingkan bulan lalu.")
        else:
            maint = fleet.get('maintenance', 0)
            render_metric_card("Kesehatan Armada", f"{100 - (maint*10)}%", "Operasional", "#38bdf8", help_text="Persentase kapal yang siap beroperasi.")
    with c4: 
        comp_val = orders.get('completed', 0)
        # AI Logic for scalability
        fleet_analysis = MarineAIAnalyst.analyze_fleet((fleet.get('operating', 0) / max(fleet.get('total_vessels', 1), 1)) * 100)
        ai_desc = fleet_analysis['insights'][0]['desc']
        
        render_metric_card("Task Selesai", comp_val, "Analisis AI Aktif", "#2dd4bf", help_text=f"Analisis AI: {ai_desc}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.subheader("📊 Tren Operasional")
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
             rev_df = get_revenue_analysis()
             if not rev_df.empty:
                 fig = px.bar(rev_df, x='month', y='revenue', title="Arus Pendapatan Bulanan", template="plotly_dark", color='revenue', color_continuous_scale=['#0f172a', '#38bdf8'])
                 apply_chart_style(fig)
                 st.plotly_chart(fig, use_container_width=True)
                 
                 # Revenue Insight
                 last_month = rev_df.iloc[-1]
                 prev_month = rev_df.iloc[-2] if len(rev_df) > 1 else last_month
                 growth = ((last_month['revenue'] - prev_month['revenue']) / prev_month['revenue']) * 100 if prev_month['revenue'] > 0 else 0
                 
                 rev_insight = MarineAIAnalyst.analyze_financials({'delta_revenue': growth})['insights'][0]['desc']
                 
                 st.caption(f"🤖 {rev_insight}")
             else: st.info("Data pendapatan tidak tersedia.")
        else:
             if orders:
                 order_df = pd.DataFrame([{"Status": "Selesai", "Count": orders.get('completed',0)}, {"Status": "Terbuka", "Count": orders.get('open',0)}, {"Status": "Berjalan", "Count": orders.get('on_progress',0)}])
                 fig = px.pie(order_df, values='Count', names='Status', hole=0.7, title="Distribusi Pesanan", template="plotly_dark", color_discrete_sequence=['#2dd4bf', '#f472b6', '#fbbf24'])
                 apply_chart_style(fig)
                 st.plotly_chart(fig, use_container_width=True)
                 
                 # Order Insight
                 completed = orders.get('completed', 0)
                 open_orders = orders.get('open', 0)
                 ratio = completed / (completed + open_orders) if (completed + open_orders) > 0 else 0
                 
                 ord_insight = ""
                 if ratio > 0.8: ord_insight = "✅ **Efisiensi Tinggi**: Mayoritas pesanan telah diselesaikan dengan cepat."
                 elif open_orders > completed: ord_insight = "⏳ **Bottleneck**: Jumlah pesanan terbuka melebihi kapasitas penyelesaian."
                 else: ord_insight = "⚖️ **Seimbang**: Alur masuk dan keluar pesanan terjaga."
                 
                 st.caption(f"🤖 {ord_insight}")


    with c_right:
        st.subheader("⚡ Tindakan Cepat")
        if role == ROLE_ADMIN:
             if st.button("👨‍💼 Manajemen Pengguna", use_container_width=True): st.session_state.current_page = "👨‍💼 Manajemen Pengguna"; st.rerun()
             if st.button("🔧 Konfigurasi Sistem", use_container_width=True): st.session_state.current_page = "🔧 Pengaturan"; st.rerun()
        elif role == ROLE_OPERATIONS:
             if st.button("🗺️ Buka Peta Kapal", use_container_width=True): st.session_state.current_page = "🗺️ Peta Kapal"; st.rerun()
        
        st.markdown("### 🚢 Ringkasan Armada")
        
        fleet_source = get_fleet_status()
        
        fleet_data = pd.DataFrame([
            {"Status": "Beroperasi", "Count": fleet_source.get('operating', 0)},
            {"Status": "Idle", "Count": fleet_source.get('idle', 0)},
            {"Status": "Perawatan", "Count": fleet_source.get('maintenance', 0)},
        ])
        
        max_val = int(max(fleet_source.get('total_vessels', 10), 1))
        
        st.dataframe(
            fleet_data, 
            hide_index=True, 
            use_container_width=True, 
            column_config={
                "Status": "Status", 
                "Count": st.column_config.ProgressColumn("Jumlah", format="%d", min_value=0, max_value=max_val)
            }
        )



def render_monitoring_view():
    # Data Loading
    role = st.session_state.user_role
    with st.spinner("🚀 Sinkronisasi data langsung..."):
        data = asyncio.run(data_manager_async.get_dashboard_data(role))
    
    render_overview_tab(data['fleet'], data['orders'], data['financial'], role)

    # --- AI COGNITIVE LAYER (v4.0) ---
    # Prepare metrics for holistic analysis
    rev_growth = data['financial'].get('delta_revenue', 0) if data['financial'] else 0
    util = (data['fleet'].get('operating', 0) / max(data['fleet'].get('total_vessels', 1), 1)) * 100
    # Mocking environmental anomalies (to be connected to live sensor data)
    anomaly_count = 0 
    
    # Check churn risk count from client summary
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
        st.markdown("---")
        st.subheader("🧠 Analisis Kognitif (Cross-Domain)")
        for insight in holistic_analysis['insights']:
            if insight['type'] == 'critical':
                st.error(f"**{insight['title']}**\n\n{insight['desc']}")
            elif insight['type'] == 'warning':
                st.warning(f"**{insight['title']}**\n\n{insight['desc']}")
            elif insight['type'] == 'positive':
                st.success(f"**{insight['title']}**\n\n{insight['desc']}")
            else:
                st.info(f"**{insight['title']}**\n\n{insight['desc']}")
