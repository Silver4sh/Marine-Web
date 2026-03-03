import streamlit as st
from db.connection import run_query

@st.cache_data(ttl=300)
def get_client_stats():
    query = "SELECT COUNT(code_client) as total_clients, SUM(CASE WHEN created_at <= NOW() - INTERVAL '21 days' and status = 'Active' THEN 1 ELSE 0 END) as new_clients,  SUM(CASE WHEN created_at <= NOW() - INTERVAL '21 days' and status <> 'Active' THEN 1 ELSE 0 END) as deactive_clients FROM operation.clients"
    df = run_query(query)
    if df.empty: return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}
    return {"total_clients": int(df.iloc[0]["total_clients"]), "new_clients": int(df.iloc[0]["new_clients"]), "deactive_clients": int(df.iloc[0]["deactive_clients"])}

@st.cache_data(ttl=300)
def get_clients_summary():
    query = "SELECT c.code_client, c.name, c.industry, c.region, c.status, COUNT(DISTINCT o.id) as total_orders, COALESCE(SUM(p.total_amount), 0) as ltv FROM operation.clients c LEFT JOIN operation.orders o ON c.code_client = o.id_client LEFT JOIN operation.payments p ON o.code_order = p.id_order AND p.status = 'Completed' GROUP BY c.code_client, c.name, c.industry, c.region, c.status ORDER BY ltv DESC"
    return run_query(query)

@st.cache_data(ttl=3600)
def get_client_reliability_scoring():
    query = """
    WITH payment_stats AS (
        SELECT 
            id_order,
            SUM(total_amount) as total_paid,
            MAX(payment_date) as last_payment_date
        FROM operation.payments
        WHERE status = 'Completed'
        GROUP BY 1
    ),
    client_metrics AS (
        SELECT 
            c.code_client,
            c.name,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(ps.total_paid), 0) as total_revenue,
            AVG(EXTRACT(DAY FROM (ps.last_payment_date - o.order_date))) as avg_payment_delay_days
        FROM operation.clients c
        JOIN operation.orders o ON c.code_client = o.id_client
        JOIN payment_stats ps ON o.code_order = ps.id_order
        GROUP BY 1, 2
    )
    SELECT 
        code_client,
        name,
        total_revenue,
        COALESCE(avg_payment_delay_days, 0) as avg_payment_delay,
        (
            (total_revenue / 100000000) * 0.6
            - 
            (COALESCE(avg_payment_delay_days, 30) / 10) * 0.4
        ) as reliability_score
    FROM client_metrics
    ORDER BY reliability_score DESC
    """
    return run_query(query)
