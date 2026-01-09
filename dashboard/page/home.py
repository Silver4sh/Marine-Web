import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor

from back.src.constants import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS
from back.src.utils import render_metric_card, apply_chart_style
from back.src.constants import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS
from back.src.utils import render_metric_card, apply_chart_style
from back.query.queries import get_fleet_status, get_order_stats, get_financial_metrics, get_revenue_analysis, get_clients_summary
from back.query.config_queries import get_system_settings

# --- Async Data Loading ---
class AsyncDataManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def get_dashboard_data(self, role):
        loop = asyncio.get_event_loop()
        
        # Define tasks based on role to save resources
        tasks = []
        
        # Task 0: Fleet Status (Common)
        tasks.append(loop.run_in_executor(self.executor, get_fleet_status))
        
        # Task 1: Orders (Common)
        tasks.append(loop.run_in_executor(self.executor, get_order_stats))
        
        # Task 2: Financials (Admin/Finance/Marcom)
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
             tasks.append(loop.run_in_executor(self.executor, get_financial_metrics))
        else:
             tasks.append(loop.run_in_executor(self.executor, lambda: {}))

        # Task 3: Settings (Common for insights)
        tasks.append(loop.run_in_executor(self.executor, get_system_settings))
        
        # Task 4: Clients (For Churn Risk)
        tasks.append(loop.run_in_executor(self.executor, get_clients_summary))

        results = await asyncio.gather(*tasks)
        return {
            "fleet": results[0],
            "orders": results[1],
            "financial": results[2],
            "settings": results[3],
            "clients": results[4]
        }

data_manager = AsyncDataManager()

data_manager = AsyncDataManager()




        

def render_dashboard_home(fleet, orders, financial, role, settings, clients):
    st.markdown(f"## 👋 Welcome back, {st.session_state.username}")
    

    
    st.markdown("---")
    
    # --- Hero Section (KPIs) ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        render_metric_card("Operating Vessels", fleet.get('operating', 0), f"{fleet.get('maintenance', 0)} in Maintenance", "#fbbf24")
        
    with c2:
        pending = orders.get('on_progress', 0) + orders.get('in_completed', 0)
        render_metric_card("Pending Orders", pending, "Requires Action", "#f472b6")
        
    with c3:
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            revenue = financial.get('total_revenue', 0)
            delta_rev = financial.get('delta_revenue', 0.0)
            
            # Format K/M for large numbers
            rev_str = f"IDR {revenue:,.0f}"
            if revenue > 1000000000: rev_str = f"IDR {revenue/1000000000:.1f}B"
            elif revenue > 1000000: rev_str = f"IDR {revenue/1000000:.1f}M"
            elif revenue > 1000: rev_str = f"IDR {revenue/1000:.0f}K"
            
            delta_str = f"{delta_rev:+.1f}% vs last month"
            delta_color = "#ef4444" if delta_rev < 0 else "#38bdf8"
            render_metric_card("Revenue", rev_str, delta_str, delta_color)
        else:
            in_maintenance = fleet.get('maintenance', 0)
            render_metric_card("Fleet Health", f"{100 - (in_maintenance*10)}%", "Operational", "#38bdf8")

    with c4:
        completed = orders.get('completed', 0)
        render_metric_card("Completed Missions", completed, "All Time High", "#2dd4bf")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Content Grid ---
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("📊 Operational Trends")
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
             # Revenue Chart
             rev_df = get_revenue_analysis()
             if not rev_df.empty:
                 fig = px.bar(
                     rev_df, x='month', y='revenue',
                     title="Monthly Revenue Stream",
                     template="plotly_dark",
                     color='revenue',
                     color_continuous_scale=['#0f172a', '#38bdf8']
                 )
                 apply_chart_style(fig)
                 fig.update_layout(title_font_color="#f8fafc", title="Monthly Revenue Stream")
                 fig.update_traces(marker_line_width=0, opacity=0.8)
                 st.plotly_chart(fig, use_container_width=True)
             else:
                 st.info("No revenue data available.")
        else:
             # Just order stats chart for Operations
             if orders:
                 order_df = pd.DataFrame([
                     {"Status": "Completed", "Count": orders.get('completed', 0)},
                     {"Status": "Open", "Count": orders.get('open', 0)},
                     {"Status": "In Progress", "Count": orders.get('on_progress', 0)},
                 ])
                 fig = px.pie(
                     order_df, values='Count', names='Status', hole=0.7, 
                     title="Order Distribution", template="plotly_dark",
                     color_discrete_sequence=['#2dd4bf', '#f472b6', '#fbbf24']
                 )
                 apply_chart_style(fig)
                 fig.update_layout(title="Order Distribution", legend=dict(orientation="h", y=-0.1))
                 fig.update_traces(textinfo='none', hoverinfo='label+percent+value')
                 st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.subheader("⚡ Actions")
        
        # Action Buttons Container
        with st.container():
            if role == ROLE_ADMIN:
                 if st.button("👨‍💼 User Management", use_container_width=True): 
                     st.session_state.current_page = "👨‍💼 User Management"
                     st.rerun()
                 if st.button("🔧 System Config", use_container_width=True): 
                     st.session_state.current_page = "🔧 System Config"
                     st.rerun()
                 from page.audit import view_audit_logs
                 if st.button("📋 Audit Logs", use_container_width=True): view_audit_logs()
            elif role == ROLE_OPERATIONS:
                 if st.button("🗺️ Open Vessel Map", use_container_width=True):
                     st.session_state.current_page = "🗺️ Vessel Map_DIRECT"
                     st.rerun()
                 st.button("📝 Create Report", use_container_width=True)
        
        st.markdown("### 🚢 Fleet Overview")
        fleet_df = pd.DataFrame([
            {"Status": "Operating", "Count": fleet.get('operating', 0), "Color": "#38bdf8"},
            {"Status": "Idle", "Count": fleet.get('idle', 0), "Color": "#94a3b8"},
            {"Status": "Maintenance", "Count": fleet.get('maintenance', 0), "Color": "#f472b6"},
        ])
        
        st.dataframe(
            fleet_df[["Status", "Count"]], 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Status": st.column_config.TextColumn("Status"), 
                "Count": st.column_config.ProgressColumn(
                    "Count", 
                    format="%d", 
                    min_value=0, 
                    max_value=int(max(fleet.get('total_vessels', 10), 1))
                )
            }
        )


@st.fragment(run_every=10)
def dashboard_content(role):
    # Data refreshing logic
    # Note: st.cache_data might prevent actual refresh if we don't clear it or if parameters don't change. 
    # But here get_dashboard_data calls underlying queries. 
    # To Ensure real freshness, the underlying queries should be cached with short TTL or we rely on this fragment 
    # rerunning and fetching new data.
    
    with st.spinner("🚀 Syncing live data..."):
        data = asyncio.run(data_manager.get_dashboard_data(role))
    
    render_dashboard_home(
        data['fleet'], 
        data['orders'], 
        data['financial'],
        role,
        data['settings'],
        data['clients']
    )

def dashboard_home_page():
    role = st.session_state.user_role
    dashboard_content(role)
