import streamlit as st
from sqlalchemy import text
from db.connection import get_engine
from db.repositories.user_repo import update_last_login_optimized

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
            role = rows[0][1]
            update_last_login_optimized(username, password)
            return True, role
        else:
            st.error("⚠️ Username atau password salah. Coba lagi.")
            return False, None

    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return False, None
