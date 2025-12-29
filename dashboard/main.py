import streamlit as st

st.set_page_config(
    page_title="Marine Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚢"
)
import asyncio
import pandas as pd
import plotly.express as px
import sys
import os
from concurrent.futures import ThreadPoolExecutor


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Pages & Logic
from back.conection.login import login_page
from back.query.update import update_password
from back.src.map import page_map_vessel
from back.src.heatmap import page_heatmap, radar_chart
from back.src.graph_histories import page_history_graph

# Import Queries
from back.query.queries import (
    get_fleet_status,
    get_financial_metrics,
    get_order_stats,
    get_revenue_analysis,
    get_clients_summary,
    get_logs
)

# Constants
ROLE_OPERATIONS = "Operations"
ROLE_MARCOM = "Marcom"
ROLE_ADMIN = "Admin"
ROLE_FINANCE = "Finance"



# Load CSS
def load_css():
    try:
        css_path = os.path.join(current_dir, "front/asset/style/css/style.css")
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Style file not found. UI experience might be degraded.")

load_css()

# Session State Initialization
required_states = {
    'logged_in': False,
    'username': None,
    'user_role': None,
    'current_page': '🏠 Dashboard',
    'date_filter': 'All Time'
}

for key, default in required_states.items():
    if key not in st.session_state:
        st.session_state[key] = default

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

        results = await asyncio.gather(*tasks)
        return {
            "fleet": results[0],
            "orders": results[1],
            "financial": results[2]
        }

data_manager = AsyncDataManager()

# --- Dashboard Components ---

def load_html(filename):
    file_path = os.path.join(current_dir, "front/asset/style/html", filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def render_metric_card(label, value, delta=None, color="green"):
    html_template = load_html("metric_card.html")
    if not html_template:
        st.error("Metric card template missing")
        return
        
    delta_html = ""
    if delta:
        # Simple extraction of the delta section would be better with a proper template engine
        # But here we will simpler string replacement for now
        delta_html = delta
        
    # Hacky but effective template filling
    card_html = html_template.replace("{label}", str(label)) \
                             .replace("{value}", str(value)) \
                             .replace("{delta}", str(delta) if delta else "") \
                             .replace("{delta_color}", color)
                             
    # Remove delta section if no delta (Optional improvement: use regex or separate templates)
    if not delta:
        import re
        card_html = re.sub(r'<!-- delta_section -->.*?<!-- end_delta_section -->', '', card_html, flags=re.DOTALL)
        
    # Minify HTML to prevent Markdown issues
    card_html = card_html.replace("\n", " ").strip()
    st.markdown(card_html, unsafe_allow_html=True)

@st.dialog("Audit Logs")
def view_audit_logs():
    st.write("Recent entries from Vibrocore Logs")
    df = get_logs()
    if not df.empty:
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "created_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, h:mm a")
            }
        )
    else:
        st.info("No audit logs found.")

def dashboard_home():
    role = st.session_state.user_role
    
    with st.spinner("🚀 Syncing live data..."):
        data = asyncio.run(data_manager.get_dashboard_data(role))
    
    fleet = data['fleet']
    orders = data['orders']
    financial = data['financial']
    
    render_dashboard_home(fleet, orders, financial, role)
            }
        )

def render_dashboard_home(fleet, orders, financial, role):
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
                 fig.update_layout(
                     paper_bgcolor='rgba(0,0,0,0)', 
                     plot_bgcolor='rgba(0,0,0,0)',
                     font=dict(family="Outfit", color="#8b9bb4"),
                     title_font_color="#f8fafc",
                     xaxis=dict(showgrid=False),
                     yaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)")
                 )
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
                 fig.update_layout(
                     paper_bgcolor='rgba(0,0,0,0)',
                     font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
                     showlegend=True,
                     legend=dict(orientation="h", y=-0.1)
                 )
                 fig.update_traces(textinfo='none', hoverinfo='label+percent+value')
                 st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.subheader("⚡ Actions")
        
        # Action Buttons Container
        with st.container():
            if role == ROLE_ADMIN:
                 if st.button("👨‍💼 User Management", use_container_width=True): pass
                 if st.button("🔧 System Config", use_container_width=True): pass
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
                    max_value=max(fleet.get('total_vessels', 10), 1)
                )
            }
        )

