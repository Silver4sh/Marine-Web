import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import get_supabase


@st.cache_data(ttl=300)
def get_client_stats():
    sb = get_supabase()
    resp = sb.schema("operation").table("clients").select("code_client, status, created_at").execute()
    if not resp.data:
        return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}

    df = pd.DataFrame(resp.data)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=21)

    total = len(df)
    new = int(((df["created_at"] <= cutoff) & (df["status"] == "Active")).sum())
    deactive = int(((df["created_at"] <= cutoff) & (df["status"] != "Active")).sum())
    return {"total_clients": total, "new_clients": new, "deactive_clients": deactive}


@st.cache_data(ttl=300)
def get_clients_summary():
    sb = get_supabase()

    clients = pd.DataFrame(sb.schema("operation").table("clients")
        .select("code_client, name, industry, region, status").execute().data)
    if clients.empty:
        return pd.DataFrame()

    orders = pd.DataFrame(sb.schema("operation").table("orders")
        .select("id, id_client, code_order").execute().data)

    payments = pd.DataFrame(sb.schema("operation").table("payments")
        .select("id_order, total_amount, status").execute().data)

    # Total orders per client
    if not orders.empty:
        order_counts = orders.groupby("id_client")["id"].count().reset_index()
        order_counts.columns = ["code_client", "total_orders"]
        clients = clients.merge(order_counts, on="code_client", how="left")
    else:
        clients["total_orders"] = 0

    # LTV: sum of completed payments
    if not orders.empty and not payments.empty:
        completed = payments[payments["status"] == "Completed"]
        order_ltv = completed.groupby("id_order")["total_amount"].sum().reset_index()
        order_ltv.columns = ["code_order", "payment_total"]
        orders_ltv = orders.merge(order_ltv, on="code_order", how="left")
        client_ltv = orders_ltv.groupby("id_client")["payment_total"].sum().reset_index()
        client_ltv.columns = ["code_client", "ltv"]
        clients = clients.merge(client_ltv, on="code_client", how="left")
    else:
        clients["ltv"] = 0

    clients["total_orders"] = clients.get("total_orders", 0).fillna(0).astype(int)
    clients["ltv"] = clients.get("ltv", 0).fillna(0)
    return clients.sort_values("ltv", ascending=False)


@st.cache_data(ttl=3600)
def get_client_reliability_scoring():
    sb = get_supabase()

    clients = pd.DataFrame(sb.schema("operation").table("clients")
        .select("code_client, name").execute().data)
    orders = pd.DataFrame(sb.schema("operation").table("orders")
        .select("id, code_order, id_client, order_date").execute().data)
    payments = pd.DataFrame(sb.schema("operation").table("payments")
        .select("id_order, total_amount, payment_date, status")
        .eq("status", "Completed").execute().data)

    if clients.empty or orders.empty or payments.empty:
        return pd.DataFrame()

    orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
    payments["payment_date"] = pd.to_datetime(payments["payment_date"], utc=True)

    # Merge payments onto orders
    merged = orders.merge(payments, left_on="code_order", right_on="id_order", how="inner")
    merged["days_to_pay"] = (merged["payment_date"] - merged["order_date"]).dt.days

    metrics = merged.groupby("id_client").agg(
        total_revenue=("total_amount", "sum"),
        avg_payment_delay=("days_to_pay", "mean")
    ).reset_index()
    metrics["avg_payment_delay"] = metrics["avg_payment_delay"].fillna(30)

    result = clients.merge(metrics, left_on="code_client", right_on="id_client", how="inner")
    result["reliability_score"] = (
        (result["total_revenue"] / 100_000_000) * 0.6
        - (result["avg_payment_delay"] / 10) * 0.4
    )
    return result[["code_client", "name", "total_revenue", "avg_payment_delay", "reliability_score"]]\
        .sort_values("reliability_score", ascending=False)
