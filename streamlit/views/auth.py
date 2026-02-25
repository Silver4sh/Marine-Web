"""
views/auth.py
=============
UI layer untuk halaman login.

Tanggung jawab:
  - Merender form login
  - Verifikasi kredensial ke database
  - Setup session_state setelah login sukses
"""
import streamlit as st
import pandas as pd
from sqlalchemy import text

from core import get_connection, update_last_login_optimized


# ---------------------------------------------------------------------------
# Backend helper (private)
# ---------------------------------------------------------------------------

def _verify_credentials(username: str, password: str) -> tuple[bool, str | None]:
    """
    Memverifikasi username + password ke database.

    Returns:
        (True, role_str)  — jika login valid dan akun aktif
        (False, None)     — jika gagal
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            st.error("❌ Tidak bisa terhubung ke database. Hubungi administrator.")
            return False, None

        query = text("""
            SELECT um.id_user, u.role
            FROM   operation.user_managements um
            JOIN   operation.users u ON um.id_user = u.code_user
            WHERE  um.id_user       = :username
              AND  trim(um.password) = trim(:password)
              AND  um.status         = 'Active'
              AND  u.status          = 'Active'
        """)
        df = pd.read_sql(query, conn, params={"username": username, "password": password})

        if df.empty:
            st.error("❌ Nama pengguna atau kata sandi salah, atau akun tidak aktif.")
            return False, None

        # Update last_login (best-effort, tidak blokir login jika gagal)
        update_last_login_optimized(username, password)
        return True, df.iloc[0]["role"]

    except Exception as exc:
        st.error(f"❌ Kesalahan sistem saat login: {exc}")
        return False, None
    finally:
        if conn is not None:
            conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_login_page() -> None:
    """Entry point halaman login — dipanggil dari main.py ketika belum logged in."""
    _, col, _ = st.columns([1, 2, 1])

    with col:
        st.markdown(
            "<div style='text-align:center; margin-bottom:2rem;'>"
            "<h1>⚓ MarineOS</h1>"
            "<p style='color:#94a3b8;'>Sistem Manajemen Armada Maritim</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            st.markdown("### Masuk ke Dashboard")
            username = st.text_input("Nama Pengguna", placeholder="Masukkan nama pengguna")
            password = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔑 Masuk", type="primary", width='stretch')

        if submitted:
            if not username or not password:
                st.warning("⚠️ Harap masukkan nama pengguna dan kata sandi.")
                return

            with st.spinner("Memeriksa kredensial..."):
                is_valid, role = _verify_credentials(username, password)

            if is_valid and role:
                st.session_state.logged_in  = True
                st.session_state.username   = username
                st.session_state.user_role  = role
                st.rerun()
