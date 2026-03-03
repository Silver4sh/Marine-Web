import streamlit as st
import pandas as pd
from db.connection import run_query, get_engine
from sqlalchemy import text

def init_settings_table():
    engine = get_engine()
    if not engine: return
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS operation.system_settings (key VARCHAR(50) PRIMARY KEY, value TEXT, description TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"))
            res = conn.execute(text("SELECT count(*) FROM operation.system_settings")).scalar()
            if res == 0:
                defaults = [("app_name", "MarineOS Dashboard", "Nama Aplikasi"), ("maintenance_mode", "false", "Mode Perawatan"), ("revenue_target_monthly", "5000000000", "Target Pendapatan"), ("churn_risk_threshold", "3", "Ambang Batas Churn"), ("theme_color", "#0ea5e9", "Warna Tema")]
                for k, v, d in defaults: conn.execute(text("INSERT INTO operation.system_settings (key, value, description) VALUES (:k, :v, :d)"), {"k": k, "v": v, "d": d})
    except Exception as e: print(f"Error initializing settings: {e}")

@st.cache_data(ttl=60)
def get_system_settings():
    init_settings_table()
    query = "SELECT key, value, description FROM operation.system_settings"
    df = run_query(query)
    if df.empty: return {}
    return pd.Series(df.value.values, index=df.key).to_dict()

def update_system_setting(key, value):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.system_settings SET value = :value, updated_at = NOW() WHERE key = :key"), {"value": str(value), "key": key})
            st.cache_data.clear()
            return True
    except: return False

@st.cache_data(ttl=60)
def get_logs():
    query = "SELECT changed_by, table_name, \"action\", old_data, new_data, changed_at FROM audit.audit_logs WHERE changed_at >= NOW() - interval '7 days' ORDER BY changed_at desc"
    return run_query(query)
