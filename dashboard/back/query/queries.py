import pandas as pd
import streamlit as st
from sqlalchemy import text
from back.connection.conection import get_engine

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
    return df.astype(int).iloc[0].to_dict()

# --- Posisi kapal terakhir ---
@st.cache_data(ttl=30)
def get_vessel_position():
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
    query = """
    SELECT latitude, longitude, 0 as heading, speed, created_at
    FROM alpha.vessel_positions
    WHERE id_vessel = :vessel_id
    ORDER BY created_at DESC;
    """
    return run_query(query, params={"vessel_id": vessel_id})

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
    """
    return run_query(query, params)

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

# --- Financial Metrics ---
@st.cache_data(ttl=300)
def get_financial_metrics():
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
    
    current = df.iloc[0]
    curr_rev = float(current["total_revenue"])
    curr_orders = int(current["completed_orders"])
    
    metrics = {
        "total_revenue": curr_rev,
        "completed_orders": curr_orders,
        "delta_revenue": 0.0,
        "delta_orders": 0.0
    }
    
    if len(df) > 1:
        previous = df.iloc[1]
        
        if previous["total_revenue"] > 0:
            metrics["delta_revenue"] = ((current["total_revenue"] - previous["total_revenue"]) / previous["total_revenue"]) * 100
            
        if previous["completed_orders"] > 0:
            metrics["delta_orders"] = ((current["completed_orders"] - previous["completed_orders"]) / previous["completed_orders"]) * 100
            
    return metrics

@st.cache_data(ttl=300)
def get_revenue_analysis():
    query = """
    SELECT 
        DATE_TRUNC('month', payment_date) as month,
        SUM(total_amount) as revenue
    FROM alpha.payments
    WHERE status = 'Payed'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)

# --- Operational Metrics ---
@st.cache_data(ttl=300)
def get_order_stats():
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
    return df.astype(int).iloc[0].to_dict()

@st.cache_data(ttl=300)
def get_revenue_by_service():
    query = """
    SELECT 
        c.industry as "Service",
        SUM(p.total_amount) as "Value"
    FROM alpha.payments p
    JOIN alpha.orders o ON p.id_order = o.id
    JOIN alpha.clients c ON o.id_client = c.code_client
    WHERE p.status = 'Payed'
    GROUP BY c.industry
    ORDER BY "Value" DESC
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_fleet_daily_activity():
    query = """
    SELECT 
        v.code_vessel,
        TO_CHAR(vp.created_at, 'Dy') as day_name,
        EXTRACT(ISODOW FROM vp.created_at) as day_num,
        COUNT(DISTINCT DATE_TRUNC('hour', vp.created_at)) as active_hours
    FROM alpha.vessel_positions vp
    JOIN alpha.vessels v ON vp.id_vessel = v.code_vessel
    WHERE vp.created_at >= NOW() - INTERVAL '7 days'
      AND vp.speed > 0.5
    GROUP BY 1, 2, 3
    ORDER BY day_num
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_clients_summary():
    query = """
    SELECT 
        c.code_client,
        c.name,
        c.industry,
        c.region,
        c.status,
        COUNT(DISTINCT o.id) as total_orders,
        COALESCE(SUM(p.total_amount), 0) as ltv
    FROM alpha.clients c
    LEFT JOIN alpha.orders o ON c.code_client = o.id_client
    LEFT JOIN alpha.payments p ON o.id = p.id_order AND p.status = 'Payed'
    GROUP BY c.code_client, c.name, c.industry, c.region, c.status
    ORDER BY ltv DESC
    """
    return run_query(query)

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

# --- Innovative Analytics Queries ---

@st.cache_data(ttl=300)
def get_vessel_utilization_stats():
    """
    Calculate Vessel Utilization Score based on activity duration.
    """
    query = """
    SELECT 
        v.name as vessel_name,
        SUM(EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600) as total_hours,
        SUM(CASE WHEN LOWER(va.status) NOT IN ('idle', 'maintenance', 'docking') 
            THEN EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600 
            ELSE 0 END) as productive_hours
    FROM alpha.vessel_activities va
    JOIN alpha.vessels v ON va.id_vessel = v.code_vessel
    WHERE va.start_date >= NOW() - INTERVAL '30 days'
    GROUP BY v.name
    """
    df = run_query(query)
    if not df.empty:
        df['utilization_rate'] = (df['productive_hours'] / df['total_hours']) * 100
        df['utilization_rate'] = df['utilization_rate'].fillna(0)
    return df

@st.cache_data(ttl=300)
def get_revenue_cycle_metrics():
    """
    Analyze Order-to-Cash cycle efficiency.
    """
    query = """
    SELECT 
        DATE_TRUNC('month', o.order_date) as month,
        AVG(EXTRACT(DAY FROM (p.payment_date - o.order_date))) as avg_days_to_cash,
        SUM(p.total_amount) as realized_revenue,
        SUM(CASE WHEN p.status = 'Payed' THEN 1 ELSE 0 END) as paid_count,
        COUNT(o.id) as total_orders
    FROM alpha.orders o
    JOIN alpha.payments p ON o.id = p.id_order
    WHERE o.order_date >= NOW() - INTERVAL '6 months'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_environmental_anomalies():
    """
    Detect anomalies in sensor data using Z-Score (Statistical Deviation).
    Returns rows where values deviate > 2 SD from the monthly average.
    """
    query = """
    WITH stats AS (
        SELECT 
            id_buoy,
            AVG(salinitas) as avg_sal,
            STDDEV(salinitas) as std_sal,
            AVG(turbidity) as avg_tur,
            STDDEV(turbidity) as std_tur
        FROM alpha.buoy_sensor_histories
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY id_buoy
    )
    SELECT 
        h.id_buoy,
        h.created_at,
        h.salinitas,
        h.turbidity,
        (h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0) as sal_z_score,
        (h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0) as tur_z_score
    FROM alpha.buoy_sensor_histories h
    JOIN stats s ON h.id_buoy = s.id_buoy
    WHERE h.created_at >= NOW() - INTERVAL '7 days'
      AND (
          ABS((h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0)) > 2
          OR 
          ABS((h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0)) > 2
      )
    ORDER BY h.created_at DESC
    LIMIT 50
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_logistics_performance():
    """
    Analyze delivery performance by destination.
    """
    query = """
    SELECT 
        destination,
        COUNT(*) as total_trips,
        AVG(EXTRACT(EPOCH FROM (actual_delivery_date - scheduled_delivery_date))/3600) as avg_delay_hours,
        SUM(CASE WHEN actual_delivery_date > scheduled_delivery_date THEN 1 ELSE 0 END) as late_trips
    FROM alpha.orders
    WHERE actual_delivery_date IS NOT NULL 
      AND scheduled_delivery_date IS NOT NULL
    GROUP BY destination
    ORDER BY avg_delay_hours DESC
    """
    return run_query(query)
