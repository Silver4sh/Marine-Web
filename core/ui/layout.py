"""core/ui/layout.py — moved from components/layout.py"""
import time
import streamlit as st
from core.config import ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE
from core.services.alert import get_unacknowledged_count


def _get_brand():
    try:
        from db.repos.settings import get_system_settings
        s      = get_system_settings()
        name   = s.get("app_name", "⚓ MarineOS") or "⚓ MarineOS"
        color1 = s.get("theme_color_primary",   s.get("theme_color", "#ef4444")) or "#ef4444"
        color2 = s.get("theme_color_secondary", "#f59e0b") or "#f59e0b"
    except Exception:
        name, color1, color2 = "⚓ MarineOS", "#ef4444", "#f59e0b"
    return name, color1, color2


def change_page(page_name):
    st.session_state.current_page = page_name


def do_logout():
    st.session_state.logged_in = False
    st.session_state.username  = None


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
                ROLE_FINANCE:    "#0ea5e9",
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
                        font-family: 'Outfit', sans-serif; flex-shrink: 0;
                    ">{st.session_state.username[0].upper()}</div>
                    <div>
                        <div style="font-size:0.82rem; font-weight:600; color:#f0f6ff;
                                    font-family:'Outfit',sans-serif; white-space:nowrap;
                                    overflow:hidden; text-overflow:ellipsis; max-width:140px;">{st.session_state.username}</div>
                        <div style="font-size:0.7rem; color:{color}; font-weight:600; letter-spacing:0.04em;">{role}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        role = st.session_state.user_role
        # Build alert label with unread badge
        unread = get_unacknowledged_count()
        alert_label = f"🔔 Alert ({unread})" if unread > 0 else "🔔 Alert"

        menu = ["🏠 Monitoring", "🌊 Lingkungan"]
        if role in [ROLE_ADMIN, ROLE_OPERATIONS]:
            menu.extend(["🗺️ Peta Kapal", "🗓️ Voyage", "🛠️ Maintenance", "📋 Survey"])
        if role in [ROLE_ADMIN, ROLE_MARCOM, ROLE_FINANCE]:
            menu.extend(["👥 Klien", "📈 Analitik"])
        if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
            menu.append("📊 KPI")
        if role == ROLE_ADMIN:
            menu.append("👨‍💼 Admin")
        # Alert always visible to all roles
        menu.append(alert_label)

        for item in menu:
            # Match current page even if alert label has count suffix
            is_active = (
                st.session_state.current_page == item
                or (item.startswith("🔔 Alert") and st.session_state.current_page == "🔔 Alert")
            )
            # Normalize alert page name on click
            target = "🔔 Alert" if item.startswith("🔔 Alert") else item
            st.button(
                item,
                key=f"nav_{item}",
                type="primary" if is_active else "secondary",
                on_click=change_page,
                args=(target,),
            )
        st.divider()
        st.button("🚪 Keluar", key="logout", on_click=do_logout)


def transition_loader(page):
    if "last_page" not in st.session_state:
        st.session_state.last_page = None
    should_show = st.session_state.last_page != page
    if should_show:
        st.session_state.last_page = page
    placeholder = st.empty()
    if should_show:
        placeholder.markdown("""
            <style>
                .fullscreen-loader-auto-hide {
                    animation: fadeOutLoader 0.5s ease-in-out 1.2s forwards;
                }
                @keyframes fadeOutLoader {
                    to { opacity: 0; visibility: hidden; pointer-events: none; display: none; }
                }
            </style>
            <div class="fullscreen-loader fullscreen-loader-auto-hide">
                <div class="sonar-wrapper">
                    <div class="sonar-emitter"></div>
                    <div class="sonar-wave"></div>
                    <div class="sonar-wave"></div>
                    <div class="sonar-wave"></div>
                </div>
                <div class="loader-text">Memuat Sistem...</div>
            </div>
        """, unsafe_allow_html=True)
    return placeholder, should_show


def close_loader(loader_placeholder, should_show_loader):
    pass  # CSS animation handles fade-out natively
