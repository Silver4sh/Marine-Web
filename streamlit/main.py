import streamlit as st
import sys
import os

# Konfigurasi Halaman (Harus di awal)
st.set_page_config(
    page_title="MarineOS Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚢"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Impor Tampilan
from views.auth import render_login_page
from views.monitoring import render_monitoring_view
from views.notifications import show_notification_dialog, count_unread_notifications
from views.analytics import render_analytics_page
from views.clients import render_clients_page
from views.admin import render_admin_page
from views.environment import render_environment_page
from views.survey import render_survey_page
from core import render_map_content, inject_custom_css, ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE

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
    'current_page': '🏠 Monitoring',
    'date_filter': 'Semua Waktu'
}

for key, default in required_states.items():
    if key not in st.session_state:
        st.session_state[key] = default


# --- Navigasi & Routing ---

def sidebar_nav():
    with st.sidebar:
        # Brand Header
        st.markdown("""
            <div style="padding: 0.5rem 0 0.25rem 0;">
                <div style="
                    font-family: 'Outfit', sans-serif;
                    font-size: 1.3rem; font-weight: 900;
                    background: linear-gradient(90deg, #0ea5e9, #818cf8);
                    -webkit-background-clip: text; background-clip: text;
                    -webkit-text-fill-color: transparent; color: transparent;
                    letter-spacing: -0.02em;
                ">⚓ MarineOS</div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.username:
            role_colors = {
                ROLE_ADMIN: "#818cf8",
                ROLE_OPERATIONS: "#22c55e",
                ROLE_MARCOM: "#f59e0b",
                ROLE_FINANCE: "#0ea5e9"
            }
            role = st.session_state.user_role
            color = role_colors.get(role, "#8ba3c0")
            st.markdown(f"""
                <div style="
                    display: flex; align-items: center; gap: 8px;
                    padding: 8px 10px;
                    background: rgba(255,255,255,0.04);
                    border-radius: 12px;
                    border: 1px solid rgba(255,255,255,0.07);
                    margin: 6px 0;
                ">
                    <div style="
                        width: 30px; height: 30px; border-radius: 50%;
                        background: linear-gradient(135deg, #0ea5e9, #818cf8);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 0.9rem; font-weight: 700; color: white;
                        font-family: 'Outfit', sans-serif;
                        flex-shrink: 0;
                    ">{st.session_state.username[0].upper()}</div>
                    <div>
                        <div style="font-size:0.82rem; font-weight:600; color:#f0f6ff; font-family:'Outfit',sans-serif; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:140px;">{st.session_state.username}</div>
                        <div style="font-size:0.7rem; color:{color}; font-weight:600; letter-spacing:0.04em;">{role}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        role = st.session_state.user_role
        menu = ["🏠 Monitoring", "🌊 Lingkungan"]

        if role in [ROLE_ADMIN, ROLE_OPERATIONS]:
            menu.extend(["🗺️ Peta Kapal", "📋 Survey"])

        if role in [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE]:
            menu.extend(["👥 Klien", "📈 Analitik"])

        if role == ROLE_ADMIN:
            menu.append("👨‍💼 Admin")

        # Render nav buttons
        for item in menu:
            key_btn = f"nav_{item}"
            if st.button(
                item,
                key=key_btn,
                use_container_width=True,
                type="primary" if st.session_state.current_page == item else "secondary"
            ):
                st.session_state.current_page = item
                st.rerun()

        st.divider()

        # Notification button with badge
        try:
            unread = count_unread_notifications(st.session_state.user_role)
        except Exception:
            unread = 0

        notif_label = f"🔔 Notifikasi  {'· ' + str(unread) if unread > 0 else ''}"
        if st.button(notif_label, key="notif_btn", use_container_width=True):
            show_notification_dialog()

        st.divider()

        if st.button("🚪 Keluar", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()


def render_page_header(icon: str, title: str, subtitle: str = ""):
    """Renders a consistent animated page header."""
    sub_html = f'<p class="page-header-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
        <div class="page-header">
            <div class="page-header-icon">{icon}</div>
            <div>
                <p class="page-header-title">{title}</p>
                {sub_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


def main_app():
    sidebar_nav()
    page = st.session_state.current_page

    # Page transition loader
    if "last_page" not in st.session_state:
        st.session_state.last_page = None

    should_show_loader = st.session_state.last_page != page
    if should_show_loader:
        st.session_state.last_page = page

    loader_placeholder = st.empty()

    if should_show_loader:
        loader_placeholder.markdown("""
            <div class="fullscreen-loader">
                <div class="sonar-wrapper">
                    <div class="sonar-emitter"></div>
                    <div class="sonar-wave"></div>
                    <div class="sonar-wave"></div>
                    <div class="sonar-wave"></div>
                </div>
                <div class="loader-text">Memuat Sistem...</div>
            </div>
        """, unsafe_allow_html=True)

    try:
        if page == "🏠 Monitoring":
            render_monitoring_view()

        elif page == "🌊 Lingkungan":
            render_environment_page()

        elif page == "🗺️ Peta Kapal" or page == "🗺️ Peta Kapal_DIRECT":
            if page == "🗺️ Peta Kapal_DIRECT":
                st.session_state.current_page = "🗺️ Peta Kapal"
            render_map_content()

        elif page == "📈 Analitik":
            render_analytics_page()

        elif page == "👥 Klien":
            render_clients_page()

        elif page == "👨‍💼 Admin":
            render_admin_page()

        elif page == "📋 Survey":
            render_survey_page()

    except Exception as e:
        st.error(f"Error loading page: {e}")

    finally:
        if should_show_loader:
            import time
            time.sleep(1.2)
            loader_placeholder.empty()


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
