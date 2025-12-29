import pandas as pd
import streamlit as st
from sqlalchemy import text
from back.conection.conection import get_engine

# -- Running Query
def run_query(query, params=None):
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()

    try:
        # Use a context manager to ensure the connection is closed/returned to pool
        with engine.connect() as conn:
            # If params is provided, use safely
            if params:
                df = pd.read_sql(text(query), conn, params=params)
            else:
                df = pd.read_sql(text(query), conn)
            return df
    except Exception as e:
        # Log error in console but don't break the UI
        print(f"Query error: {e}") 
        return pd.DataFrame()

# #################################

# --- Fleet Metrics ---
@st.cache_data(ttl=60)
def get_fleet_status():
    query = """
    SELECT 
        COUNT(*) as total_vessels,
        SUM(CASE WHEN LOWER(status) = 'operating' THEN 1 ELSE 0 END) as operating,
        SUM(CASE WHEN LOWER(status) IN ('maintenance', 'mtc') THEN 1 ELSE 0 END) as maintenance,
        SUM(CASE WHEN LOWER(status) = 'idle' THEN 1 ELSE 0 END) as idle
    FROM alpha.vessels
    """
    df = run_query(query)
    if df.empty:
        return {"total_vessels": 0, "operating": 0, "maintenance": 0, "idle": 0}
    return df.iloc[0].to_dict()

# --- Posisi kapal terakhir ---
@st.cache_data(ttl=30)
def get_vessel_position():
    """
    Get latest vessel positions.
    Using DISTINCT ON to get only the latest position per vessel.
    """
    query = """
    SELECT DISTINCT ON (vp.id_vessel)
           vp.id_vessel as "code_vessel",
           'Vessel Name' as "Vessel Name",
           v.status as "Status",
           vp.latitude,
           vp.longitude,
           vp.speed,
           0 as heading,
           vp.created_at as "Last Update"
    FROM alpha.vessel_positions vp
    JOIN alpha.vessels v ON vp.id_vessel = v.code_vessel
    ORDER BY vp.id_vessel, vp.created_at DESC;
    """
    return run_query(query)

@st.cache_data(ttl=30)
def get_path_vessel(vessel_id):
    """
    Get historical path for a specific vessel.
    """
    query = """
    SELECT latitude, longitude, heading, speed, created_at
    FROM alpha.vessel_positions
    WHERE id_vessel = :vessel_id
    ORDER BY created_at DESC
    LIMIT 200;
    """
    return run_query(query, params={"vessel_id": vessel_id})

# --- Financial Metrics ---
@st.cache_data(ttl=300)
def get_financial_metrics():
    """
    Get key financial metrics with month-over-month growth.
    """
    query = """
    SELECT 
        COALESCE(SUM(total_amount), 0) as total_revenue,
        COUNT(DISTINCT id_order) as completed_orders,
        DATE_TRUNC('month', payment_date)::DATE AS payment_day
    FROM alpha.payments
    WHERE status = 'Payed'
    GROUP BY DATE_TRUNC('month', payment_date)
    ORDER BY payment_day DESC;
    """
    df = run_query(query)
    
    if df.empty:
        return {
            "total_revenue": 0, 
            "completed_orders": 0, 
            "delta_revenue": 0.0,
            "delta_orders": 0.0
        }
    
    # Get current (latest) month data
    current = df.iloc[0]
    
    # Initialize metrics with current month values
    metrics = {
        "total_revenue": current["total_revenue"],
        "completed_orders": current["completed_orders"],
        "delta_revenue": 0.0,
        "delta_orders": 0.0
    }
    
    # Calculate deltas if we have previous month data
    if len(df) > 1:
        previous = df.iloc[1]
        
        # Revenue Delta
        if previous["total_revenue"] > 0:
            metrics["delta_revenue"] = ((current["total_revenue"] - previous["total_revenue"]) / previous["total_revenue"]) * 100
            
        # Orders Delta
        if previous["completed_orders"] > 0:
            metrics["delta_orders"] = ((current["completed_orders"] - previous["completed_orders"]) / previous["completed_orders"]) * 100
            
    return metrics

@st.cache_data(ttl=300)
def get_revenue_analysis():
    """
    Monthly revenue analysis.
    """
    query = """
    SELECT 
        DATE_TRUNC('month', payment_date) as month,
        SUM(total_amount) as revenue
    FROM alpha.payments
    WHERE status = 'Payed'
    GROUP BY 1
    ORDER BY 1 DESC
    LIMIT 12
    """
    return run_query(query)

# --- Operational Metrics ---
@st.cache_data(ttl=300)
def get_order_stats():
    """
    Order statistics by status.
    """
    query = """
    SELECT 
        COUNT(*) as total_orders,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN status = 'In Completed' THEN 1 ELSE 0 END) as in_completed,
        SUM(CASE WHEN status = 'On Progress' THEN 1 ELSE 0 END) as on_progress,
        SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed
    FROM alpha.orders
    """
    df = run_query(query)
    if df.empty:
        return {"total_orders": 0, "completed": 0, "in_completed": 0, "on_progress": 0, "failed": 0}
    return df.iloc[0].to_dict()

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
    FROM alpha.buoy_sensor_histories bsh
    JOIN alpha.buoys b ON b.code_buoy = bsh.id_buoy
    JOIN alpha.sites s ON s.code_site = b.id_site
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
    FROM alpha.buoy_sensor_histories bsh
    {where_clause}
    ORDER BY created_at ASC
    LIMIT 1000
    """
    return run_query(query, params)

@st.cache_data(ttl=300)
def get_clients_summary():
    """Client summary with order counts"""
    query = """
    SELECT 
        c.code_client,
        c.name,
        c.industry,
        c.region,
        c.status,
        COUNT(o.id) as total_orders
    FROM alpha.clients c
    LEFT JOIN alpha.orders o ON c.code_client = o.id_client
    GROUP BY c.code_client, c.name, c.industry, c.region, c.status
    ORDER BY total_orders DESC
    """
    return run_query(query)

@st.cache_data(ttl=3600)
def get_buoy_list():
    """Get unique list of buoys"""
    query = "SELECT DISTINCT id_buoy FROM alpha.buoy_sensor_histories ORDER BY id_buoy"
    return run_query(query)

@st.cache_data(ttl=600)
def get_buoy_date_range(buoy_id):
    """Get efficient min/max dates for slider"""
    query = """
    SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
    FROM alpha.buoy_sensor_histories
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
    FROM alpha.buoy_sensor_histories bsh
    JOIN alpha.buoys b ON bsh.id_buoy = b.code_buoy 
    JOIN alpha.sites s ON b.id_site = s.code_site 
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
    FROM alpha.buoy_sensor_histories
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
    FROM alpha.buoy_sensor_histories
    WHERE created_at >= :start_date AND created_at <= :end_date
    GROUP BY 1
    ORDER BY 1 ASC
    """
    return run_query(query, params={
        "start_date": start_date,
        "end_date": end_date
    })

@st.cache_data(ttl=60)
def get_logs():
    query = """
    SELECT 
        changed_by,
        table_name,
        "action",
        old_data,
        new_data,
        changed_at        
    FROM audit.audit_logs
    WHERE created_at <= NOW() - interval '7 days'
    ORDER BY created_at desc
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_vessel_list():
    query = """
    SELECT 
        code_vessel
    FROM alpha.vessels
    """
    return run_query(query)
