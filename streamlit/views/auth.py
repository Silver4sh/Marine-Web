import streamlit as st
from sqlalchemy import text
from core.database import get_engine, update_last_login_optimized


def check_login_working(username: str, password: str):
    """Validates credentials against DB. Returns (success: bool, role: str|None)."""
    engine = get_engine()
    if engine is None:
        st.error("❌ Tidak dapat terhubung ke database.")
        return False, None

    try:
        with engine.connect() as conn:
            stmt = text("""
                SELECT um.id_user, u.role
                FROM operation.user_managements um
                JOIN operation.users u ON um.id_user = u.code_user
                WHERE um.id_user = :username
                  AND trim(um.password) = trim(:password)
                  AND um.status = 'Active'
                  AND u.status  = 'Active'
            """)
            result = conn.execute(stmt, {"username": username, "password": password})
            rows = result.fetchall()

        if rows:
            role = rows[0][1]  # u.role column
            update_last_login_optimized(username, password)
            return True, role
        else:
            st.error("⚠️ Username atau password salah. Coba lagi.")
            return False, None

    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return False, None


def render_login_page():
    # --- Animated Particle Background ---
    st.markdown("""
        <style>
        @keyframes particle-float {
            0%   { transform: translateY(0)   translateX(0)    scale(1);   opacity: 0.5; }
            50%  { transform: translateY(-60px) translateX(20px) scale(1.1); opacity: 0.8; }
            100% { transform: translateY(0)   translateX(0)    scale(1);   opacity: 0.5; }
        }
        .particle {
            position: fixed;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(14,165,233,0.6), transparent);
            pointer-events: none;
            z-index: 0;
            animation: particle-float linear infinite;
        }
        .login-wrap { position: relative; z-index: 1; }
        </style>
        <div class="particle" style="width:180px;height:180px;top:10%;left:5%;animation-duration:9s;opacity:0.3;"></div>
        <div class="particle" style="width:120px;height:120px;top:70%;left:8%;animation-duration:11s;animation-delay:2s;opacity:0.2;background:radial-gradient(circle,rgba(129,140,248,0.5),transparent);"></div>
        <div class="particle" style="width:200px;height:200px;top:20%;right:6%;animation-duration:13s;animation-delay:4s;opacity:0.2;background:radial-gradient(circle,rgba(20,184,166,0.4),transparent);"></div>
        <div class="particle" style="width:90px;height:90px;top:80%;right:10%;animation-duration:8s;animation-delay:1s;opacity:0.25;background:radial-gradient(circle,rgba(236,72,153,0.4),transparent);"></div>
    """, unsafe_allow_html=True)

    # --- Centered Layout ---
    c1, c2, c3 = st.columns([1, 1.6, 1])
    with c2:
        # Logo / Hero Header
        st.markdown("""
            <div class='login-header login-wrap' style='text-align: center; margin-bottom: 2rem; padding-top: 2rem;'>
                <div style='font-size:4rem; margin-bottom: 0.5rem; animation: float 4s ease-in-out infinite; display:inline-block;'>⚓</div>
                <h1 style='
                    font-family: Outfit, sans-serif;
                    font-size: 2.5rem; font-weight: 900; margin: 0;
                    background: linear-gradient(90deg, #0ea5e9, #818cf8, #ec4899, #14b8a6);
                    background-size: 300% 300%;
                    -webkit-background-clip: text; background-clip: text;
                    -webkit-text-fill-color: transparent; color: transparent;
                    animation: gradientShift 5s ease infinite;
                '>MarineOS</h1>
                <p style='color: #8ba3c0; font-size: 0.9rem; margin-top: 6px; letter-spacing: 0.05em;'>
                    Integrated Maritime Operations Platform
                </p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### Masuk ke Dashboard")

            username = st.text_input("Username", placeholder="👤  Username", label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="🔑  Password", label_visibility="collapsed")

            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button(
                "🚀  Masuk ke Sistem",
                type="primary",
                use_container_width=True
            )

            if submit_button:
                if username and password:
                    with st.spinner("Memeriksa kredensial..."):
                        is_valid, user_role = check_login_working(username, password)

                    if is_valid and user_role:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = user_role
                        st.toast(f"✅ Selamat datang, {username}!", icon="🚢")
                        st.rerun()
                else:
                    st.warning("⚠️ Harap masukkan username dan password.")
