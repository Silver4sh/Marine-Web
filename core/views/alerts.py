"""core/views/alerts.py — Alert Management UI Page"""
import streamlit as st
from core.services.alert import (
    get_all_alerts,
    get_unacknowledged_count,
    acknowledge_alert,
    acknowledge_all,
    clear_alerts,
    AlertLevel,
)

# ── Style constants ──────────────────────────────────────────────────────────────
_LEVEL_CONFIG: dict[str, dict] = {
    "critical": {
        "icon":   "🚨",
        "accent": "#f43f5e",
        "bg":     "rgba(244,63,94,0.08)",
        "border": "rgba(244,63,94,0.25)",
    },
    "warning": {
        "icon":   "⚠️",
        "accent": "#f59e0b",
        "bg":     "rgba(245,158,11,0.08)",
        "border": "rgba(245,158,11,0.25)",
    },
    "info": {
        "icon":   "ℹ️",
        "accent": "#60a5fa",
        "bg":     "rgba(96,165,250,0.08)",
        "border": "rgba(96,165,250,0.22)",
    },
    "positive": {
        "icon":   "✅",
        "accent": "#22c55e",
        "bg":     "rgba(34,197,94,0.08)",
        "border": "rgba(34,197,94,0.22)",
    },
}

_CATEGORY_LABELS: dict[str, str] = {
    "geofencing":    "Geofencing",
    "anomaly":       "Anomali Kapal",
    "environment":   "Sensor Lingkungan",
    "vessel_status": "Status Armada",
    "system":        "Sistem",
}


# ── Components ───────────────────────────────────────────────────────────────────
def _render_alert_card(alert: dict, idx: int) -> None:
    cfg = _LEVEL_CONFIG.get(alert["level"], _LEVEL_CONFIG["info"])
    icon   = cfg["icon"]
    accent = cfg["accent"]
    bg     = cfg["bg"]
    border = cfg["border"]
    acked  = alert["acknowledged"]
    opacity = "0.5" if acked else "1"
    cat_label  = _CATEGORY_LABELS.get(alert["category"], alert["category"].title())
    vessel_str = f' · <span style="color:#fbbf24;">🚢 {alert["vessel_name"]}</span>' if alert["vessel_name"] else ""

    st.markdown(f"""
        <div style="
            background:{bg}; border:1px solid {border};
            border-left:4px solid {accent};
            border-radius:12px; padding:14px 18px; margin-bottom:10px;
            opacity:{opacity};
            display:flex; gap:14px; align-items:flex-start;
        ">
            <div style="font-size:1.4rem; flex-shrink:0; margin-top:2px;">{icon}</div>
            <div style="flex:1; min-width:0;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:4px;">
                    <div style="font-family:'Outfit',sans-serif; font-weight:800;
                                color:#f0f6ff; font-size:0.9rem;">{alert['title']}</div>
                    <div style="display:flex; gap:6px; align-items:center; flex-shrink:0;">
                        <span style="background:{accent}22; color:{accent}; border:1px solid {accent}55;
                                     border-radius:99px; font-size:0.68rem; font-weight:700;
                                     padding:2px 8px;">{cat_label}</span>
                        {"<span style='font-size:0.68rem; color:#8ba3c0; font-style:italic;'>✔ Ditangani</span>" if acked else ""}
                    </div>
                </div>
                <div style="color:#8ba3c0; font-size:0.82rem; line-height:1.5; margin-bottom:6px;">
                    {alert['description']}{vessel_str}
                </div>
                <div style="font-size:0.72rem; color:#475569;">🕐 {alert['timestamp_str']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not acked:
        if st.button(
            "✔ Tandai Ditangani",
            key=f"ack_alert_{alert['id']}_{idx}",
            type="secondary",
        ):
            acknowledge_alert(alert["id"])
            st.rerun()


def _render_empty_state() -> None:
    st.markdown("""
        <div style="
            text-align:center; padding:40px 20px;
            background:rgba(34,197,94,0.06);
            border:1px solid rgba(34,197,94,0.15);
            border-radius:16px; margin-top:10px;
        ">
            <div style="font-size:2.5rem; margin-bottom:10px;">✅</div>
            <div style="font-family:'Outfit',sans-serif; font-weight:700; color:#22c55e;
                        font-size:1rem; margin-bottom:6px;">Tidak Ada Alert Aktif</div>
            <div style="font-size:0.82rem; color:#8ba3c0;">
                Semua sistem operasional normal. Alert baru akan muncul secara otomatis.
            </div>
        </div>
    """, unsafe_allow_html=True)


# ── Main page ────────────────────────────────────────────────────────────────────
def render_alerts_page() -> None:
    # Page header
    unread = get_unacknowledged_count()
    badge = (
        f'<span style="background:#f43f5e; color:white; border-radius:99px; '
        f'font-size:0.72rem; padding:2px 8px; margin-left:8px; '
        f'font-weight:700; font-family:\'Outfit\',sans-serif;">{unread} Baru</span>'
        if unread > 0 else ""
    )
    st.markdown(f"""
        <div class="page-header">
            <div class="page-header-icon">🔔</div>
            <div>
                <p class="page-header-title">Pusat Alert{badge}</p>
                <p class="page-header-subtitle">Notifikasi real-time · anomali · status armada · lingkungan</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    alerts = get_all_alerts(include_acknowledged=True)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    col_filter, col_act1, col_act2 = st.columns([3, 1, 1])
    with col_filter:
        filter_options = ["Semua", "Belum Ditangani", "critical", "warning", "info"]
        selected_filter = st.selectbox(
            "Filter",
            filter_options,
            label_visibility="collapsed",
            key="alert_filter",
        )
    with col_act1:
        if st.button("✔ Tandai Semua", type="secondary", key="ack_all_btn"):
            acknowledge_all()
            st.rerun()
    with col_act2:
        if st.button("🗑️ Hapus Semua", type="secondary", key="clear_alerts_btn"):
            clear_alerts()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Summary metrics ───────────────────────────────────────────────────────
    total     = len(alerts)
    critical  = sum(1 for a in alerts if a["level"] == "critical" and not a["acknowledged"])
    warnings  = sum(1 for a in alerts if a["level"] == "warning"  and not a["acknowledged"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Alert", total)
    c2.metric("🚨 Critical", critical)
    c3.metric("⚠️ Warning",  warnings)
    c4.metric("✔ Ditangani", total - unread)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter alerts ─────────────────────────────────────────────────────────
    if selected_filter == "Belum Ditangani":
        display_alerts = [a for a in alerts if not a["acknowledged"]]
    elif selected_filter in ("critical", "warning", "info"):
        display_alerts = [a for a in alerts if a["level"] == selected_filter]
    else:
        display_alerts = alerts

    # ── Render ────────────────────────────────────────────────────────────────
    if not display_alerts:
        _render_empty_state()
    else:
        for i, alert in enumerate(display_alerts):
            _render_alert_card(alert, i)
