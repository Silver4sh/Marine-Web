import streamlit as st
import pandas as pd
from sqlalchemy import text
from core import get_connection, update_last_login_optimized

def check_login_working(username: str, password: str):
    try:
        conn = get_connection()
        if conn is None:
            return False, None

        query = text("""
            SELECT 
                um.id_user,
                um.password,
                u.role,
                u.status as user_status,
                um.status as account_status
            FROM operation.user_managements um
            JOIN operation.users u ON um.id_user = u.code_user
            WHERE um.id_user = :username
                AND trim(um.password) = trim(:password)
                AND um.status = 'Active'
                AND u.status = 'Active'
        """)

        df = pd.read_sql(query, conn, params={"username": username, "password": password})

        if not df.empty:
            success = update_last_login_optimized(username, password)
            if success:
                st.success("Login berhasil!")
            else:
                st.warning("Login berhasil tetapi gagal memperbarui waktu login terakhir")
            return True, df.iloc[0]['role']
        else:
            st.error("Nama pengguna atau kata sandi salah")
            return False, None
    except Exception as e:
        st.error(f"Kesalahan login: {e}")
        return False, None
    finally:
        if conn:
            conn.close()


def render_login_page():
    # Centered Layout
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<div class='login-header' style='text-align: center; margin-bottom: 2rem;'><h1>⚓ MarineOS</h1></div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Masuk ke Dashboard")
            username = st.text_input("Nama Pengguna", placeholder="Masukkan nama pengguna")
            password = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Masuk", type="primary", use_container_width=True)

            if submit_button:
                if username and password:
                    with st.spinner("Memeriksa kredensial..."):
                        is_valid, user_role = check_login_working(username, password)

                    if is_valid and user_role:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = user_role
                        st.success(f"Selamat datang {username}!")
                        st.rerun()
                else:
                    st.warning("Harap masukkan nama pengguna dan kata sandi")
