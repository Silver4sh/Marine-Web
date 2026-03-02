import streamlit as st
import pandas as pd
from db.connection import run_query

@st.cache_data(ttl=60)
def get_fleet_status():
    """Returns dict with total, operating, maintenance, idle vessel counts."""
    query = """
    SELECT
        COUNT(*) AS total_vessels,
        SUM(CASE WHEN LOWER(va.status) IN ('operating', 'running', 'on_duty') THEN 1 ELSE 0 END) AS operating,
        SUM(CASE WHEN LOWER(va.status) IN ('maintenance', 'mtc', 'repair')    THEN 1 ELSE 0 END) AS maintenance,
        SUM(CASE WHEN LOWER(va.status) IN ('idle', 'anchored', 'berthed')     THEN 1 ELSE 0 END) AS idle
    FROM operation.vessels v
    JOIN operation.vessel_activities va
        ON v.code_vessel = va.id_vessel
    WHERE va.seq_activity IN (
        SELECT MAX(vva.seq_activity)
        FROM operation.vessel_activities vva
        GROUP BY vva.id_vessel
    )
    """
    df = run_query(query)
    if df.empty:
        return {"total_vessels": 0, "operating": 0, "maintenance": 0, "idle": 0}
    row = df.iloc[0]
    return {k: int(row.get(k, 0) or 0) for k in ["total_vessels", "operating", "maintenance", "idle"]}


@st.cache_data(ttl=30)
def get_vessel_position():
    """
    Returns latest position for every vessel, including the vessel's actual name.
    Sorted newest-position first per vessel via DISTINCT ON.
    """
    query = """
    SELECT DISTINCT ON (vp.id_vessel)
        vp.id_vessel                                    AS code_vessel,
        COALESCE(v.name, vp.id_vessel)                  AS "Vessel Name",
        v.status                                        AS "Status",
        vp.latitude,
        vp.longitude,
        COALESCE(vp.speed, 0)                           AS speed,
        COALESCE(vp.heading, 0)                         AS heading,
        vp.created_at                                   AS "Last Update"
    FROM operation.vessel_positions vp
    JOIN operation.vessels v ON vp.id_vessel = v.code_vessel
    ORDER BY vp.id_vessel, vp.created_at DESC
    """
    df = run_query(query)
    if not df.empty and "Last Update" in df.columns:
        df["Last Update"] = pd.to_datetime(df["Last Update"], errors="coerce")
    return df


@st.cache_data(ttl=30)
def get_path_vessel(vessel_id: str):
    """Returns chronological position history for a single vessel."""
    query = """
    SELECT
        latitude,
        longitude,
        COALESCE(heading, 0) AS heading,
        COALESCE(speed,   0) AS speed,
        created_at
    FROM operation.vessel_positions
    WHERE id_vessel = :vessel_id
    ORDER BY created_at DESC
    LIMIT 500
    """
    df = run_query(query, params={"vessel_id": vessel_id})
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def get_vessel_list():
    query = "SELECT code_vessel, name FROM operation.vessels ORDER BY name"
    return run_query(query)


@st.cache_data(ttl=300)
def get_fleet_daily_activity():
    """Hourly active hours per vessel for the last 7 days (for heatmap)."""
    query = """
    SELECT
        v.code_vessel,
        TO_CHAR(vp.created_at, 'Dy')                          AS day_name,
        EXTRACT(ISODOW FROM vp.created_at)                    AS day_num,
        COUNT(DISTINCT DATE_TRUNC('hour', vp.created_at))     AS active_hours
    FROM operation.vessel_positions vp
    JOIN operation.vessels v ON vp.id_vessel = v.code_vessel
    WHERE vp.created_at >= NOW() - INTERVAL '7 days'
      AND vp.speed > 0.5
    GROUP BY 1, 2, 3
    ORDER BY day_num
    """
    return run_query(query)


@st.cache_data(ttl=300)
def get_vessel_utilization_stats():
    query = """
    SELECT
        v.name AS vessel_name,
        SUM(EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date)) / 3600) AS total_hours,
        SUM(CASE WHEN LOWER(va.status) NOT IN ('idle', 'maintenance', 'docking')
                 THEN EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date)) / 3600
                 ELSE 0 END) AS productive_hours
    FROM operation.vessel_activities va
    JOIN operation.vessels v ON va.id_vessel = v.code_vessel
    WHERE va.start_date >= NOW() - INTERVAL '30 days'
    GROUP BY v.name
    """
    df = run_query(query)
    if not df.empty and "total_hours" in df.columns:
        df["utilization_rate"] = (
            (df["productive_hours"] / df["total_hours"].replace(0, pd.NA)) * 100
        ).fillna(0).round(1)
    return df


@st.cache_data(ttl=300)
def get_logistics_performance():
    query = """
    SELECT
        destination,
        COUNT(*)                                                          AS total_trips,
        AVG(EXTRACT(EPOCH FROM (actual_delivery_date - scheduled_delivery_date)) / 3600)
                                                                          AS avg_delay_hours,
        SUM(CASE WHEN actual_delivery_date > scheduled_delivery_date THEN 1 ELSE 0 END)
                                                                          AS late_trips
    FROM operation.orders
    WHERE actual_delivery_date   IS NOT NULL
      AND scheduled_delivery_date IS NOT NULL
    GROUP BY destination
    ORDER BY avg_delay_hours DESC
    """
    return run_query(query)


@st.cache_data(ttl=60)
def get_operational_anomalies():
    """
    Detects two types of vessel anomalies in the last 2 hours:
      • Ghost Operation  — reported Operating but speed < 0.5 kn
      • Unauthorized Move — status idle/maintenance but speed > 2 kn
    """
    query = """
    WITH recent_pos AS (
        SELECT DISTINCT ON (id_vessel)
            id_vessel, speed, created_at, latitude, longitude
        FROM operation.vessel_positions
        WHERE created_at >= NOW() - INTERVAL '2 hours'
        ORDER BY id_vessel, created_at DESC
    )
    SELECT
        rp.id_vessel,
        COALESCE(v.name, rp.id_vessel) AS vessel_name,
        v.status                        AS reported_status,
        rp.speed,
        rp.latitude,
        rp.longitude,
        rp.created_at,
        CASE
            WHEN LOWER(v.status) IN ('operating', 'running') AND rp.speed < 0.5
                THEN 'Ghost Operation'
            WHEN LOWER(v.status) IN ('idle', 'maintenance', 'docking') AND rp.speed > 2.0
                THEN 'Pergerakan Tidak Sah'
            ELSE 'Normal'
        END AS anomaly_type
    FROM recent_pos rp
    JOIN operation.vessels v ON rp.id_vessel = v.code_vessel
    WHERE
        (LOWER(v.status) IN ('operating', 'running') AND rp.speed < 0.5)
        OR
        (LOWER(v.status) IN ('idle', 'maintenance', 'docking') AND rp.speed > 2.0)
    ORDER BY rp.created_at DESC
    LIMIT 20
    """
    return run_query(query)
