import streamlit as st
import sys
import os

# Konfigurasi Halaman (Harus di awal)
st.set_page_config(
    page_title="Dasbor Analitik Marine",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚢"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Impor Tampilan Baru
from dashboard.views.auth import render_login_page
from dashboard.views.monitoring import render_monitoring_view, show_notification_dialog
from dashboard.views.analytics import render_analytics_page
from dashboard.views.clients import render_clients_page
from dashboard.views.admin import render_admin_page
from dashboard.views.environment import render_environment_page
from dashboard.core import render_map_content, inject_custom_css, ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE

# Memuat Gaya Global
try:
    inject_custom_css()
except Exception as e:
    print(f"Gagal memuat gaya: {e}")

# Inisialisasi State Sesi
required_states = {
    'logged_in': False,
    'username': None,
    'user_role': None,
    'current_page': '🏠 Pemantauan',
    'date_filter': 'Semua Waktu'
}

for key, default in required_states.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Navigasi & Routing ---

def sidebar_nav():
    with st.sidebar:
        st.markdown(f"## ⚓ MarineOS")
        if st.session_state.username:
            st.caption(f"Masuk sebagai: **{st.session_state.username}** ({st.session_state.user_role})")
        st.divider()
        
        role = st.session_state.user_role
        menu = ["🏠 Pemantauan", "🌊 Lingkungan"]
        
        if role in [ROLE_ADMIN, ROLE_OPERATIONS]:
            menu.extend(["🗺️ Peta Kapal"])
            
        if role in [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE]:
             menu.extend(["👥 Klien", "📈 Analitik"])
             
        if role == ROLE_ADMIN:
             menu.append("👨‍💼 Admin")
        
        # Render Tombol
        for item in menu:
            key_btn = f"nav_{item}"
            if st.button(item, key=key_btn, use_container_width=True, type="primary" if st.session_state.current_page == item else "secondary"):
                st.session_state.current_page = item
                st.rerun()

        st.divider()
        if st.button("🔔 Notifikasi", key="notif_btn", use_container_width=True):
            show_notification_dialog()
                
        st.divider()
        if st.button("🚪 Keluar", key="logout", use_container_width=True):
             st.session_state.logged_in = False
             st.session_state.username = None
             st.rerun()

def main_app():
    sidebar_nav()
    page = st.session_state.current_page
    
    if page == "🏠 Pemantauan":
        render_monitoring_view()

    elif page == "🌊 Lingkungan":
        render_environment_page()
    
    elif page == "🗺️ Peta Kapal" or page == "🗺️ Peta Kapal_DIRECT":
        if page == "🗺️ Peta Kapal_DIRECT": st.session_state.current_page = "🗺️ Peta Kapal"
        render_map_content()
        
    elif page == "📈 Analitik":
        render_analytics_page()
        
    elif page == "👥 Klien":
        render_clients_page()

    elif page == "👨‍💼 Admin":
        render_admin_page()

def main():
    if not st.session_state.logged_in:
        render_login_page()
    else:
        main_app()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"⚠️ Sistem mengalami kesalahan kritis: {e}")
        st.info("Silakan muat ulang halaman atau hubungi dukungan.")
