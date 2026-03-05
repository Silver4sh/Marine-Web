import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import get_supabase


@st.cache_data(ttl=60)
def get_fleet_status():
    sb = get_supabase()
    activities = pd.DataFrame(sb.schema("operation").table("vessel_activities")
        .select("id_vessel, seq_activity, status").execute().data)
    if activities.empty:
        return {"total_vessels": 0, "operating": 0, "maintenance": 0, "idle": 0}

    # Latest activity per vessel
    latest = activities.sort_values("seq_activity").groupby("id_vessel").last().reset_index()
    s = latest["status"].str.lower()
    return {
        "total_vessels": len(latest),
        "operating":     int(s.isin(["operating", "running", "on_duty"]).sum()),
        "maintenance":   int(s.isin(["maintenance", "mtc", "repair"]).sum()),
        "idle":          int(s.isin(["idle", "anchored", "berthed"]).sum()),
    }


@st.cache_data(ttl=30)
def get_vessel_position():
    sb = get_supabase()
    positions = pd.DataFrame(sb.schema("operation").table("vessel_positions")
        .select("id_vessel, latitude, longitude, speed, heading, created_at")
        .order("created_at", desc=True).execute().data)
    vessels = pd.DataFrame(sb.schema("operation").table("vessels")
        .select("code_vessel, name, status").execute().data)

    if positions.empty:
        return pd.DataFrame()

    # Keep latest position per vessel
    positions["created_at"] = pd.to_datetime(positions["created_at"], utc=True)
    latest = positions.sort_values("created_at", ascending=False)\
        .drop_duplicates(subset="id_vessel")

    df = latest.merge(vessels, left_on="id_vessel", right_on="code_vessel", how="left")
    df["speed"]   = df["speed"].fillna(0)
    df["heading"] = df["heading"].fillna(0)
    df = df.rename(columns={
        "id_vessel":  "code_vessel",
        "name":       "Vessel Name",
        "status":     "Status",
        "created_at": "Last Update",
    })
    return df[["code_vessel", "Vessel Name", "Status", "latitude", "longitude",
               "speed", "heading", "Last Update"]]


@st.cache_data(ttl=30)
def get_path_vessel(vessel_id: str):
    sb = get_supabase()
    resp = sb.schema("operation").table("vessel_positions")\
        .select("latitude, longitude, heading, speed, created_at")\
        .eq("id_vessel", vessel_id).order("created_at", desc=True).limit(500).execute()
    df = pd.DataFrame(resp.data)
    if not df.empty:
        df["heading"] = df["heading"].fillna(0)
        df["speed"]   = df["speed"].fillna(0)
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df


@st.cache_data(ttl=3600)
def get_vessel_list():
    sb = get_supabase()
    resp = sb.schema("operation").table("vessels")\
        .select("code_vessel, name").order("name").execute()
    return pd.DataFrame(resp.data)


@st.cache_data(ttl=300)
def get_fleet_daily_activity():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    positions = pd.DataFrame(sb.schema("operation").table("vessel_positions")
        .select("id_vessel, speed, created_at")
        .gte("created_at", cutoff).execute().data)
    vessels = pd.DataFrame(sb.schema("operation").table("vessels")
        .select("code_vessel").execute().data)

    if positions.empty:
        return pd.DataFrame()

    positions["created_at"] = pd.to_datetime(positions["created_at"], utc=True)
    active = positions[positions["speed"] > 0.5].copy()
    active["day_num"]  = active["created_at"].dt.isocalendar().day
    active["day_name"] = active["created_at"].dt.strftime("%a")
    active["hour"]     = active["created_at"].dt.floor("h")

    result = active.groupby(["id_vessel", "day_name", "day_num"])["hour"]\
        .nunique().reset_index()
    result.columns = ["code_vessel", "day_name", "day_num", "active_hours"]
    return result.sort_values("day_num")


