import streamlit as st
import pandas as pd
from db.connection import run_query

@st.cache_data(ttl=300)
def get_financial_metrics():
    """
    Returns financial summary with REAL month-over-month delta.
    Compares current calendar month revenue vs last calendar month.
    """
    query = """
    WITH monthly AS (
        SELECT
            DATE_TRUNC('month', payment_date) AS month,
            SUM(total_amount)                  AS revenue,
            COUNT(DISTINCT id_order)           AS order_count
        FROM operation.payments
        WHERE status = 'Completed'
          AND payment_date >= NOW() - INTERVAL '2 months'
        GROUP BY 1
        ORDER BY 1 DESC
        LIMIT 2
    )
    SELECT
        COALESCE(MAX(CASE WHEN row_num = 1 THEN revenue  END), 0) AS current_revenue,
        COALESCE(MAX(CASE WHEN row_num = 2 THEN revenue  END), 0) AS prev_revenue,
        COALESCE(MAX(CASE WHEN row_num = 1 THEN order_count END), 0) AS completed_orders,
        (SELECT COALESCE(SUM(total_amount), 0) FROM operation.payments WHERE status = 'Completed') AS total_revenue_all
    FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY month DESC) AS row_num FROM monthly) ranked
    """
    df = run_query(query)
    if df.empty:
        return {"total_revenue": 0, "completed_orders": 0, "delta_revenue": 0.0,
                "current_revenue": 0, "prev_revenue": 0}

    row = df.iloc[0]
    cur  = float(row.get("current_revenue", 0) or 0)
    prev = float(row.get("prev_revenue",    0) or 0)
    delta = ((cur - prev) / prev * 100) if prev > 0 else 0.0

    return {
        "total_revenue":     float(row.get("total_revenue_all", 0) or 0),
        "current_revenue":   cur,
        "prev_revenue":      prev,
        "completed_orders":  int(row.get("completed_orders", 0) or 0),
        "delta_revenue":     round(delta, 2),
    }


@st.cache_data(ttl=300)
def get_revenue_analysis():
    query = """
    SELECT
        DATE_TRUNC('month', payment_date) AS month,
        SUM(total_amount)                 AS revenue
    FROM operation.payments
    WHERE status = 'Completed'
    GROUP BY 1
    ORDER BY 1 ASC
    """
    return run_query(query)


@st.cache_data(ttl=300)
def get_revenue_by_service():
    query = """
    SELECT
        c.industry AS "Layanan",
        SUM(p.total_amount) AS "Nilai"
    FROM operation.payments p
    JOIN operation.orders  o ON p.id_order  = o.code_order
    JOIN operation.clients c ON o.id_client = c.code_client
    WHERE p.status = 'Completed'
    GROUP BY c.industry
    ORDER BY "Nilai" DESC
    """
    return run_query(query)


@st.cache_data(ttl=300)
def get_order_stats():
    query = """
    SELECT
        COUNT(*)                                                      AS total_orders,
        SUM(CASE WHEN status = 'Completed'   THEN 1 ELSE 0 END)      AS completed,
        SUM(CASE WHEN status = 'In Completed' THEN 1 ELSE 0 END)     AS in_completed,
        SUM(CASE WHEN status = 'On Progress' THEN 1 ELSE 0 END)      AS on_progress,
        SUM(CASE WHEN status = 'Failed'      THEN 1 ELSE 0 END)      AS failed,
        SUM(CASE WHEN status = 'Open'        THEN 1 ELSE 0 END)      AS open
    FROM operation.orders
    """
    df = run_query(query)
    if df.empty:
        return {"total_orders": 0, "completed": 0, "in_completed": 0,
                "on_progress": 0, "failed": 0, "open": 0}
    row = df.iloc[0]
    return {k: int(row.get(k, 0) or 0) for k in
            ["total_orders", "completed", "in_completed", "on_progress", "failed", "open"]}


@st.cache_data(ttl=1800)
def get_revenue_cycle_metrics():
    query = """
    SELECT
        DATE_TRUNC('month', o.order_date) AS month,
        AVG(EXTRACT(DAY FROM (p.payment_date - o.order_date))) AS avg_days_to_cash,
        SUM(p.total_amount)               AS realized_revenue,
        SUM(CASE WHEN p.status = 'Completed' THEN 1 ELSE 0 END) AS paid_count,
        COUNT(o.code_order)               AS total_orders
    FROM operation.orders o
    JOIN operation.payments p ON o.code_order = p.id_order
    WHERE o.order_date >= NOW() - INTERVAL '6 months'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)


@st.cache_data(ttl=3600)
def get_client_stats():
    query = """
    SELECT
        COUNT(code_client) AS total_clients,
        SUM(CASE WHEN created_at >= NOW() - INTERVAL '30 days' AND status = 'Active'  THEN 1 ELSE 0 END) AS new_clients,
        SUM(CASE WHEN status <> 'Active' THEN 1 ELSE 0 END) AS deactive_clients
    FROM operation.clients
    """
    df = run_query(query)
    if df.empty:
        return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}
    row = df.iloc[0]
    return {k: int(row.get(k, 0) or 0) for k in ["total_clients", "new_clients", "deactive_clients"]}
