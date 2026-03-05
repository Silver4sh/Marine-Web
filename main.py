import logging
import time
import streamlit as st

# ── Suppress 'missing ScriptRunContext' noise from background threads ──────────
# Supabase-py (httpx / realtime) spins up internal threads that don't hold a
# Streamlit script context.  These are harmless, but flood the log in production.
class _NoCtxFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "missing ScriptRunContext" not in record.getMessage()

logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context")\
    .addFilter(_NoCtxFilter())


# Konfigurasi Halaman (Harus di awal)
st.set_page_config(
    page_title="MarineOS Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚢"
)

# Impor Tampilan
from views.auth import render_login_page
from views.monitoring import render_monitoring_view
from views.analytics import render_analytics_page
from views.clients import render_clients_page
from views.admin import render_admin_page
from views.environment import render_environment_page
from views.survey import render_survey_page
from components.visualizations import render_map_content
from config.settings import inject_custom_css
from components.layout import sidebar_nav, transition_loader, close_loader

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

def main_app():
    sidebar_nav()
    page = st.session_state.current_page

    loader_placeholder, should_show_loader = transition_loader(page)

    try:
        if page == "🏠 Monitoring":
            render_monitoring_view()
        elif page == "🌊 Lingkungan":
            render_environment_page()
        elif page == "🗺️ Peta Kapal":
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
        close_loader(loader_placeholder, should_show_loader)


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
