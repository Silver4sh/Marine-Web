from __future__ import annotations
import hashlib
import streamlit as st
from db.connection import sb_table
from db.repositories.user_repo import update_last_login_optimized

# ── Security constants ─────────────────────────────────────────────────────────
_MAX_ATTEMPTS  = 5          # max failed logins before lockout
_LOCKOUT_SECS  = 300        # lockout duration: 5 minutes
_MAX_INPUT_LEN = 64         # max length for username / password input


def _sanitize(value: str) -> str:
    """Strip whitespace and enforce max length."""
    return str(value).strip()[:_MAX_INPUT_LEN]


def _rate_check(username: str) -> tuple[bool, str]:
    """
    Returns (allowed, message).
    Tracks failed attempts per username in st.session_state.
    """
    import time
    key_attempts = f"_login_attempts_{username}"
    key_lockout  = f"_login_lockout_{username}"

    lockout_until = st.session_state.get(key_lockout, 0)
    if time.time() < lockout_until:
        remaining = int(lockout_until - time.time())
        return False, f"Terlalu banyak percobaan. Coba lagi dalam {remaining} detik."

    return True, ""


def _record_failure(username: str) -> None:
    """Increment failure count; lock out if threshold reached."""
    import time
    key_attempts = f"_login_attempts_{username}"
    key_lockout  = f"_login_lockout_{username}"

    count = st.session_state.get(key_attempts, 0) + 1
    st.session_state[key_attempts] = count
    if count >= _MAX_ATTEMPTS:
        st.session_state[key_lockout]  = time.time() + _LOCKOUT_SECS
        st.session_state[key_attempts] = 0


def _clear_failures(username: str) -> None:
    """Reset failure counter on successful login."""
    st.session_state.pop(f"_login_attempts_{username}", None)
    st.session_state.pop(f"_login_lockout_{username}",  None)


def check_login_working(username: str, password: str):
    """
    Validates credentials. Returns (success: bool, role: str|None).
    - Inputs are sanitized
    - Rate-limited: 5 failed attempts → 5-minute lockout
    """
    username = _sanitize(username)
    password = _sanitize(password)

    if not username or not password:
        st.error("⚠️ Username dan password wajib diisi.")
        return False, None

    # Rate limit check
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
        # Never expose internal errors to user in production
        st.error("❌ Layanan sementara tidak tersedia. Coba lagi.")
        return False, None
