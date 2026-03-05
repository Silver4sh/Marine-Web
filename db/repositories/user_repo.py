import pandas as pd
from db.connection import get_supabase


def get_all_users():
    sb = get_supabase()
    users = pd.DataFrame(sb.schema("operation").table("users")
        .select("code_user, role, status").order("code_user").execute().data)
    mgmt  = pd.DataFrame(sb.schema("operation").table("user_managements")
        .select("id_user, status, last_login").execute().data)

    if users.empty:
        return pd.DataFrame()

    df = users.merge(mgmt, left_on="code_user", right_on="id_user", how="left")
    df = df.rename(columns={
        "status_x": "user_status",
        "status_y": "account_status",
        "id_user":  "username",
    })
    return df[["code_user", "username", "role", "user_status", "account_status", "last_login"]]


def create_new_user(username, password, role):
    try:
        sb = get_supabase()
        existing = sb.schema("operation").table("users")\
            .select("code_user").eq("code_user", username).execute()
        if existing.data:
            return False, "Pengguna sudah ada."
        sb.schema("operation").table("users")\
            .insert({"code_user": username, "role": role, "status": "Active"}).execute()
        sb.schema("operation").table("user_managements")\
            .insert({"id_user": username, "password": password, "status": "Active"}).execute()
        return True, "Berhasil dibuat."
    except Exception as e:
        return False, str(e)


def update_user_status(username, new_status):
    try:
        sb = get_supabase()
        sb.schema("operation").table("users")\
            .update({"status": new_status}).eq("code_user", username).execute()
        sb.schema("operation").table("user_managements")\
            .update({"status": new_status}).eq("id_user", username).execute()
        return True
    except Exception:
        return False


def update_user_role(username, new_role):
    try:
        sb = get_supabase()
        sb.schema("operation").table("users")\
            .update({"role": new_role}).eq("code_user", username).execute()
        return True
    except Exception:
        return False


def delete_user(username):
    try:
        sb = get_supabase()
        sb.schema("operation").table("user_managements")\
            .delete().eq("id_user", username).execute()
        sb.schema("operation").table("users")\
            .delete().eq("code_user", username).execute()
        return True
    except Exception:
        return False


def update_last_login_optimized(username, password):
    try:
        sb = get_supabase()
        from datetime import datetime, timezone
        sb.schema("operation").table("user_managements")\
            .update({"last_login": datetime.now(timezone.utc).isoformat()})\
            .eq("id_user", username).eq("password", password).execute()
        return True
    except Exception:
        return False


def update_password(username, old_pass, new_pass):
    if old_pass == new_pass:
        return False, "Kata sandi identik"
    try:
        sb = get_supabase()
        check = sb.schema("operation").table("user_managements")\
            .select("id_user").eq("id_user", username).eq("password", old_pass).execute()
        if not check.data:
            return False, "Kredensial salah"
        sb.schema("operation").table("user_managements")\
            .update({"password": new_pass.strip()}).eq("id_user", username).execute()
        return True, "Berhasil"
    except Exception as e:
        return False, str(e)
