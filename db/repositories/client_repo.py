import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from db.connection import sb_table

_EMPTY = pd.DataFrame()


@st.cache_data(ttl=300)
def get_client_stats() -> dict:
    rows = sb_table("operation", "clients").select("status, created_at").execute().data
    if not rows:
        return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}

    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=21)
    return {
        "total_clients":   len(df),
        "new_clients":     int(((df["created_at"] <= cutoff) & (df["status"] == "Active")).sum()),
        "deactive_clients": int((df["status"] != "Active").sum()),
    }


@st.cache_data(ttl=300)
def get_clients_summary() -> pd.DataFrame:
    clients  = pd.DataFrame(sb_table("operation", "clients")
        .select("code_client, name, industry, region, status").execute().data)
    if clients.empty:
        return _EMPTY

    orders   = pd.DataFrame(sb_table("operation", "orders")
        .select("id, id_client, code_order").execute().data)
    payments = pd.DataFrame(sb_table("operation", "payments")
        .select("id_order, total_amount").eq("status", "Completed").execute().data)

    if not orders.empty:
        counts = orders.groupby("id_client")["id"].count().reset_index()
        counts.columns = ["code_client", "total_orders"]
        clients = clients.merge(counts, on="code_client", how="left")

        if not payments.empty:
            ltv = payments.groupby("id_order")["total_amount"].sum().reset_index()
            ltv.columns = ["code_order", "payment_total"]
            o = orders.merge(ltv, on="code_order", how="left")
            c_ltv = o.groupby("id_client")["payment_total"].sum().reset_index()
            c_ltv.columns = ["code_client", "ltv"]
            clients = clients.merge(c_ltv, on="code_client", how="left")

    clients["total_orders"] = clients.get("total_orders", 0).fillna(0).astype(int)
    clients["ltv"] = clients.get("ltv", 0).fillna(0)
    return clients.sort_values("ltv", ascending=False)


@st.cache_data(ttl=3600)
def get_client_reliability_scoring() -> pd.DataFrame:
    clients  = pd.DataFrame(sb_table("operation", "clients")
        .select("code_client, name").execute().data)
    orders   = pd.DataFrame(sb_table("operation", "orders")
        .select("code_order, id_client, order_date").execute().data)
    payments = pd.DataFrame(sb_table("operation", "payments")
        .select("id_order, total_amount, payment_date")
        .eq("status", "Completed").execute().data)

    if any(df.empty for df in [clients, orders, payments]):
        return _EMPTY

    orders["order_date"]      = pd.to_datetime(orders["order_date"],      utc=True)
    payments["payment_date"]  = pd.to_datetime(payments["payment_date"],  utc=True)

    merged = orders.merge(payments, left_on="code_order", right_on="id_order", how="inner")
    merged["days_to_pay"] = (merged["payment_date"] - merged["order_date"]).dt.days

    metrics = merged.groupby("id_client").agg(
        total_revenue=("total_amount", "sum"),
        avg_payment_delay=("days_to_pay", "mean"),
    ).reset_index().fillna({"avg_payment_delay": 30})

    result = clients.merge(metrics, left_on="code_client", right_on="id_client", how="inner")
    result["reliability_score"] = (
        (result["total_revenue"] / 100_000_000) * 0.6
        - (result["avg_payment_delay"] / 10) * 0.4
    )
    return result[["code_client", "name", "total_revenue",
                   "avg_payment_delay", "reliability_score"]].sort_values(
        "reliability_score", ascending=False)
