import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import get_supabase


@st.cache_data(ttl=300)
def get_financial_metrics():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()

    payments = pd.DataFrame(sb.schema("operation").table("payments")
        .select("id_order, total_amount, payment_date, status")
        .eq("status", "Completed").gte("payment_date", cutoff).execute().data)

    all_payments = pd.DataFrame(sb.schema("operation").table("payments")
        .select("total_amount").eq("status", "Completed").execute().data)

    total_revenue = float(all_payments["total_amount"].sum()) if not all_payments.empty else 0.0

    if payments.empty:
        return {"total_revenue": total_revenue, "completed_orders": 0,
                "delta_revenue": 0.0, "current_revenue": 0.0, "prev_revenue": 0.0}

    payments["payment_date"] = pd.to_datetime(payments["payment_date"], utc=True)
    payments["month"] = payments["payment_date"].dt.to_period("M")

    monthly = payments.groupby("month").agg(
        revenue=("total_amount", "sum"),
        order_count=("id_order", "nunique")
    ).sort_index(ascending=False)

    cur  = float(monthly.iloc[0]["revenue"]) if len(monthly) > 0 else 0.0
    prev = float(monthly.iloc[1]["revenue"]) if len(monthly) > 1 else 0.0
    delta = round(((cur - prev) / prev * 100) if prev > 0 else 0.0, 2)
    completed = int(monthly.iloc[0]["order_count"]) if len(monthly) > 0 else 0

    return {"total_revenue": total_revenue, "current_revenue": cur,
            "prev_revenue": prev, "completed_orders": completed, "delta_revenue": delta}


@st.cache_data(ttl=300)
def get_revenue_analysis():
    sb = get_supabase()
    resp = sb.schema("operation").table("payments")\
        .select("total_amount, payment_date").eq("status", "Completed").execute()
    if not resp.data:
        return pd.DataFrame()

    df = pd.DataFrame(resp.data)
    df["payment_date"] = pd.to_datetime(df["payment_date"], utc=True)
    df["month"] = df["payment_date"].dt.to_period("M").dt.to_timestamp()
    return df.groupby("month")["total_amount"].sum().reset_index().rename(
        columns={"month": "month", "total_amount": "revenue"}).sort_values("month")


@st.cache_data(ttl=300)
def get_revenue_by_service():
    sb = get_supabase()
    payments = pd.DataFrame(sb.schema("operation").table("payments")
        .select("id_order, total_amount").eq("status", "Completed").execute().data)
    orders = pd.DataFrame(sb.schema("operation").table("orders")
        .select("code_order, id_client").execute().data)
    clients = pd.DataFrame(sb.schema("operation").table("clients")
        .select("code_client, industry").execute().data)

    if payments.empty or orders.empty or clients.empty:
        return pd.DataFrame()

    df = payments.merge(orders, left_on="id_order", right_on="code_order", how="inner")
    df = df.merge(clients, left_on="id_client", right_on="code_client", how="inner")
    result = df.groupby("industry")["total_amount"].sum().reset_index()
    result.columns = ["Layanan", "Nilai"]
    return result.sort_values("Nilai", ascending=False)


@st.cache_data(ttl=300)
def get_order_stats():
    sb = get_supabase()
    resp = sb.schema("operation").table("orders").select("status").execute()
    if not resp.data:
        return {"total_orders": 0, "completed": 0, "in_completed": 0,
                "on_progress": 0, "failed": 0, "open": 0}

    df = pd.DataFrame(resp.data)
    counts = df["status"].value_counts().to_dict()
    return {
        "total_orders":  len(df),
        "completed":     int(counts.get("Completed", 0)),
        "in_completed":  int(counts.get("In Completed", 0)),
        "on_progress":   int(counts.get("On Progress", 0)),
        "failed":        int(counts.get("Failed", 0)),
        "open":          int(counts.get("Open", 0)),
    }


@st.cache_data(ttl=1800)
def get_revenue_cycle_metrics():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()

    orders = pd.DataFrame(sb.schema("operation").table("orders")
        .select("code_order, order_date").gte("order_date", cutoff).execute().data)
    payments = pd.DataFrame(sb.schema("operation").table("payments")
        .select("id_order, total_amount, payment_date, status").execute().data)

    if orders.empty or payments.empty:
        return pd.DataFrame()

    orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
    payments["payment_date"] = pd.to_datetime(payments["payment_date"], utc=True)

    merged = orders.merge(payments, left_on="code_order", right_on="id_order", how="inner")
    merged["days_to_cash"] = (merged["payment_date"] - merged["order_date"]).dt.days
    merged["month"] = merged["order_date"].dt.to_period("M").dt.to_timestamp()

    result = merged.groupby("month").agg(
        avg_days_to_cash=("days_to_cash", "mean"),
        realized_revenue=("total_amount", "sum"),
        paid_count=("status", lambda x: (x == "Completed").sum()),
        total_orders=("code_order", "count")
    ).reset_index().sort_values("month", ascending=False)
    return result


@st.cache_data(ttl=3600)
def get_client_stats():
    sb = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    resp = sb.schema("operation").table("clients").select("code_client, status, created_at").execute()
    if not resp.data:
        return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}

    df = pd.DataFrame(resp.data)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return {
        "total_clients":  len(df),
        "new_clients":    int(((df["created_at"] >= cutoff) & (df["status"] == "Active")).sum()),
        "deactive_clients": int((df["status"] != "Active").sum()),
    }
