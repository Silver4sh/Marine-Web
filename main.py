import logging
import streamlit as st

class _NoCtxFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "missing ScriptRunContext" not in record.getMessage()

logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context")\
    .addFilter(_NoCtxFilter())

logger = logging.getLogger(__name__)


# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="MarineOS Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚢",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from core.views.auth        import render_login_page
from core.views.monitoring  import render_monitoring_view
from core.views.analytics   import render_analytics_page
from core.views.clients     import render_clients_page
from core.views.admin       import render_admin_page
from core.views.client_portal import render_client_portal
from core.views.environment import render_environment_page
from core.views.survey      import render_survey_page
from core.views.alerts      import render_alerts_page
from core.views.voyage      import render_voyage_page
from core.views.maintenance import render_maintenance_page
from core.views.kpi_dashboard import render_kpi_dashboard
from core.ui.maps           import render_map_content
from core.config            import inject_custom_css
from core.ui.layout         import sidebar_nav, transition_loader, close_loader

# ── Inject global CSS ─────────────────────────────────────────────────────────
try:
    inject_custom_css()
except Exception as e:
    logger.error("Gagal memuat gaya: %s", e)

# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS = {
    "logged_in":    False,
    "username":     None,
    "user_role":    None,
    "current_page": "🏠 Monitoring",
    "date_filter":  "Semua Waktu",
}
for key, default in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Routing ───────────────────────────────────────────────────────────────────
def main_app():
    sidebar_nav()
    page = st.session_state.current_page
    loader_placeholder, should_show_loader = transition_loader(page)
    try:
        if   page == "🏠 Monitoring":   render_monitoring_view()
        elif page == "🌊 Lingkungan":   render_environment_page()
        elif page == "🗺️ Peta Kapal":  render_map_content()
        elif page == "📈 Analitik":     render_analytics_page()
        elif page == "👥 Klien":        render_clients_page()
        elif page == "👨‍💼 Admin":      render_admin_page()
        elif page == "📋 Survey":       render_survey_page()
        elif page == "🔔 Alert":        render_alerts_page()
        elif page == "🗓️ Voyage":      render_voyage_page()
        elif page == "🛠️ Maintenance": render_maintenance_page()
        elif page == "📊 KPI":          render_kpi_dashboard()
        elif page == "🌐 Portal Klien": render_client_portal()
    except Exception as e:
        logger.error(f"Halaman gagal dimuat", exc_info=e)
        st.error("⚠️ Maaf, halaman tidak dapat dimuat saat ini. Sila coba lagi nanti atau hubungi dukungan teknis.", icon="🚨")
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
        logger.error(f"Sistem mengalami kesalahan kritis", exc_info=e)
        st.error("⚠️ Sistem mengalami kesalahan kritis. Silakan muat ulang halaman atau hubungi dukungan teknis.", icon="🚨")
