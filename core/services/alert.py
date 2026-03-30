"""core/services/alert.py — Alert & Notification Engine for MarineOS"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Literal
import streamlit as st

AlertLevel = Literal["critical", "warning", "info", "positive"]
AlertCategory = Literal["geofencing", "anomaly", "environment", "vessel_status", "system"]


# ── Data model ──────────────────────────────────────────────────────────────────
@dataclass
class Alert:
    id: str
    level: AlertLevel
    category: AlertCategory
    title: str
    description: str
    vessel_name: str = ""
    acknowledged: bool = False
    timestamp: float = field(default_factory=time.time)

    @property
    def timestamp_str(self) -> str:
        import datetime
        dt = datetime.datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%d %b %Y, %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "vessel_name": self.vessel_name,
            "acknowledged": self.acknowledged,
            "timestamp": self.timestamp,
            "timestamp_str": self.timestamp_str,
        }


# ── Storage helpers ──────────────────────────────────────────────────────────────
_SESSION_KEY = "_marineos_alerts"


def _get_store() -> list[dict]:
    if _SESSION_KEY not in st.session_state:
        st.session_state[_SESSION_KEY] = []
    return st.session_state[_SESSION_KEY]


def _save_alert(alert: Alert) -> None:
    store = _get_store()
    # Avoid duplicate alerts (same title + vessel in last 5 min)
    cutoff = time.time() - 300
    for existing in store:
        if (
            existing["title"] == alert.title
            and existing["vessel_name"] == alert.vessel_name
            and existing["timestamp"] > cutoff
        ):
            return
    store.insert(0, alert.to_dict())
    # Keep max 100 alerts in session
    if len(store) > 100:
        st.session_state[_SESSION_KEY] = store[:100]


# ── Public API ───────────────────────────────────────────────────────────────────
def create_alert(
    level: AlertLevel,
    category: AlertCategory,
    title: str,
    description: str,
    vessel_name: str = "",
) -> Alert:
    """Create and store a new alert. Returns the Alert object."""
    alert = Alert(
        id=str(uuid.uuid4()),
        level=level,
        category=category,
        title=title,
        description=description,
        vessel_name=vessel_name,
    )
    _save_alert(alert)
    return alert


def get_all_alerts(include_acknowledged: bool = True) -> list[dict]:
    """Return all stored alerts, newest first."""
    store = _get_store()
    if include_acknowledged:
        return store
    return [a for a in store if not a["acknowledged"]]


def get_unacknowledged_count() -> int:
    return sum(1 for a in _get_store() if not a["acknowledged"])


def acknowledge_alert(alert_id: str) -> None:
    for a in _get_store():
        if a["id"] == alert_id:
            a["acknowledged"] = True
            break


def acknowledge_all() -> None:
    for a in _get_store():
        a["acknowledged"] = True


def clear_alerts() -> None:
    st.session_state[_SESSION_KEY] = []


# ── Rule-based auto-detection ────────────────────────────────────────────────────
def check_anomaly_alerts(anomaly_df) -> None:
    """Generate alerts from operational anomaly dataframe."""
    if anomaly_df is None or anomaly_df.empty:
        return
    for _, row in anomaly_df.iterrows():
        a_type = str(row.get("anomaly_type", "Unknown"))
        v_name = str(row.get("vessel_name", row.get("id_vessel", "Tidak Diketahui")))
        speed  = float(row.get("speed", 0) or 0)

        is_critical = "Ghost" in a_type or "hantu" in a_type.lower()
        create_alert(
            level="critical" if is_critical else "warning",
            category="anomaly",
            title=f"Anomali Terdeteksi: {a_type}",
            description=f"Kapal {v_name} menunjukkan perilaku tidak normal. "
                        f"Kecepatan: {speed:.1f} kn. Status: {row.get('reported_status', '—')}",
            vessel_name=v_name,
        )


def check_environment_alerts(env_df, thresholds: dict | None = None) -> None:
    """Generate alerts from environment/sensor dataframe."""
    if env_df is None or env_df.empty:
        return
    th = thresholds or {
        "salinity":    (30.0, 38.0),
        "temperature": (20.0, 32.0),
        "current":     (0.0, 3.0),
    }
    for _, row in env_df.iterrows():
        for param, (lo, hi) in th.items():
            val = row.get(param)
            if val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            if not (lo <= val <= hi):
                label = param.capitalize()
                unit_map = {"salinity": "PSU", "temperature": "°C", "current": "m/s"}
                unit = unit_map.get(param, "")
                create_alert(
                    level="warning",
                    category="environment",
                    title=f"⚠️ Sensor {label} Di Luar Batas Normal",
                    description=f"Nilai {label} terdeteksi {val:.2f} {unit} "
                                f"(batas normal: {lo}–{hi} {unit}). Periksa buoy sensor.",
                )


def check_fleet_status_alerts(fleet: dict) -> None:
    """Generate alert if too many vessels are in maintenance."""
    total = max(fleet.get("total_vessels", 1), 1)
    maint = fleet.get("maintenance", 0)
    pct   = (maint / total) * 100
    if pct >= 50:
        create_alert(
            level="critical",
            category="vessel_status",
            title="🚢 Lebih dari 50% Armada dalam Perawatan",
            description=f"{maint} dari {total} kapal saat ini dalam status "
                        f"perawatan ({pct:.0f}%). Kapasitas operasional sangat terbatas.",
        )
    elif pct >= 30:
        create_alert(
            level="warning",
            category="vessel_status",
            title="⚠️ Banyak Kapal dalam Perawatan",
            description=f"{maint} dari {total} kapal ({pct:.0f}%) dalam perawatan. "
                        f"Pantau ketersediaan armada.",
        )