@st.cache_data(ttl=300)
def get_vessel_utilization_stats():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    activities = pd.DataFrame(sb.schema("operation").table("vessel_activities")
        .select("id_vessel, status, start_date, end_date")
        .gte("start_date", cutoff).execute().data)
    vessels = pd.DataFrame(sb.schema("operation").table("vessels")
        .select("code_vessel, name").execute().data)

    if activities.empty:
        return pd.DataFrame()

    now = datetime.now(timezone.utc)
    activities["start_date"] = pd.to_datetime(activities["start_date"], utc=True)
    activities["end_date"]   = pd.to_datetime(activities["end_date"],   utc=True).fillna(now)
    activities["duration_h"] = (activities["end_date"] - activities["start_date"]).dt.total_seconds() / 3600
    idle_statuses = ["idle", "maintenance", "docking"]
    activities["productive_h"] = activities.apply(
        lambda r: 0 if r["status"].lower() in idle_statuses else r["duration_h"], axis=1)

    df = activities.groupby("id_vessel").agg(
        total_hours=("duration_h", "sum"),
        productive_hours=("productive_h", "sum")
    ).reset_index().merge(vessels, left_on="id_vessel", right_on="code_vessel", how="left")

    df["utilization_rate"] = (
        df["productive_hours"] / df["total_hours"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)
    df = df.rename(columns={"name": "vessel_name"})
    return df[["vessel_name", "total_hours", "productive_hours", "utilization_rate"]]


@st.cache_data(ttl=300)
def get_logistics_performance():
    sb = get_supabase()
    resp = sb.schema("operation").table("orders")\
        .select("destination, actual_delivery_date, scheduled_delivery_date")\
        .not_.is_("actual_delivery_date", "null")\
        .not_.is_("scheduled_delivery_date", "null").execute()
    if not resp.data:
        return pd.DataFrame()

    df = pd.DataFrame(resp.data)
    df["actual_delivery_date"]    = pd.to_datetime(df["actual_delivery_date"],    utc=True)
    df["scheduled_delivery_date"] = pd.to_datetime(df["scheduled_delivery_date"], utc=True)
    df["delay_hours"] = (df["actual_delivery_date"] - df["scheduled_delivery_date"]).dt.total_seconds() / 3600
    df["late"] = df["delay_hours"] > 0

    result = df.groupby("destination").agg(
        total_trips=("destination", "count"),
        avg_delay_hours=("delay_hours", "mean"),
        late_trips=("late", "sum")
    ).reset_index().sort_values("avg_delay_hours", ascending=False)
    return result


@st.cache_data(ttl=60)
def get_operational_anomalies():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    positions = pd.DataFrame(sb.schema("operation").table("vessel_positions")
        .select("id_vessel, speed, latitude, longitude, created_at")
        .gte("created_at", cutoff).order("created_at", desc=True).execute().data)
    vessels = pd.DataFrame(sb.schema("operation").table("vessels")
        .select("code_vessel, name, status").execute().data)

    if positions.empty:
        return pd.DataFrame()

    # Latest per vessel
    latest = positions.drop_duplicates(subset="id_vessel")
    df = latest.merge(vessels, left_on="id_vessel", right_on="code_vessel", how="inner")
    s = df["status"].str.lower()

    ghost = (s.isin(["operating", "running"])) & (df["speed"] < 0.5)
    unauth = (s.isin(["idle", "maintenance", "docking"])) & (df["speed"] > 2.0)
    df = df[ghost | unauth].copy()

    df["anomaly_type"] = df.apply(
        lambda r: "Ghost Operation" if r["status"].lower() in ["operating", "running"] and r["speed"] < 0.5
                  else "Pergerakan Tidak Sah", axis=1)
    df = df.rename(columns={"name": "vessel_name", "status": "reported_status"})
    return df[["id_vessel", "vessel_name", "reported_status", "speed",
               "latitude", "longitude", "created_at", "anomaly_type"]].head(20)
