"""core/services/auth.py — moved from services/auth_service.py"""
from __future__ import annotations
import hashlib
import streamlit as st
from db.connection import sb_table
from db.repos.user import update_last_login_optimized

_MAX_ATTEMPTS  = 3
_LOCKOUT_SECS  = 300
_MAX_INPUT_LEN = 64


def _sanitize(value: str) -> str:
    return str(value).strip()[:_MAX_INPUT_LEN]


def _rate_check(username: str) -> tuple[bool, str]:
    import time
    lockout_until = st.session_state.get(f"_login_lockout_{username}", 0)
    if time.time() < lockout_until:
        remaining = int(lockout_until - time.time())
        return False, f"Terlalu banyak percobaan. Coba lagi dalam {remaining} detik."
    return True, ""


def _record_failure(username: str) -> None:
    import time
    key_a = f"_login_attempts_{username}"
    key_l = f"_login_lockout_{username}"
    count = st.session_state.get(key_a, 0) + 1
    st.session_state[key_a] = count
    if count >= _MAX_ATTEMPTS:
        st.session_state[key_l] = time.time() + _LOCKOUT_SECS
        st.session_state[key_a] = 0


def _clear_failures(username: str) -> None:
    st.session_state.pop(f"_login_attempts_{username}", None)
    st.session_state.pop(f"_login_lockout_{username}",  None)


def check_login_working(username: str, password: str):
    username = _sanitize(username)
    password = _sanitize(password)
    if not username or not password:
        st.error("⚠️ Username dan password wajib diisi.")
        return False, None
    allowed, msg = _rate_check(username)
    if not allowed:
        st.error(f"🔒 {msg}")
        return False, None
    try:
        mgmt = sb_table("operation", "user_managements")\
            .select("id_user")\
            .eq("id_user", username)\
            .eq("password", password)\
            .eq("status", "Active")\
            .execute()
        if not mgmt.data:
            _record_failure(username)
            st.error("⚠️ Username atau password salah.")
            return False, None
        user = sb_table("operation", "users")\
            .select("role")\
            .eq("code_user", username)\
            .eq("status", "Active")\
            .execute()
        if not user.data:
            _record_failure(username)
            st.error("⚠️ Akun tidak aktif.")
            return False, None
        _clear_failures(username)
        update_last_login_optimized(username, password)
        return True, user.data[0]["role"]
    except Exception:
        st.error("❌ Layanan sementara tidak tersedia. Coba lagi.")
        return False, None
