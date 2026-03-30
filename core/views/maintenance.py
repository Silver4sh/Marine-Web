"""core/views/maintenance.py — Vessel Maintenance Tracker"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import date, timedelta

try:
    from db.repos.maintenance import get_all_maintenance, create_maintenance, update_maintenance_status
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False


_STATUS_CONFIG = {
    "Scheduled":   {"color": "#60a5fa", "icon": "📅"},
    "In Progress": {"color": "#fbbf24", "icon": "🛠️"},
    "Done":        {"color": "#22c55e", "icon": "✅"},
    "Overdue":     {"color": "#f43f5e", "icon": "🚨"},
}
_STATUS_LIST = list(_STATUS_CONFIG.keys())


def _status_badge(status: str) -> str:
    cfg = _STATUS_CONFIG.get(status, {"color": "#8ba3c0", "icon": "❓"})
    c = cfg["color"]
    i = cfg["icon"]
    return (
        f'<span style="background:{c}22; color:{c}; border:1px solid {c}55; '
        f'border-radius:99px; font-size:0.72rem; font-weight:700; padding:2px 9px;">'
        f'{i} {status}</span>'
    )


def _section_header(icon: str, title: str, subtitle: str = "") -> None:
    sub = f'<div style="font-size:0.78rem;color:#8ba3c0;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;margin-top:4px;">
            <span style="font-size:1.15rem;">{icon}</span>
            <div>
                <div style="font-family:'Outfit',sans-serif;font-size:0.95rem;font-weight:800;color:#f0f6ff;">{title}</div>
                {sub}
            </div>
        </div>
    """, unsafe_allow_html=True)


def _demo_maintenance() -> pd.DataFrame:
    today = date.today()
    return pd.DataFrame([
        {"id": 1, "vessel_name": "KM Sabuk", "component": "Mesin Utama", "type": "Rutin",
         "scheduled_date": str(today + timedelta(days=5)), "status": "Scheduled", "notes": "Ganti oli filter"},
        {"id": 2, "vessel_name": "KM Bahari", "component": "Sistem Navigasi", "type": "Perbaikan",
         "scheduled_date": str(today - timedelta(days=2)), "status": "Overdue", "notes": "Periksa radar"},
        {"id": 3, "vessel_name": "KM Nusantara", "component": "Hull", "type": "Terjadwal (Docking)",
         "scheduled_date": str(today), "status": "In Progress", "notes": "Dry dock rutin"},
    ])


def _render_add_form() -> None:
    st.markdown("""
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);
                    border-radius:14px;padding:20px;margin-bottom:16px;">
            <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#f0f6ff;margin-bottom:14px;">
                ➕ Tambah Jadwal Maintenance
            </div>
    """, unsafe_allow_html=True)

    with st.form("add_maint_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        vessel = c1.text_input("Nama Kapal", placeholder="KM Contoh")
        comp   = c2.text_input("Komponen", placeholder="Mesin / Radar / Hull")
        m_type = c1.selectbox("Jenis", ["Rutin", "Perbaikan", "Terjadwal (Docking)"])
        s_date = c2.date_input("Tanggal Jadwal", value=date.today() + timedelta(days=7))
        notes  = st.text_area("Catatan Teknisi")

        ca, cb = st.columns(2)
        submitted = ca.form_submit_button("✅ Simpan Jadwal", type="primary")
        cancelled = cb.form_submit_button("↩️ Batal")

        if submitted:
            if vessel and comp:
                payload = {
                    "vessel_name": vessel, "component": comp, "type": m_type,
                    "scheduled_date": str(s_date), "status": "Scheduled", "notes": notes
                }
                if _DB_AVAILABLE:
                    ok, msg = create_maintenance(payload)
                    st.success(msg) if ok else st.error(msg)
                    st.session_state.maint_panel = None
                else:
                    st.info("Demo mode: Data tidak disimpan.")
                    st.session_state.maint_panel = None
                st.rerun()
            else:
                st.warning("Nama kapal dan komponen wajib diisi.")
        if cancelled:
            st.session_state.maint_panel = None
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_maint_card(row: dict, idx: int) -> None:
    badge  = _status_badge(row.get("status", "Scheduled"))
    vessel = row.get("vessel_name", "—")
    comp   = row.get("component", "—")
    m_type = row.get("type", "—")
    s_date = row.get("scheduled_date", "—")
    notes  = row.get("notes", "")

    st.markdown(f"""
        <div style="
            background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.07);
            border-left:4px solid {_STATUS_CONFIG.get(row.get('status'), {}).get('color', '#8b')};
            border-radius:14px; padding:16px 20px; margin-bottom:10px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="font-family:'Outfit',sans-serif; font-weight:800; color:#f0f6ff; font-size:0.95rem;">
                    🚢 {vessel} — {comp}
                </div>
                {badge}
            </div>
            <div style="display:flex; gap:20px; flex-wrap:wrap; font-size:0.82rem; color:#8ba3c0; margin-bottom:8px;">
                <span>⚙️ Jenis: <strong style="color:#cbd5e1;">{m_type}</strong></span>
                <span>📅 Tanggal: <strong style="color:#cbd5e1;">{s_date}</strong></span>
            </div>
            {f'<div style="font-size:0.78rem; color:#8ba3c0; font-style:italic;">📝 {notes}</div>' if notes else ""}
        </div>
    """, unsafe_allow_html=True)

    if row.get("status") != "Done":
        with st.expander("Update Status", expanded=False):
            new_status = st.selectbox("Status Baru", _STATUS_LIST,
                                      index=_STATUS_LIST.index(row.get("status")), key=f"ms_sel_{idx}")
            if st.button("Simpan", key=f"btn_{idx}", type="primary"):
                if _DB_AVAILABLE:
                    ok, msg = update_maintenance_status(row["id"], new_status)
                    st.success(msg) if ok else st.error(msg)
                else:
                    st.info("Demo mode")
                st.rerun()


def render_maintenance_page():
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">🛠️</div>
            <div>
                <p class="page-header-title">Maintenance Tracker</p>
                <p class="page-header-subtitle">Jadwal perawatan kapal · riwayat service · status kerusakan</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "maint_panel" not in st.session_state:
        st.session_state.maint_panel = None

    if _DB_AVAILABLE:
        df = get_all_maintenance()
        if df.empty: df = _demo_maintenance()
    else:
        df = _demo_maintenance()

    c1, c2 = st.columns([5, 1])
    with c2:
        if st.button("➕ Tambah Data", type="primary"):
            st.session_state.maint_panel = "add"

    if st.session_state.maint_panel == "add":
        _render_add_form()

    # Filter & Render
    if not df.empty:
        _section_header("🛠️", "Jadwal Perawatan Aktif")
        for i, row in df.iterrows():
            _render_maint_card(row.to_dict(), i)
    else:
        st.info("Tidak ada jadwal maintenance.")
