import streamlit as st
import sys
import os

# Set page config must be first
st.set_page_config(
    page_title="Marine Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚢"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Pages & Logic
from page.auth import render_login_page
from back.src.map import page_map_vessel
from back.src.graph_histories import page_history_graph
from back.src.constants import ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE
from back.src.utils import apply_chart_style

# Import New Page Modules
from page.home import dashboard_home_page
from page.clients import render_clients_page
from page.settings import render_settings_page
from page.analytics import render_analytics_page
from page.analytics import render_analytics_page
from page.environmental import render_heatmap_page
from page.user_management import render_user_management_page
from page.system_config import render_system_config_page
from page.notifications import render_notification_page

# Load Global CSS (Refactored to check availability)
def load_css():
    try:
        from back.src.styles import inject_custom_css
        inject_custom_css()
    except Exception as e:
        print(f"Style loading failed: {e}")

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

# --- Navigation & Routing ---

def sidebar_nav():
    with st.sidebar:
        st.markdown(f"## ⚓ MarineOS")
        if st.session_state.username:
            st.caption(f"Logged in as: **{st.session_state.username}** ({st.session_state.user_role})")
        st.divider()
        
        # Navigation Items based on Role
        role = st.session_state.user_role
        
        menu = ["🏠 Dashboard"]
        
        if role in [ROLE_ADMIN, ROLE_OPERATIONS]:
            menu.extend(["🗺️ Vessel Map", "🔥 Heatmap", "📈 Sensors History"])
            
        if role in [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE]:
             menu.extend(["👥 Clients", "📈 Analytics"])
             
        menu.extend(["🔔 Notifications", "⚙️ Settings"])
        
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
        dashboard_home_page()
    
    elif page == "🗺️ Vessel Map" or page == "🗺️ Vessel Map_DIRECT":
        if page == "🗺️ Vessel Map_DIRECT": st.session_state.current_page = "🗺️ Vessel Map"
        page_map_vessel()
        
    elif page == "🔥 Heatmap":
        render_heatmap_page()

    elif page == "📈 Sensors History":
        st.markdown("## 📈 Historical Sensor Data")
        page_history_graph()
    
    elif page == "📈 Analytics":
        render_analytics_page()
        
    elif page == "👥 Clients":
        render_clients_page()

    elif page == "⚙️ Settings":
        render_settings_page()

    elif page == "👨‍💼 User Management":
        render_user_management_page()

    elif page == "🔧 System Config":
        render_system_config_page()

    elif page == "🔔 Notifications":
        render_notification_page()

def main():
    if not st.session_state.logged_in:
        render_login_page()
    else:
        main_app()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Global Error Boundary
        st.error(f"⚠️ System encountered a critical error: {e}")
        st.info("Please refresh the page or contact support.")
