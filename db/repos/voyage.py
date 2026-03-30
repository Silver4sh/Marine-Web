"""db/repos/voyage.py — Voyage data repository for MarineOS"""
from __future__ import annotations
import logging
import streamlit as st
import pandas as pd
from db.connection import sb_table

logger = logging.getLogger(__name__)

_VOYAGE_STATUS = ["Planned", "Underway", "Arrived", "Completed", "Cancelled"]


@st.cache_data(ttl=60)
def get_all_voyages() -> pd.DataFrame:
    """Fetch all voyages from the database."""
    try:
        res = sb_table("operation", "voyages").select("*").order("departure_date", desc=True).execute()
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        logger.error("get_all_voyages error: %s", e)
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_active_voyages() -> pd.DataFrame:
    """Fetch only active (Planned + Underway) voyages."""
    try:
        res = (
            sb_table("operation", "voyages")
            .select("*")
            .in_("status", ["Planned", "Underway"])
            .order("departure_date")
            .execute()
        )
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        logger.error("get_active_voyages error: %s", e)
        return pd.DataFrame()


def create_voyage(data: dict) -> tuple[bool, str]:
    """Insert a new voyage record."""
    try:
        sb_table("operation", "voyages").insert(data).execute()
        get_all_voyages.clear()
        get_active_voyages.clear()
        return True, "Voyage berhasil ditambahkan."
    except Exception as e:
        return False, f"Gagal menambahkan voyage: {e}"


def update_voyage_status(voyage_id: str | int, new_status: str) -> tuple[bool, str]:
    """Update the status of an existing voyage."""
    try:
        sb_table("operation", "voyages").update({"status": new_status}).eq("id", voyage_id).execute()
        get_all_voyages.clear()
        get_active_voyages.clear()
        return True, f"Status berhasil diperbarui ke '{new_status}'."
    except Exception as e:
        return False, f"Gagal memperbarui status: {e}"


def delete_voyage(voyage_id: str | int) -> tuple[bool, str]:
    try:
        sb_table("operation", "voyages").delete().eq("id", voyage_id).execute()
        get_all_voyages.clear()
        get_active_voyages.clear()
        return True, "Voyage berhasil dihapus."
    except Exception as e:
        return False, f"Gagal menghapus voyage: {e}"
