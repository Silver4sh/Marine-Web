import streamlit as st
from sqlalchemy import text
from back.conection.conection import get_engine, get_connection
from back.query.queries import run_query
import pandas as pd

# --- INIT / MIGRATION ---
def init_settings_table():
    """Ensure the system_settings table exists."""
    engine = get_engine()
    if not engine: return
    
    try:
        with engine.begin() as conn:
            # Create table if not exists
            # Using a simple Key-Value pair structure
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alpha.system_settings (
                    key VARCHAR(50) PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Seed default values if empty
            res = conn.execute(text("SELECT count(*) FROM alpha.system_settings")).scalar()
            if res == 0:
                defaults = [
                    ("app_name", "MarineOS Dashboard", "Application Name displayed in header"),
                    ("maintenance_mode", "false", "Enable maintenance mode overlay"),
                    ("revenue_target_monthly", "5000000000", "Monthly Revenue Target (IDR)"),
                    ("churn_risk_threshold", "3", "Number of high-risk clients to trigger alert"),
                    ("theme_color", "#0ea5e9", "Primary accent color hex code")
                ]
                for k, v, d in defaults:
                    conn.execute(
                        text("INSERT INTO alpha.system_settings (key, value, description) VALUES (:k, :v, :d)"),
                        {"k": k, "v": v, "d": d}
                    )
    except Exception as e:
        print(f"Error initializing settings: {e}")

# --- READ ---
@st.cache_data(ttl=60)
def get_system_settings():
    """Fetch all settings as a dictionary."""
    init_settings_table() # Ensure table exists first
    query = "SELECT key, value, description FROM alpha.system_settings"
    df = run_query(query)
    if df.empty: return {}
    return pd.Series(df.value.values, index=df.key).to_dict()

# --- UPDATE ---
def update_system_setting(key, value):
    """Update a specific setting."""
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            query = text("UPDATE alpha.system_settings SET value = :value, updated_at = NOW() WHERE key = :key")
            conn.execute(query, {"value": str(value), "key": key})
            st.cache_data.clear() # Clear cache globally if possible, or at least for this func
            return True
    except Exception as e:
        st.error(f"Failed to update setting: {e}")
        return False
