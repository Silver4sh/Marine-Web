"""db/repos/environ.py — moved from db/repositories/environ_repo.py"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from db.connection import sb_table

_EMPTY    = pd.DataFrame()
_MAX_ROWS = 5_000


@st.cache_data(ttl=60)
def get_data_water() -> pd.DataFrame:
    bsh = pd.DataFrame(sb_table("ocean", "buoy_sensor_histories")
        .select("id_buoy, salinitas, turbidity, current, oxygen, tide, density, created_at")
        .order("created_at", desc=True).limit(_MAX_ROWS).execute().data)
    if bsh.empty:
        return _EMPTY
    buoys = pd.DataFrame(sb_table("ocean", "buoys").select("code_buoy, id_site").execute().data)
    sites = pd.DataFrame(sb_table("operation", "sites").select("code_site, latitude, longitude").execute().data)
    df = bsh.merge(buoys, left_on="id_buoy", right_on="code_buoy", how="left")\
            .merge(sites, left_on="id_site",  right_on="code_site",  how="left")\
            .rename(columns={"created_at": "latest_timestamp"})
    return df[["id_buoy", "latitude", "longitude", "salinitas", "turbidity",
               "current", "oxygen", "tide", "density", "latest_timestamp"]]


@st.cache_data(ttl=60)
def get_environmental_anomalies() -> pd.DataFrame:
    cutoff_30 = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    cutoff_7  = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    hist = pd.DataFrame(sb_table("ocean", "buoy_sensor_histories")
        .select("id_buoy, salinitas, turbidity, created_at")
        .gte("created_at", cutoff_30).limit(_MAX_ROWS).execute().data)
    if hist.empty:
        return _EMPTY
    stats = hist.groupby("id_buoy").agg(
        avg_sal=("salinitas", "mean"), std_sal=("salinitas", "std"),
        avg_tur=("turbidity", "mean"), std_tur=("turbidity", "std"),
    ).reset_index()
    recent = hist[hist["created_at"] >= cutoff_7].merge(stats, on="id_buoy", how="left")
    recent["sal_z_score"] = (recent["salinitas"] - recent["avg_sal"]) / recent["std_sal"].replace(0, np.nan)
    recent["tur_z_score"] = (recent["turbidity"] - recent["avg_tur"]) / recent["std_tur"].replace(0, np.nan)
    return recent[
        (recent["sal_z_score"].abs() > 2) | (recent["tur_z_score"].abs() > 2)
    ][["id_buoy", "created_at", "salinitas", "turbidity",
       "sal_z_score", "tur_z_score"]].sort_values("created_at", ascending=False)


@st.cache_data(ttl=57)
def get_buoy_fleet() -> pd.DataFrame:
    buoys = pd.DataFrame(sb_table("ocean", "buoys").select("code_buoy, status, id_site").execute().data)
    if buoys.empty:
        return _EMPTY
    sites      = pd.DataFrame(sb_table("operation", "sites").select("code_site, location").execute().data)
    last_reads = pd.DataFrame(sb_table("ocean", "buoy_sensor_histories")
        .select("id_buoy, created_at").order("created_at", desc=True).limit(500).execute().data)
    last_per_buoy = last_reads.groupby("id_buoy")["created_at"].first().reset_index()
    last_per_buoy.columns = ["code_buoy", "last_update"]
    df = buoys.merge(sites, left_on="id_site", right_on="code_site", how="left")\
              .merge(last_per_buoy, on="code_buoy", how="left")
    df["battery"] = "85%"
    return df[["code_buoy", "status", "location", "battery", "last_update"]].sort_values("code_buoy")


@st.cache_data(ttl=60)
def get_buoy_history(buoy_id: str) -> pd.DataFrame:
    resp = sb_table("ocean", "buoy_sensor_histories")\
        .select("id_buoy, created_at, salinitas, turbidity, oxygen, density, current, tide")\
        .eq("id_buoy", buoy_id).order("created_at").limit(1000).execute()
    return pd.DataFrame(resp.data)


@st.cache_data(ttl=3600)
def get_environmental_compliance_dashboard() -> pd.DataFrame:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    resp = sb_table("ocean", "buoy_sensor_histories")\
        .select("turbidity, created_at").gte("created_at", cutoff)\
        .limit(_MAX_ROWS).execute()
    if not resp.data:
        return _EMPTY
    df = pd.DataFrame(resp.data)
    df["created_at"]   = pd.to_datetime(df["created_at"], utc=True)
    df["monitor_date"] = df["created_at"].dt.floor("D")
    result = df.groupby("monitor_date").agg(
        total_readings=("turbidity", "count"),
        high_turbidity_events=("turbidity", lambda x: (x > 50).sum()),
        avg_turbidity=("turbidity", "mean"),
    ).reset_index()
    result["compliance_score_pct"] = (
        100.0 - result["high_turbidity_events"] / result["total_readings"].replace(0, np.nan) * 100.0
    ).fillna(100.0)
    return result.sort_values("monitor_date", ascending=False)
