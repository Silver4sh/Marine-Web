import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import sb_table

_EMPTY = pd.DataFrame()
_POS_LIMIT = 1_000  # cap position history per fetch


@st.cache_data(ttl=60)
def get_fleet_status() -> dict:
    rows = sb_table("operation", "vessel_activities")\
        .select("id_vessel, seq_activity, status").execute().data
    if not rows:
        return {"total_vessels": 0, "operating": 0, "maintenance": 0, "idle": 0}

    df = pd.DataFrame(rows).sort_values("seq_activity")\
         .groupby("id_vessel").last().reset_index()
    s = df["status"].str.lower()
    return {
        "total_vessels": len(df),
        "operating":     int(s.isin(["operating", "running", "on_duty"]).sum()),
        "maintenance":   int(s.isin(["maintenance", "mtc", "repair"]).sum()),
        "idle":          int(s.isin(["idle", "anchored", "berthed"]).sum()),
    }


@st.cache_data(ttl=30)
def get_vessel_position() -> pd.DataFrame:
    positions = pd.DataFrame(sb_table("operation", "vessel_positions")
        .select("id_vessel, latitude, longitude, speed, heading, created_at")
        .order("created_at", desc=True).limit(_POS_LIMIT).execute().data)
    if positions.empty:
        return _EMPTY

    vessels = pd.DataFrame(sb_table("operation", "vessels")
        .select("code_vessel, name, status").execute().data)

    positions["created_at"] = pd.to_datetime(positions["created_at"], utc=True)
    latest = positions.drop_duplicates("id_vessel").merge(
        vessels, left_on="id_vessel", right_on="code_vessel", how="left")\
        .drop(columns=["code_vessel"])  # drop vessels' code_vessel to avoid duplicate after rename
    latest["speed"]   = latest["speed"].fillna(0)
    latest["heading"] = latest["heading"].fillna(0)
    return latest.rename(columns={
        "id_vessel":  "code_vessel",
        "name":       "Vessel Name",
        "status":     "Status",
        "created_at": "Last Update",
    })[["code_vessel", "Vessel Name", "Status", "latitude",
        "longitude", "speed", "heading", "Last Update"]]


@st.cache_data(ttl=30)
def get_path_vessel(vessel_id: str) -> pd.DataFrame:
    rows = sb_table("operation", "vessel_positions")\
        .select("latitude, longitude, heading, speed, created_at")\
        .eq("id_vessel", vessel_id).order("created_at", desc=True).limit(500).execute().data
    df = pd.DataFrame(rows)
    if not df.empty:
        df[["heading", "speed"]] = df[["heading", "speed"]].fillna(0)
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df


@st.cache_data(ttl=3600)
def get_vessel_list() -> pd.DataFrame:
    return pd.DataFrame(sb_table("operation", "vessels")
        .select("code_vessel, name").order("name").execute().data)


@st.cache_data(ttl=300)
def get_fleet_daily_activity() -> pd.DataFrame:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    rows = sb_table("operation", "vessel_positions")\
        .select("id_vessel, speed, created_at").gte("created_at", cutoff)\
        .limit(_POS_LIMIT).execute().data
    if not rows:
        return _EMPTY

    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    active = df[df["speed"] > 0.5].copy()
    active["day_num"]  = active["created_at"].dt.isocalendar().day
    active["day_name"] = active["created_at"].dt.strftime("%a")
    active["hour"]     = active["created_at"].dt.floor("h")

    result = active.groupby(["id_vessel", "day_name", "day_num"])["hour"]\
        .nunique().reset_index()
    result.columns = ["code_vessel", "day_name", "day_num", "active_hours"]
    return result.sort_values("day_num")


@st.cache_data(ttl=300)
def get_vessel_utilization_stats() -> pd.DataFrame:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    activities = pd.DataFrame(sb_table("operation", "vessel_activities")
        .select("id_vessel, status, start_date, end_date")
        .gte("start_date", cutoff).execute().data)
    if activities.empty:
        return _EMPTY

    vessels = pd.DataFrame(sb_table("operation", "vessels")
        .select("code_vessel, name").execute().data)

    now = datetime.now(timezone.utc)
    activities["start_date"] = pd.to_datetime(activities["start_date"], utc=True)
    activities["end_date"]   = pd.to_datetime(activities["end_date"],   utc=True).fillna(now)
    activities["dur_h"] = (activities["end_date"] - activities["start_date"]).dt.total_seconds() / 3600
    idle_set = {"idle", "maintenance", "docking"}
    activities["prod_h"] = activities.apply(
        lambda r: 0.0 if r["status"].lower() in idle_set else r["dur_h"], axis=1)

    df = activities.groupby("id_vessel").agg(
        total_hours=("dur_h", "sum"), productive_hours=("prod_h", "sum")
    ).reset_index().merge(vessels, left_on="id_vessel", right_on="code_vessel", how="left")
    df["utilization_rate"] = (
        df["productive_hours"] / df["total_hours"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)
    return df.rename(columns={"name": "vessel_name"})\
             [["vessel_name", "total_hours", "productive_hours", "utilization_rate"]]


@st.cache_data(ttl=300)
def get_logistics_performance() -> pd.DataFrame:
    rows = sb_table("operation", "orders")\
        .select("destination, actual_delivery_date, scheduled_delivery_date")\
        .not_.is_("actual_delivery_date", "null")\
        .not_.is_("scheduled_delivery_date", "null").execute().data
    if not rows:
        return _EMPTY

    df = pd.DataFrame(rows)
    df["actual_delivery_date"]    = pd.to_datetime(df["actual_delivery_date"],    utc=True)
    df["scheduled_delivery_date"] = pd.to_datetime(df["scheduled_delivery_date"], utc=True)
    df["delay_hours"] = (df["actual_delivery_date"] - df["scheduled_delivery_date"]).dt.total_seconds() / 3600
    df["late"] = df["delay_hours"] > 0

    return df.groupby("destination").agg(
        total_trips=("destination", "count"),
        avg_delay_hours=("delay_hours", "mean"),
        late_trips=("late", "sum"),
    ).reset_index().sort_values("avg_delay_hours", ascending=False)


@st.cache_data(ttl=60)
def get_operational_anomalies() -> pd.DataFrame:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    positions = pd.DataFrame(sb_table("operation", "vessel_positions")
        .select("id_vessel, speed, latitude, longitude, created_at")
        .gte("created_at", cutoff).order("created_at", desc=True).limit(200).execute().data)
    if positions.empty:
        return _EMPTY

    vessels = pd.DataFrame(sb_table("operation", "vessels")
        .select("code_vessel, name, status").execute().data)

    df = positions.drop_duplicates("id_vessel").merge(
        vessels, left_on="id_vessel", right_on="code_vessel", how="inner")
    s = df["status"].str.lower()
    mask = (
        (s.isin(["operating", "running"]) & (df["speed"] < 0.5)) |
        (s.isin(["idle", "maintenance", "docking"]) & (df["speed"] > 2.0))
    )
    df = df[mask].copy()
    df["anomaly_type"] = df.apply(
        lambda r: "Ghost Operation"
        if r["status"].lower() in {"operating", "running"} and r["speed"] < 0.5
        else "Pergerakan Tidak Sah", axis=1)
    return df.rename(columns={"name": "vessel_name", "status": "reported_status"})\
             [["id_vessel", "vessel_name", "reported_status", "speed",
                "latitude", "longitude", "created_at", "anomaly_type"]].head(20)
