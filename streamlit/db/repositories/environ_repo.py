import streamlit as st
import pandas as pd
from db.connection import run_query

@st.cache_data(ttl=60)
def get_data_water():
    query = """SELECT bsh.id_buoy, s.latitude, s.longitude,
        bsh.salinitas, bsh.turbidity, bsh.current,
        bsh.oxygen, bsh.tide, bsh.density, bsh.created_at as latest_timestamp
        FROM buoy.buoy_sensor_histories bsh
        JOIN buoy.buoys b ON b.code_buoy = bsh.id_buoy
        JOIN operation.sites s ON s.code_site = b.id_site
        ORDER BY bsh.created_at DESC"""
    return run_query(query)

@st.cache_data(ttl=60)
def get_environmental_anomalies():
    query = """WITH stats AS (
        SELECT id_buoy,
            AVG(salinitas) as avg_sal, STDDEV(salinitas) as std_sal,
            AVG(turbidity) as avg_tur, STDDEV(turbidity) as std_tur
        FROM buoy.buoy_sensor_histories
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY id_buoy
    )
    SELECT h.id_buoy, h.created_at, h.salinitas, h.turbidity,
        (h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0) as sal_z_score,
        (h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0) as tur_z_score
    FROM buoy.buoy_sensor_histories h
    JOIN stats s ON h.id_buoy = s.id_buoy
    WHERE h.created_at >= NOW() - INTERVAL '7 days'
      AND (ABS((h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0)) > 2
        OR ABS((h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0)) > 2)
    ORDER BY h.created_at DESC"""
    return run_query(query)

@st.cache_data(ttl=57)
def get_buoy_fleet():
    q1 = """
        SELECT
            b.code_buoy,
            b.status,
            s.location,
            '85%' as battery,
            MAX(bsh.created_at) as last_update
        FROM buoy.buoys b
        LEFT JOIN buoy.buoy_sensor_histories bsh ON b.code_buoy = bsh.id_buoy
        LEFT JOIN operation.sites s ON b.id_site = s.code_site
        GROUP BY b.code_buoy, b.status, s.location
    """
    df = run_query(q1)
    if not df.empty:
        return df.sort_values('code_buoy')
    return pd.DataFrame()

@st.cache_data(ttl=60)
def get_buoy_history(buoy_id):
    query = """SELECT id_buoy, created_at, salinitas, turbidity,
        oxygen, density, current, tide
        FROM buoy.buoy_sensor_histories
        WHERE id_buoy = :buoy_id ORDER BY created_at ASC"""
    df = run_query(query, params={"buoy_id": buoy_id})
    return df

@st.cache_data(ttl=3600)
def get_environmental_compliance_dashboard():
    """
    Aggregates environmental risk factors.
    Returns daily stats on high turbidity events reported by Buoys.
    """
    query = """
    SELECT 
        DATE_TRUNC('day', created_at) as monitor_date,
        COUNT(*) as total_readings,
        SUM(CASE WHEN turbidity > 50 THEN 1 ELSE 0 END) as high_turbidity_events,
        AVG(turbidity) as avg_turbidity
    FROM operation.buoy_sensor_histories
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)
