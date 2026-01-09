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
    SELECT latitude, longitude, 0 as heading, speed, created_at
    FROM alpha.vessel_positions
    WHERE id_vessel = :vessel_id
    ORDER BY created_at DESC;
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
    
    # Get current (latest) month data (explicit cast)
    current = df.iloc[0]
    curr_rev = float(current["total_revenue"])
    curr_orders = int(current["completed_orders"])
    
    # Initialize metrics with current month values
    metrics = {
        "total_revenue": curr_rev,
        "completed_orders": curr_orders,
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
    return df.astype(int).iloc[0].to_dict()

@st.cache_data(ttl=300)
def get_revenue_by_service():
    """
    Get revenue breakdown by Client Industry (as proxy for Service).
    """
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
    """
    Calculate fleet activity hours per day for the last 7 days.
    (Mock logic: count 'active' signals per day/vessel).
    """
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
    """Client summary with order counts"""
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
