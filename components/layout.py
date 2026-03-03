import time
import streamlit as st
from config.settings import ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE


def _get_brand():
    """Load branding from system_settings (cached by settings_repo).
    Returns tuple (app_name, gradient_css_value)."""
    try:
        from db.repositories.settings_repo import get_system_settings
        s = get_system_settings()
        name   = s.get("app_name", "⚓ MarineOS") or "⚓ MarineOS"
        color1 = s.get("theme_color_primary",   s.get("theme_color", "#0ea5e9")) or "#0ea5e9"
        color2 = s.get("theme_color_secondary", "#818cf8") or "#818cf8"
    except Exception:
        name, color1, color2 = "⚓ MarineOS", "#0ea5e9", "#818cf8"
    return name, color1, color2


def sidebar_nav():
    app_name, color1, color2 = _get_brand()

    with st.sidebar:
        st.markdown(f"""
            <div style="padding: 0.5rem 0 0.25rem 0;">
                <div style="
                    font-family: 'Outfit', sans-serif;
                    font-size: 1.3rem; font-weight: 900;
                    background: linear-gradient(90deg, {color1}, {color2});
                    -webkit-background-clip: text; background-clip: text;
                    -webkit-text-fill-color: transparent; color: transparent;
                    letter-spacing: -0.02em;
                ">{app_name}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.username:
            role_colors = {
                ROLE_ADMIN:      "#818cf8",
                ROLE_OPERATIONS: "#22c55e",
                ROLE_MARCOM:     "#f59e0b",
                ROLE_FINANCE:    "#0ea5e9"
            }
            role  = st.session_state.user_role
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
                        background: linear-gradient(135deg, {color1}, {color2});
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

        for item in menu:
            key_btn = f"nav_{item}"
            if st.button(
                item,
                key=key_btn,
                width="stretch",
                type="primary" if st.session_state.current_page == item else "secondary"
            ):
                st.session_state.current_page = item
                st.rerun()

        st.divider()

        if st.button("🚪 Keluar", key="logout", width="stretch"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()


def transition_loader(page):
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

    return loader_placeholder, should_show_loader


def close_loader(loader_placeholder, should_show_loader):
    if should_show_loader:
        time.sleep(1.2)
        loader_placeholder.empty()
