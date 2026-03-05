import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import sb_table

_EMPTY = pd.DataFrame()


def _strip_tz(series: pd.Series) -> pd.Series:
    """Convert tz-aware datetime series to tz-naive UTC for period operations."""
    return pd.to_datetime(series, utc=True).dt.tz_convert(None)


@st.cache_data(ttl=300)
def get_financial_metrics() -> dict:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()

    payments = pd.DataFrame(sb_table("operation", "payments")
        .select("id_order, total_amount, payment_date")
        .eq("status", "Completed").gte("payment_date", cutoff).execute().data)

    total_resp = sb_table("operation", "payments")\
        .select("total_amount").eq("status", "Completed").execute()
    total_revenue = float(sum(r["total_amount"] for r in (total_resp.data or [])))

    if payments.empty:
        return {"total_revenue": total_revenue, "completed_orders": 0,
                "delta_revenue": 0.0, "current_revenue": 0.0, "prev_revenue": 0.0}

    payments["month"] = _strip_tz(payments["payment_date"]).dt.to_period("M")
    monthly = payments.groupby("month").agg(
        revenue=("total_amount", "sum"),
        order_count=("id_order", "nunique"),
    ).sort_index(ascending=False)

    cur   = float(monthly.iloc[0]["revenue"])     if len(monthly) > 0 else 0.0
    prev  = float(monthly.iloc[1]["revenue"])     if len(monthly) > 1 else 0.0
    delta = round(((cur - prev) / prev * 100) if prev > 0 else 0.0, 2)
    return {
        "total_revenue":   total_revenue,
        "current_revenue": cur,
        "prev_revenue":    prev,
        "completed_orders": int(monthly.iloc[0]["order_count"]) if len(monthly) > 0 else 0,
        "delta_revenue":   delta,
    }


@st.cache_data(ttl=300)
def get_revenue_analysis() -> pd.DataFrame:
    rows = sb_table("operation", "payments")\
        .select("total_amount, payment_date").eq("status", "Completed").execute().data
    if not rows:
        return _EMPTY
    df = pd.DataFrame(rows)
    df["month"] = _strip_tz(df["payment_date"]).dt.to_period("M").dt.to_timestamp()
    return df.groupby("month")["total_amount"].sum().reset_index()\
             .rename(columns={"total_amount": "revenue"})\
             .sort_values("month").reset_index(drop=True)


@st.cache_data(ttl=300)
def get_revenue_by_service() -> pd.DataFrame:
    payments = pd.DataFrame(sb_table("operation", "payments")
        .select("id_order, total_amount").eq("status", "Completed").execute().data)
    orders   = pd.DataFrame(sb_table("operation", "orders")
        .select("code_order, id_client").execute().data)
    clients  = pd.DataFrame(sb_table("operation", "clients")
        .select("code_client, industry").execute().data)

    if any(df.empty for df in [payments, orders, clients]):
        return _EMPTY

    df = payments.merge(orders,  left_on="id_order",  right_on="code_order",  how="inner")\
                 .merge(clients, left_on="id_client", right_on="code_client", how="inner")
    return df.groupby("industry")["total_amount"].sum().reset_index()\
             .rename(columns={"industry": "Layanan", "total_amount": "Nilai"})\
             .sort_values("Nilai", ascending=False)


@st.cache_data(ttl=300)
def get_order_stats() -> dict:
    rows = sb_table("operation", "orders").select("status").execute().data
    if not rows:
        return {"total_orders": 0, "completed": 0, "in_completed": 0,
                "on_progress": 0, "failed": 0, "open": 0}
    counts = pd.DataFrame(rows)["status"].value_counts().to_dict()
    return {
        "total_orders":  len(rows),
        "completed":     int(counts.get("Completed", 0)),
        "in_completed":  int(counts.get("In Completed", 0)),
        "on_progress":   int(counts.get("On Progress", 0)),
        "failed":        int(counts.get("Failed", 0)),
        "open":          int(counts.get("Open", 0)),
    }


@st.cache_data(ttl=1800)
def get_revenue_cycle_metrics() -> pd.DataFrame:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
    orders   = pd.DataFrame(sb_table("operation", "orders")
        .select("code_order, order_date").gte("order_date", cutoff).execute().data)
    payments = pd.DataFrame(sb_table("operation", "payments")
        .select("id_order, total_amount, payment_date, status").execute().data)

    if orders.empty or payments.empty:
        return _EMPTY

    orders["order_date"]     = pd.to_datetime(orders["order_date"],     utc=True)
    payments["payment_date"] = pd.to_datetime(payments["payment_date"], utc=True)

    merged = orders.merge(payments, left_on="code_order", right_on="id_order", how="inner")
    merged["days_to_cash"] = (merged["payment_date"] - merged["order_date"]).dt.days
    merged["month"] = _strip_tz(merged["order_date"]).to_period("M").dt.to_timestamp()

    return merged.groupby("month").agg(
        avg_days_to_cash=("days_to_cash", "mean"),
        realized_revenue=("total_amount", "sum"),
        paid_count=("status", lambda x: (x == "Completed").sum()),
        total_orders=("code_order", "count"),
    ).reset_index().sort_values("month", ascending=False)


@st.cache_data(ttl=3600)
def get_client_stats() -> dict:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    rows = sb_table("operation", "clients").select("status, created_at").execute().data
    if not rows:
        return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}
    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return {
        "total_clients":   len(df),
        "new_clients":     int(((df["created_at"] >= cutoff) & (df["status"] == "Active")).sum()),
        "deactive_clients": int((df["status"] != "Active").sum()),
    }
