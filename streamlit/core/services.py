"""
core/services.py
================
Backend data-loading layer.

Memisahkan logika pengambilan dan agregasi data dari lapisan UI (views).
Views hanya memanggil fungsi di sini — tidak pernah memanggil database langsung.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from .database import (
    get_fleet_status, get_order_stats, get_financial_metrics,
    get_clients_summary, get_system_settings,
    get_revenue_analysis, get_logistics_performance,
)

# Thread pool reusable — Streamlit-safe (tidak menggunakan asyncio.run)
_executor = ThreadPoolExecutor(max_workers=6)


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------

def load_monitoring_data(role: str) -> dict[str, Any]:
    """
    Memuat semua data yang dibutuhkan halaman Monitoring secara paralel.
    Menggunakan ThreadPoolExecutor — aman untuk Streamlit (bukan asyncio).

    Returns:
        dict dengan kunci: fleet, orders, financial, settings, clients
    """
    from core.config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM

    jobs: dict[str, Any] = {
        "fleet":    _executor.submit(get_fleet_status),
        "orders":   _executor.submit(get_order_stats),
        "settings": _executor.submit(get_system_settings),
        "clients":  _executor.submit(get_clients_summary),
    }

    if role in (ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM):
        jobs["financial"] = _executor.submit(get_financial_metrics)
    else:
        jobs["financial"] = None

    defaults: dict[str, Any] = {
        "fleet": {}, "orders": {}, "financial": {},
        "settings": {}, "clients": [],
    }

    results = dict(defaults)
    for key, future in jobs.items():
        if future is None:
            continue
        try:
            results[key] = future.result(timeout=12)
        except Exception as exc:
            print(f"[services] Data load failed for '{key}': {exc}")

    return results


# ---------------------------------------------------------------------------
# Analytics — helper aggregations
# ---------------------------------------------------------------------------

def compute_order_insight(orders: dict) -> str:
    """Mengembalikan string insight berdasarkan rasio penyelesaian pesanan."""
    completed   = orders.get('completed', 0)
    open_orders = orders.get('open', 0)
    total       = completed + open_orders

    if total == 0:
        return "📊 Belum ada data pesanan."

    ratio = completed / total
    if ratio > 0.8:
        return "✅ **Efisiensi Tinggi**: Mayoritas pesanan telah diselesaikan dengan cepat."
    if open_orders > completed:
        return "⏳ **Bottleneck**: Jumlah pesanan terbuka melebihi kapasitas penyelesaian."
    return "⚖️ **Seimbang**: Alur masuk dan keluar pesanan terjaga."


def compute_fleet_health_pct(fleet: dict) -> int:
    """Menghitung persentase kesehatan armada secara aman."""
    total = max(fleet.get('total_vessels', 1), 1)
    maint = fleet.get('maintenance', 0)
    return round((1 - maint / total) * 100)
