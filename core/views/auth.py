import streamlit as st
from core.services.auth import check_login_working


def render_login_page():
    # ── Animated geometric background ──────────────────────────────────────────
    st.markdown("""
        <style>
        @keyframes particle-float {
            0%   { transform: translateY(0) translateX(0) scale(1);    opacity: 0.4; }
            50%  { transform: translateY(-55px) translateX(18px) scale(1.08); opacity: 0.7; }
            100% { transform: translateY(0) translateX(0) scale(1);    opacity: 0.4; }
        }
        @keyframes grid-pan {
            0%   { transform: translateY(0); }
            100% { transform: translateY(60px); }
        }
        .login-bg-particle {
            position: fixed;
            border-radius: 50%;
            pointer-events: none;
            z-index: 0;
            animation: particle-float linear infinite;
        }
        .login-grid {
            position: fixed;
            inset: 0;
            z-index: 0;
            background-image:
                linear-gradient(rgba(239,68,68,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(239,68,68,0.04) 1px, transparent 1px);
            background-size: 60px 60px;
            animation: grid-pan 8s linear infinite;
            pointer-events: none;
        }
        .login-wrap { position: relative; z-index: 1; }
        </style>
        <div class="login-grid"></div>
        <div class="login-bg-particle" style="width:220px;height:220px;top:8%;left:3%;
             animation-duration:10s;opacity:0.25;
             background:radial-gradient(circle, rgba(239,68,68,0.45), transparent 70%);"></div>
        <div class="login-bg-particle" style="width:140px;height:140px;top:65%;left:6%;
             animation-duration:13s;animation-delay:2s;opacity:0.18;
             background:radial-gradient(circle, rgba(245,158,11,0.40), transparent 70%);"></div>
        <div class="login-bg-particle" style="width:240px;height:240px;top:15%;right:4%;
             animation-duration:14s;animation-delay:4s;opacity:0.18;
             background:radial-gradient(circle, rgba(239,68,68,0.30), transparent 70%);"></div>
        <div class="login-bg-particle" style="width:100px;height:100px;top:80%;right:8%;
             animation-duration:9s;animation-delay:1s;opacity:0.22;
             background:radial-gradient(circle, rgba(251,146,60,0.40), transparent 70%);"></div>
    """, unsafe_allow_html=True)

    # ── Centered layout ─────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        # Hero header
        st.markdown("""
            <div class='login-wrap' style='text-align: center; margin-bottom: 2.2rem; padding-top: 2rem;'>
                <div style='
                    font-size: 3.8rem;
                    margin-bottom: 0.75rem;
                    animation: float 4s ease-in-out infinite;
                    display: inline-block;
                    filter: drop-shadow(0 0 18px rgba(239,68,68,0.65));
                '>⚓</div>
                <h1 style='
                    font-family: Outfit, sans-serif;
                    font-size: 2.6rem; font-weight: 900; margin: 0;
                    background: linear-gradient(135deg, #ef4444, #f59e0b, #fb923c);
                    background-size: 200% 200%;
                    -webkit-background-clip: text; background-clip: text;
                    -webkit-text-fill-color: transparent; color: transparent;
                    animation: gradientShift 5s ease infinite;
                    letter-spacing: -0.03em;
                '>MarineOS</h1>
                <p style='
                    color: #64748b;
                    font-size: 0.85rem;
                    margin-top: 8px;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    font-family: Inter, sans-serif;
                '>Integrated Maritime Operations Platform</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("""
                <div style='
                    font-family: Outfit, sans-serif;
                    font-size: 1.15rem;
                    font-weight: 700;
                    color: #f1f5f9;
                    margin-bottom: 20px;
                    text-align: center;
                '>Masuk ke Dashboard</div>
            """, unsafe_allow_html=True)

            username = st.text_input(
                "Username",
                placeholder="👤  Username",
                label_visibility="collapsed"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="🔑  Password",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("🚀  Masuk ke Sistem")

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
                        st.error("❌ Username atau password salah.")
                else:
                    st.warning("⚠️ Harap masukkan username dan password.")

        # Footer note
        st.markdown("""
            <div style='
                text-align: center;
                margin-top: 1.5rem;
                color: #334155;
                font-size: 0.72rem;
                font-family: Inter, sans-serif;
                letter-spacing: 0.04em;
            '>🔒 Secure Maritime Intelligence Platform · v4.0</div>
        """, unsafe_allow_html=True)
