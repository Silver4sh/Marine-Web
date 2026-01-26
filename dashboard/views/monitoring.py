import streamlit as st
import asyncio
import pandas as pd
import datetime
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor

from dashboard.core import (
    ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS,
    render_metric_card, apply_chart_style, render_vessel_list_column, get_status_color, render_vessel_card,
    get_fleet_status, get_order_stats, get_financial_metrics, get_revenue_analysis, 
    get_clients_summary, get_system_settings, get_logs,
    get_notification_id, generate_insights
)

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

# --- NOTIFICATIONS ---
@st.cache_data(ttl=60, show_spinner=False)
def load_notification_data(role):
    return {
        "fleet": get_fleet_status(),
        "financial": get_financial_metrics(),
        "settings": get_system_settings(),
        "clients": get_clients_summary(),
        "logs": get_logs()
    }

def update_notification_status(notif_id, new_status):
    st.session_state.notification_states[notif_id] = new_status

def restore_notification(notif_id):
    if notif_id in st.session_state.notification_states:
        del st.session_state.notification_states[notif_id]

def render_notification_item(item, status):
    notif_id = item['id']
    icons = {"FLEET": "🚢", "FINANCIAL": "💰", "SYSTEM": "🖥️", "CLIENTS": "👥", "ALERT": "⚠️"}
    category = item.get('category', 'ALERT').upper()
    cat_ind = {"FLEET": "ARMADA", "FINANCIAL": "KEUANGAN", "SYSTEM": "SISTEM", "CLIENTS": "KLIEN", "ALERT": "PERINGATAN"}
    cat_display = cat_ind.get(category, category)
    
    icon = icons.get(category, "🔔")
    
    styles = {
        'inbox': {'bg': 'rgba(255, 255, 255, 0.05)', 'border': 'transparent', 'text': '#f8fafc', 'dot': True},
        'done':  {'bg': 'rgba(20, 83, 45, 0.2)', 'border': '#22c55e',      'text': '#f0fdf4', 'dot': False},
        'trash': {'bg': 'rgba(0, 0, 0, 0.2)',    'border': 'transparent',  'text': '#64748b', 'dot': False}
    }
    style = styles.get(status, styles['inbox'])
    
    dot_html = '<span style="height:8px;width:8px;background:#0ea5e9;border-radius:50%;display:inline-block;margin-right:8px;"></span>' if style['dot'] else ''
    
    html_content = (
        f'<div style="background:{style["bg"]}; border-left:3px solid {style["border"]}; padding:12px; border-radius:6px; margin-bottom:8px;">'
        f'    <div style="display:flex; justify-content:space-between; align-items:center;">'
        f'        <div style="display:flex; align-items:center;">'
        f'            {dot_html}'
        f'            <span style="font-size:16px; margin-right:6px;">{icon}</span>'
        f'            <strong style="color:{style["text"]}; font-size:14px;">{cat_display}</strong>'
        f'        </div>'
        f'        <small style="color:#94a3b8; font-size:11px;">{item.get("time_str", "")}</small>'
        f'    </div>'
        f'    <div style="color:{style["text"]}; font-size:13px; margin-top:6px; opacity: 0.9;">'
        f'        {item["message"]}'
        f'    </div>'
        f'</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.8, 0.2])
    with c2:
        if status == 'inbox':
            ca, cb = st.columns(2)
            ca.button("✅", key=f"d_{notif_id}", on_click=update_notification_status, args=(notif_id, 'done'), use_container_width=True)
            cb.button("🗑️", key=f"t_{notif_id}", on_click=update_notification_status, args=(notif_id, 'trash'), use_container_width=True)
        elif status == 'done':
             st.button("🗑️", key=f"td_{notif_id}", on_click=update_notification_status, args=(notif_id, 'trash'), use_container_width=True)
        elif status == 'trash':
             st.button("♻️", key=f"r_{notif_id}", on_click=restore_notification, args=(notif_id,), use_container_width=True)

@st.dialog("🔔 Pusat Notifikasi")
def show_notification_dialog():
    if 'notification_states' not in st.session_state:
        st.session_state.notification_states = {}

    data = load_notification_data(st.session_state.user_role)
    raw = generate_insights(data['fleet'], data['financial'], st.session_state.user_role, data['settings'], data['clients'])
    
    all_items = []
    for i in raw:
        i['id'] = get_notification_id(i.get('category', 'Alert'), i['message'], "dynamic")
        i['time_str'] = "Baru Saja"
        all_items.append(i)
        
    logs = data['logs']
    if not logs.empty:
        for _, row in logs.head(10).iterrows():
            ts = row['changed_at']
            if isinstance(ts, str): ts = datetime.datetime.now()
            msg = f"{row['action']} pada {row['table_name']}"
            all_items.append({
                "id": get_notification_id("System", msg, str(ts)),
                "category": "System",
                "message": msg,
                "time_str": ts.strftime("%H:%M") if hasattr(ts, 'strftime') else "Hari Ini",
                "level": "info"
            })

    views = {'inbox': [], 'done': [], 'trash': []}
    for item in all_items:
        state = st.session_state.notification_states.get(item['id'], 'inbox')
        views[state].append(item)

    tabs = st.tabs([f"Masuk ({len(views['inbox'])})", f"Selesai ({len(views['done'])})", f"Sampah ({len(views['trash'])})"])
    
    for tab, state in zip(tabs, ['inbox', 'done', 'trash']):
        with tab:
            if not views[state]:
                st.caption("Tidak ada notifikasi." if state != 'inbox' else "Anda sudah mengetahui semuanya!")
            else:
                for item in views[state]: render_notification_item(item, state)
            if state == 'trash' and views['trash']:
                 if st.button("Kosongkan Sampah", use_container_width=True): st.toast("Sampah dibersihkan")

# --- MONITORING VIEWS ---
def render_overview_tab(fleet, orders, financial, role):
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Kapal Beroperasi", fleet.get('operating', 0), f"{fleet.get('maintenance', 0)} dalam Perawatan", "#fbbf24")
    with c2: 
        pending = orders.get('on_progress', 0) + orders.get('in_completed', 0)
        render_metric_card("Pesanan Tertunda", pending, "Perlu Tindakan", "#f472b6")
    with c3:
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            revenue = financial.get('total_revenue', 0)
            delta = financial.get('delta_revenue', 0.0)
            rev_str = f"Rp {revenue:,.0f}" if revenue < 1e9 else f"Rp {revenue/1e9:.1f}M"
            render_metric_card("Pendapatan", rev_str, f"{delta:+.1f}% vs bulan lalu", "#ef4444" if delta < 0 else "#38bdf8")
        else:
            maint = fleet.get('maintenance', 0)
            render_metric_card("Kesehatan Armada", f"{100 - (maint*10)}%", "Operasional", "#38bdf8")
    with c4: render_metric_card("Misi Selesai", orders.get('completed', 0), "Tertinggi Sepanjang Masa", "#2dd4bf")

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
             else: st.info("Data pendapatan tidak tersedia.")
        else:
             if orders:
                 order_df = pd.DataFrame([{"Status": "Selesai", "Count": orders.get('completed',0)}, {"Status": "Terbuka", "Count": orders.get('open',0)}, {"Status": "Berjalan", "Count": orders.get('on_progress',0)}])
                 fig = px.pie(order_df, values='Count', names='Status', hole=0.7, title="Distribusi Pesanan", template="plotly_dark", color_discrete_sequence=['#2dd4bf', '#f472b6', '#fbbf24'])
                 apply_chart_style(fig)
                 st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.subheader("⚡ Tindakan Cepat")
        if role == ROLE_ADMIN:
             if st.button("👨‍💼 Manajemen Pengguna", use_container_width=True): st.session_state.current_page = "👨‍💼 Manajemen Pengguna"; st.rerun()
             if st.button("🔧 Konfigurasi Sistem", use_container_width=True): st.session_state.current_page = "🔧 Pengaturan"; st.rerun()
        elif role == ROLE_OPERATIONS:
             if st.button("🗺️ Buka Peta Kapal", use_container_width=True): st.session_state.current_page = "🗺️ Peta Kapal"; st.rerun()
        
        st.markdown("### 🚢 Ringkasan Armada")
        fleet_df = pd.DataFrame([
            {"Status": "Beroperasi", "Count": fleet.get('operating', 0)},
            {"Status": "Idle", "Count": fleet.get('idle', 0)},
            {"Status": "Perawatan", "Count": fleet.get('maintenance', 0)},
        ])
        st.dataframe(fleet_df, hide_index=True, use_container_width=True, column_config={"Status": "Status", "Count": st.column_config.ProgressColumn("Jumlah", format="%d", min_value=0, max_value=int(max(fleet.get('total_vessels', 10), 1)))})



def render_monitoring_view():
    st.markdown(f"## 👋 Selamat datang kembali, {st.session_state.username}")
    
    # Data Loading
    role = st.session_state.user_role
    with st.spinner("🚀 Sinkronisasi data langsung..."):
        data = asyncio.run(data_manager_async.get_dashboard_data(role))
    
    render_overview_tab(data['fleet'], data['orders'], data['financial'], role)
