"""db/repos/settings.py — moved from db/repositories/settings_repo.py"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import sb_table


@st.cache_data(ttl=60)
def get_system_settings() -> dict:
    try:
        rows = sb_table("operation", "system_settings")\
            .select("key, value").execute().data
        if not rows:
            return {}
        return {r["key"]: r["value"] for r in rows}
    except Exception:
        return {}


def update_system_setting(key: str, value) -> bool:
    try:
        sb_table("operation", "system_settings")\
            .update({"value": str(value),
                     "updated_at": datetime.now(timezone.utc).isoformat()})\
            .eq("key", key).execute()
        st.cache_data.clear()
        return True
    except Exception:
        return False


@st.cache_data(ttl=60)
def get_logs() -> pd.DataFrame:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    rows = sb_table("audit", "audit_logs")\
        .select("changed_by, table_name, action, old_data, new_data, changed_at")\
        .gte("changed_at", cutoff).order("changed_at", desc=True).execute().data
    return pd.DataFrame(rows)
