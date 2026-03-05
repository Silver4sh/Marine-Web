import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import get_supabase


@st.cache_data(ttl=60)
def get_system_settings():
    sb = get_supabase()
    resp = sb.schema("operation").table("system_settings")\
        .select("key, value, description").execute()
    if not resp.data:
        return {}
    df = pd.DataFrame(resp.data)
    return pd.Series(df["value"].values, index=df["key"]).to_dict()


def update_system_setting(key, value):
    try:
        sb = get_supabase()
        sb.schema("operation").table("system_settings")\
            .update({"value": str(value), "updated_at": datetime.now(timezone.utc).isoformat()})\
            .eq("key", key).execute()
        st.cache_data.clear()
        return True
    except Exception:
        return False


@st.cache_data(ttl=60)
def get_logs():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    resp = sb.schema("audit").table("audit_logs")\
        .select("changed_by, table_name, action, old_data, new_data, changed_at")\
        .gte("changed_at", cutoff).order("changed_at", desc=True).execute()
    return pd.DataFrame(resp.data)
