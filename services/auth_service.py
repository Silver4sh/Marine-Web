import streamlit as st
from db.connection import get_supabase
from db.repositories.user_repo import update_last_login_optimized


def check_login_working(username: str, password: str):
    """Validates credentials against DB. Returns (success: bool, role: str|None)."""
    try:
        sb = get_supabase()
        result = sb.schema("operation").table("user_managements")\
            .select("id_user, status")\
            .eq("id_user", username)\
            .eq("password", password)\
            .eq("status", "Active")\
            .execute()

        if not result.data:
            st.error("⚠️ Username atau password salah. Coba lagi.")
            return False, None

        # Get role from users table
        user = sb.schema("operation").table("users")\
            .select("role")\
            .eq("code_user", username)\
            .eq("status", "Active")\
            .execute()

        if not user.data:
            st.error("⚠️ Akun tidak aktif.")
            return False, None

        role = user.data[0]["role"]
        update_last_login_optimized(username, password)
        return True, role

    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return False, None
