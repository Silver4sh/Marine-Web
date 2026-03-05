from __future__ import annotations
import hashlib
import pandas as pd
from datetime import datetime, timezone
from db.connection import sb_table

_MAX_LEN = 64  # max input length for username / password


def _hash(password: str) -> str:
    """SHA-256 hash for password comparison (stored as hex digest)."""
    return hashlib.sha256(password.strip().encode()).hexdigest()


def _clean(value: str) -> str:
    """Strip whitespace and cap length."""
    return str(value).strip()[:_MAX_LEN]


def get_all_users() -> pd.DataFrame:
    users = pd.DataFrame(sb_table("operation", "users")
        .select("code_user, role, status").order("code_user").execute().data)
    mgmt  = pd.DataFrame(sb_table("operation", "user_managements")
        .select("id_user, status, last_login").execute().data)
    if users.empty:
        return pd.DataFrame()

    return users.merge(mgmt, left_on="code_user", right_on="id_user", how="left")\
        .rename(columns={"status_x": "user_status", "status_y": "account_status", "id_user": "username"})\
        [["code_user", "username", "role", "user_status", "account_status", "last_login"]]


def create_new_user(username: str, password: str, role: str) -> tuple[bool, str]:
    username = _clean(username)
    password = _clean(password)
    try:
        if sb_table("operation", "users").select("code_user")\
                .eq("code_user", username).execute().data:
            return False, "Pengguna sudah ada."
        sb_table("operation", "users")\
            .insert({"code_user": username, "role": role, "status": "Active"}).execute()
        sb_table("operation", "user_managements")\
            .insert({"id_user": username, "password": password, "status": "Active"}).execute()
        return True, "Berhasil dibuat."
    except Exception as e:
        return False, str(e)


def update_user_status(username: str, new_status: str) -> bool:
    try:
        username = _clean(username)
        sb_table("operation", "users").update({"status": new_status})\
            .eq("code_user", username).execute()
        sb_table("operation", "user_managements").update({"status": new_status})\
            .eq("id_user", username).execute()
        return True
    except Exception:
        return False


def update_user_role(username: str, new_role: str) -> bool:
    try:
        sb_table("operation", "users").update({"role": new_role})\
            .eq("code_user", _clean(username)).execute()
        return True
    except Exception:
        return False


def delete_user(username: str) -> bool:
    try:
        username = _clean(username)
        sb_table("operation", "user_managements").delete().eq("id_user", username).execute()
        sb_table("operation", "users").delete().eq("code_user", username).execute()
        return True
    except Exception:
        return False


def update_last_login_optimized(username: str, password: str) -> bool:
    try:
        sb_table("operation", "user_managements")\
            .update({"last_login": datetime.now(timezone.utc).isoformat()})\
            .eq("id_user", _clean(username)).eq("password", _clean(password)).execute()
        return True
    except Exception:
        return False


def update_password(username: str, old_pass: str, new_pass: str) -> tuple[bool, str]:
    old_pass = _clean(old_pass)
    new_pass = _clean(new_pass)
    if old_pass == new_pass:
        return False, "Kata sandi identik"
    try:
        check = sb_table("operation", "user_managements").select("id_user")\
            .eq("id_user", _clean(username)).eq("password", old_pass).execute()
        if not check.data:
            return False, "Kredensial salah"
        sb_table("operation", "user_managements")\
            .update({"password": new_pass}).eq("id_user", _clean(username)).execute()
        return True, "Berhasil"
    except Exception as e:
        return False, str(e)