def render_heatmap_page():
     st.markdown("## 🔥 Environmental Heatmap")
        
     # --- Data Loading ---
     from back.query.queries import get_data_water
     
     # Load data (Cached)
     df = get_data_water()
     
     # Layout Containers
     c_overview = st.container()
     st.divider()
     c_map = st.container()
     st.divider()
     c_filter = st.container()

     # --- Filter Logic (Bottom) ---
     filtered_df = df # Default
     if not df.empty and 'latest_timestamp' in df.columns:
         valid_dates = pd.to_datetime(df['latest_timestamp'], errors='coerce').dropna()
         if not valid_dates.empty:
             df['latest_timestamp'] = pd.to_datetime(df['latest_timestamp'])
             min_date = valid_dates.min().date()
             max_date = valid_dates.max().date()
             if min_date == max_date:
                 min_date = min_date - pd.Timedelta(days=1)
             
             with c_filter:
                 st.markdown("### 🗓️ Filter Tanggal")
                 date_range = st.slider(
                     "Geser untuk memfilter data:",
                     min_value=min_date,
                     max_value=max_date,
                     value=(min_date, max_date),
                     format="DD/MM/YY"
                 )
                 
                 # Apply Filter
                 mask = (df['latest_timestamp'].dt.date >= date_range[0]) & (df['latest_timestamp'].dt.date <= date_range[1])
                 filtered_df = df[mask]
     
     # --- Area Overview (Top) ---
     with c_overview:
         st.markdown("### 🕸️ Area Overview")
         radar_chart(filtered_df)

     # --- Maps (Middle) ---
     with c_map:
         tab_main_sel = st.radio("Select Category", ["Water Quality", "Oceanographic"], horizontal=True)
         
         if tab_main_sel == "Water Quality":
              col1, col2 = st.columns(2)
              with col1: 
                  st.write("**Salinity**")
                  page_heatmap(filtered_df, "salinitas")
              with col2:
                  st.write("**Turbidity**")
                  page_heatmap(filtered_df, "turbidity")
              
              st.markdown("**Oxygen**", help="Dissolved Oxygen levels")
              page_heatmap(filtered_df, "oxygen")
              
         else:
              col1, col2 = st.columns(2)
              with col1:
                  st.write("**Current**")
                  page_heatmap(filtered_df, "current")
              with col2:
                  st.write("**Tide**")
                  page_heatmap(filtered_df, "tide")
             
              st.markdown("**Density**", help="Seawater Density")
              page_heatmap(filtered_df, "density")

# --- Navigation & Routing ---

def sidebar_nav():
    with st.sidebar:
        st.markdown(f"## ⚓ MarineOS")
        st.caption(f"Logged in as: **{st.session_state.username}** ({st.session_state.user_role})")
        st.divider()
        
        # Navigation Items based on Role
        role = st.session_state.user_role
        
        menu = ["🏠 Dashboard"]
        
        if role in [ROLE_ADMIN, ROLE_OPERATIONS]:
            menu.extend(["🗺️ Vessel Map", "🔥 Heatmap", "📈 Sensors History"])
            
        if role in [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE]:
             menu.extend(["👥 Clients", "📈 Analytics"])
             
        menu.append("⚙️ Settings")
        
        # Render Buttons
        for item in menu:
            k = f"nav_{item}"
            if st.button(item, key=k, use_container_width=True, type="primary" if st.session_state.current_page == item else "secondary"):
                st.session_state.current_page = item
                st.rerun()
                
        st.divider()
        if st.button("🚪 Logout", key="logout", use_container_width=True):
             st.session_state.logged_in = False
             st.session_state.username = None
             st.rerun()

def main_app():
    sidebar_nav()
    page = st.session_state.current_page
    
    if page == "🏠 Dashboard":
        dashboard_home()
    
    elif page == "🗺️ Vessel Map" or page == "🗺️ Vessel Map_DIRECT":
        if page == "🗺️ Vessel Map_DIRECT": st.session_state.current_page = "🗺️ Vessel Map"
        page_map_vessel()
        
    elif page == "🔥 Heatmap":
        render_heatmap_page()

    elif page == "📈 Sensors History":
        st.markdown("## 📈 Historical Sensor Data")
        page_history_graph()
        
    elif page == "👥 Clients":
        st.markdown("## 👥 Client Portfolio")
        df = get_clients_summary()
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Total Clients", len(df))
            c2.metric("Active Regions", df['region'].nunique())
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No client data found.")

    elif page == "⚙️ Settings":
        st.markdown("## ⚙️ Account Settings")
        with st.container():
            st.warning("⚠️ Security Zone")
            u = st.session_state.username
            c_pass = st.text_input("Current Password", type="password")
            n_pass = st.text_input("New Password", type="password")
            cn_pass = st.text_input("Confirm Password", type="password")
            
            if st.button("Update Credential"):
                if n_pass != cn_pass:
                    st.error("passwords do not match")
                else:
                    success, msg = update_password(u, c_pass, n_pass)
                    if success: st.success(msg)
                    else: st.error(msg)

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Global Error Boundary
        st.error(f"⚠️ System encountered a critical error: {e}")
        st.info("Please refresh the page or contact support.")
