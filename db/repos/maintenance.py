"""db/repos/maintenance.py — Maintenance Tracker repository for MarineOS"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from db.connection import sb_table


@st.cache_data(ttl=120)
def get_all_maintenance() -> pd.DataFrame:
    try:
        res = sb_table("operation", "vessel_maintenance").select("*").order("scheduled_date").execute()
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        print(f"[maintenance] get_all_maintenance error: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=120)
def get_upcoming_maintenance(days_ahead: int = 30) -> pd.DataFrame:
    """Fetch maintenance scheduled within the next N days."""
    try:
        import datetime
        today   = datetime.date.today()
        cutoff  = today + datetime.timedelta(days=days_ahead)
        res = (
            sb_table("operation", "vessel_maintenance")
            .select("*")
            .gte("scheduled_date", str(today))
            .lte("scheduled_date", str(cutoff))
            .order("scheduled_date")
            .execute()
        )
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        print(f"[maintenance] get_upcoming_maintenance error: {e}")
        return pd.DataFrame()


def create_maintenance(data: dict) -> tuple[bool, str]:
    try:
        sb_table("operation", "vessel_maintenance").insert(data).execute()
        get_all_maintenance.clear()
        get_upcoming_maintenance.clear()
        return True, "Jadwal maintenance berhasil ditambahkan."
    except Exception as e:
        return False, f"Gagal menambahkan maintenance: {e}"


def update_maintenance_status(record_id: str | int, new_status: str) -> tuple[bool, str]:
    try:
        sb_table("operation", "vessel_maintenance").update({"status": new_status}).eq("id", record_id).execute()
        get_all_maintenance.clear()
        get_upcoming_maintenance.clear()
        return True, f"Status diperbarui ke '{new_status}'."
    except Exception as e:
        return False, f"Gagal memperbarui: {e}"
