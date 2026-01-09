import pandas as pd
import streamlit as st
from back.query.queries import run_query

# --- Sensor Data ---
@st.cache_data(ttl=60)
def get_data_water():
    """Get historical sensor readings for heatmap (last 30 days) for dynamic filtering"""
    query = """
    SELECT
        bsh.id_buoy,
        s.latitude,
        s.longitude,
        bsh.salinitas as salinitas,
        bsh.turbidity as turbidity,
        bsh.current as current,
        bsh.oxygen as oxygen,
        bsh.tide as tide,
        bsh.density as density,
        bsh.created_at as latest_timestamp
    FROM operational.buoy_sensor_histories bsh
    JOIN operational.buoys b ON b.code_buoy = bsh.id_buoy
    JOIN operational.sites s ON s.code_site = b.id_site
    ORDER BY bsh.created_at DESC
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_sensor_trends(buoy_id=None):
    """Get historical sensor data for charts"""
    params = {}
    where_clause = ""
    if buoy_id:
        where_clause = "WHERE bsh.id_buoy = :buoy_id"
        params["buoy_id"] = buoy_id
        
    query = f"""
    SELECT 
        created_at,
        salinitas,
        turbidity,
        current,
        oxygen
    FROM operational.buoy_sensor_histories bsh
    {where_clause}
    ORDER BY created_at ASC
    """
    return run_query(query, params)

@st.cache_data(ttl=3600)
def get_buoy_list():
    """Get unique list of buoys"""
    query = "SELECT DISTINCT id_buoy FROM operational.buoy_sensor_histories ORDER BY id_buoy"
    return run_query(query)

@st.cache_data(ttl=600)
def get_buoy_date_range(buoy_id):
    """Get efficient min/max dates for slider"""
    query = """
    SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
    FROM operational.buoy_sensor_histories
    WHERE id_buoy = :buoy_id
    """
    return run_query(query, params={"buoy_id": buoy_id})

@st.cache_data(ttl=60)
def get_buoy_history(buoy_id, start_date, end_date):
    """
    Optimized: Fetch only requested data from DB.
    """
    query = """
    SELECT
        bsh.id_buoy,
        bsh.salinitas,
        bsh.turbidity,
        bsh.current,
        bsh.oxygen,
        bsh.tide,
        bsh.density,
        s.latitude,
        s.longitude,
        bsh.created_at
    FROM operational.buoy_sensor_histories bsh
    JOIN operational.buoys b ON bsh.id_buoy = b.code_buoy 
    JOIN operational.sites s ON b.id_site = s.code_site 
    WHERE bsh.id_buoy = :buoy_id
      AND bsh.created_at >= :start_date
      AND bsh.created_at <= :end_date
    ORDER BY bsh.created_at ASC
    """
    return run_query(query, params={
        "buoy_id": buoy_id,
        "start_date": start_date,
        "end_date": end_date
    })

@st.cache_data(ttl=600)
def get_global_date_range():
    """Get min/max dates for all buoys"""
    query = """
    SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
    FROM operational.buoy_sensor_histories
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_aggregated_buoy_history(start_date, end_date):
    """
    Get averaged sensor data across all buoys, grouped by hour.
    """
    query = """
    SELECT
        date_trunc('hour', created_at) as created_at,
        AVG(salinitas) as salinitas,
        AVG(turbidity) as turbidity,
        AVG(current) as current,
        AVG(oxygen) as oxygen,
        AVG(tide) as tide,
        AVG(density) as density
    FROM operational.buoy_sensor_histories
    WHERE created_at >= :start_date AND created_at <= :end_date
    GROUP BY 1
    ORDER BY 1 ASC
    """
    return run_query(query, params={
        "start_date": start_date,
        "end_date": end_date
    })
