import streamlit as st
import pandas as pd
from sqlalchemy import text
from back.conection.conection import get_connection
from back.query.update import update_last_login_optimized

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
            FROM alpha.user_managements um
            JOIN alpha.users u ON um.id_user = u.code_user
            WHERE um.id_user = :username
                AND trim(um.password) = trim(:password)
                AND um.status = 'Active'
                AND u.status = 'Active'
        """)


        df = pd.read_sql(query, conn, params={"username": username, "password": password})

        if not df.empty:
            # Update last login
            success = update_last_login_optimized(username, password)
            if success:
                st.success("Login successful!")
            else:
                st.warning("Login successful but failed to update last login timestamp")
            return True, df.iloc[0]['role']
        else:
            st.error("Invalid username or password")
            return False, None
    except Exception as e:
        st.error(f"Login error: {e}")
        return False, None
    finally:
        if conn:
            conn.close()


def login_page():
    st.set_page_config(page_title="Login - Dashboard", layout="centered")
    st.title("Dashboard")
    st.markdown("---")

    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if username and password:
                with st.spinner("Checking credentials..."):
                    is_valid, user_role = check_login_working(username, password)

                if is_valid and user_role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_role = user_role
                    st.success(f"Welcome {username}!")
                    st.rerun()  # pakai st.rerun() bukan experimental_rerun
            else:
                st.warning("Please enter both username and password")
