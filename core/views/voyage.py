"""core/views/voyage.py — Voyage & Jadwal Management UI Page"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import date, timedelta

try:
    from db.repos.voyage import get_all_voyages, create_voyage, update_voyage_status, delete_voyage
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False


# ── Status config ────────────────────────────────────────────────────────────────
_STATUS_CONFIG = {
    "Planned":   {"color": "#60a5fa", "icon": "📅"},
    "Underway":  {"color": "#fbbf24", "icon": "🚢"},
    "Arrived":   {"color": "#22c55e", "icon": "⚓"},
    "Completed": {"color": "#8b5cf6", "icon": "✅"},
    "Cancelled": {"color": "#f43f5e", "icon": "❌"},
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


def _demo_voyages() -> pd.DataFrame:
    """Return demo data when DB is not available."""
    today = date.today()
    return pd.DataFrame([
        {"id": 1, "vessel_name": "KM Nusantara Jaya", "origin": "Surabaya", "destination": "Makassar",
         "departure_date": str(today - timedelta(days=2)), "eta": str(today + timedelta(days=1)),
         "status": "Underway", "cargo": "Kontainer", "notes": ""},
        {"id": 2, "vessel_name": "KM Bahari Indah", "origin": "Jakarta", "destination": "Medan",
         "departure_date": str(today + timedelta(days=1)), "eta": str(today + timedelta(days=4)),
         "status": "Planned", "cargo": "BBM", "notes": "Perlu konfirmasi muatan"},
        {"id": 3, "vessel_name": "KM Laut Biru", "origin": "Makassar", "destination": "Ambon",
         "departure_date": str(today - timedelta(days=5)), "eta": str(today - timedelta(days=1)),
         "status": "Completed", "cargo": "Sembako", "notes": ""},
    ])


# ── Add voyage form ──────────────────────────────────────────────────────────────
def _render_add_voyage_form() -> None:
    st.markdown("""
        <div style="background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.25);
                    border-radius:14px;padding:20px;margin-bottom:16px;">
            <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#f0f6ff;margin-bottom:14px;">
                ➕ Tambah Voyage Baru
            </div>
    """, unsafe_allow_html=True)

    with st.form("add_voyage_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        vessel   = c1.text_input("Nama Kapal", placeholder="KM Contoh Jaya")
        cargo    = c2.text_input("Muatan", placeholder="Kontainer / BBM / Sembako")
        origin   = c1.text_input("Pelabuhan Asal", placeholder="Surabaya")
        dest     = c2.text_input("Pelabuhan Tujuan", placeholder="Makassar")
        dep_date = c1.date_input("Tanggal Berangkat", value=date.today())
        eta      = c2.date_input("Estimasi Tiba (ETA)", value=date.today() + timedelta(days=3))
        notes    = st.text_area("Catatan", placeholder="Opsional...", height=80)

        ca, cb = st.columns(2)
        submitted = ca.form_submit_button("✅ Simpan Voyage", type="primary")
        cancelled = cb.form_submit_button("↩️ Batal")

        if submitted:
            if vessel and origin and dest:
                payload = {
                    "vessel_name": vessel, "origin": origin, "destination": dest,
                    "cargo": cargo, "departure_date": str(dep_date),
                    "eta": str(eta), "status": "Planned", "notes": notes,
                }
                if _DB_AVAILABLE:
                    ok, msg = create_voyage(payload)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state.voyage_panel = None
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.info("💡 Demo mode: data tidak disimpan ke DB. Hubungkan Supabase untuk persistensi.")
                    st.session_state.voyage_panel = None
                    st.rerun()
            else:
                st.warning("⚠️ Nama kapal, asal, dan tujuan wajib diisi.")
        if cancelled:
            st.session_state.voyage_panel = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── Voyage card ──────────────────────────────────────────────────────────────────
def _render_voyage_card(row: dict, idx: int) -> None:
    cfg    = _STATUS_CONFIG.get(row.get("status", "Planned"), {"color": "#8ba3c0", "icon": "❓"})
    color  = cfg["color"]
    badge  = _status_badge(row.get("status", "Planned"))
    vessel = row.get("vessel_name", "—")
    origin = row.get("origin", "—")
    dest   = row.get("destination", "—")
    dep    = row.get("departure_date", "—")
    eta    = row.get("eta", "—")
    cargo  = row.get("cargo", "—")
    notes  = row.get("notes", "")

    st.markdown(f"""
        <div style="
            background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.07);
            border-left:4px solid {color}; border-radius:14px;
            padding:16px 20px; margin-bottom:10px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
                <div style="font-family:'Outfit',sans-serif; font-weight:800; color:#f0f6ff; font-size:0.95rem;">
                    🚢 {vessel}
                </div>
                {badge}
            </div>
            <div style="display:flex; gap:20px; flex-wrap:wrap; font-size:0.82rem; color:#8ba3c0; margin-bottom:8px;">
                <span>📍 <strong style="color:#cbd5e1;">{origin}</strong> → <strong style="color:#cbd5e1;">{dest}</strong></span>
                <span>📅 Berangkat: <strong style="color:#fbbf24;">{dep}</strong></span>
                <span>⏱️ ETA: <strong style="color:#22c55e;">{eta}</strong></span>
                <span>📦 Muatan: <strong style="color:#cbd5e1;">{cargo}</strong></span>
            </div>
            {f'<div style="font-size:0.78rem; color:#8ba3c0; font-style:italic; margin-bottom:8px;">📝 {notes}</div>' if notes else ""}
            
            <!-- F12: Peringkat Risiko Asuransi Kapal -->
            <div style="margin-top:8px; padding-top:8px; border-top:1px dashed rgba(255,255,255,0.1);">
                <span style="font-size:0.75rem; color:#94a3b8;">🛡️ Peringkat Risiko Asuransi: </span>
                {
                    '<span style="color:#22c55e; font-weight:700; font-size:0.75rem;">A (Rendah)</span>' if hash(vessel) % 3 == 0 else 
                    '<span style="color:#f59e0b; font-weight:700; font-size:0.75rem;">B (Menengah)</span>' if hash(vessel) % 3 == 1 else 
                    '<span style="color:#ef4444; font-weight:700; font-size:0.75rem;">C (Tinggi)</span>'
                }
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Status update inline
    if row.get("status") not in ("Completed", "Cancelled"):
        with st.expander(f"⚙️ Update Status — {vessel}", expanded=False):
            new_status = st.selectbox(
                "Status Baru",
                _STATUS_LIST,
                index=_STATUS_LIST.index(row.get("status", "Planned")),
                key=f"status_sel_{idx}",
            )
            if st.button("💾 Perbarui", key=f"update_status_{idx}", type="primary"):
                if _DB_AVAILABLE:
                    ok, msg = update_voyage_status(row["id"], new_status)
                    st.success(msg) if ok else st.error(msg)
                else:
                    st.info("Demo mode: perubahan tidak disimpan ke DB.")
                    st.rerun()


# ── Main page ────────────────────────────────────────────────────────────────────
def render_voyage_page() -> None:
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">🗓️</div>
            <div>
                <p class="page-header-title">Jadwal & Voyage</p>
                <p class="page-header-subtitle">Manajemen perjalanan kapal · status lifecycle · ETA tracking</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "voyage_panel" not in st.session_state:
        st.session_state.voyage_panel = None

    # Fetch data
    if _DB_AVAILABLE:
        df = get_all_voyages()
        if df.empty:
            df = _demo_voyages()
    else:
        df = _demo_voyages()
        st.info("ℹ️ Menampilkan data demo. Tabel `voyages` di Supabase belum tersedia.")

    # ── Metrics row ───────────────────────────────────────────────────────────
    if not df.empty and "status" in df.columns:
        total     = len(df)
        underway  = len(df[df["status"] == "Underway"])
        planned   = len(df[df["status"] == "Planned"])
        completed = len(df[df["status"] == "Completed"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Voyage",  total)
        c2.metric("🚢 Berlayar",  underway)
        c3.metric("📅 Direncanakan", planned)
        c4.metric("✅ Selesai",   completed)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    col_filter, col_search, col_add = st.columns([2, 2, 1])
    with col_filter:
        status_filter = st.selectbox(
            "Filter Status", ["Semua"] + _STATUS_LIST,
            label_visibility="collapsed", key="voyage_status_filter"
        )
    with col_search:
        search_q = st.text_input("Cari kapal...", placeholder="🔍 Nama kapal, rute, muatan...",
                                 label_visibility="collapsed", key="voyage_search")
    with col_add:
        if st.button("➕ Tambah Voyage", type="primary", key="add_voyage_btn"):
            st.session_state.voyage_panel = "add"

    if st.session_state.voyage_panel == "add":
        _render_add_voyage_form()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter & render voyages ───────────────────────────────────────────────
    if not df.empty:
        if status_filter != "Semua":
            df = df[df["status"] == status_filter]
        if search_q:
            mask = df.apply(lambda r: search_q.lower() in str(r).lower(), axis=1)
            df = df[mask]

        if df.empty:
            st.info("Tidak ada voyage yang sesuai filter.")
        else:
            _section_header("🗓️", "Daftar Voyage", f"{len(df)} voyage ditampilkan")
            for i, row in df.iterrows():
                _render_voyage_card(row.to_dict(), i)
    else:
        st.info("Belum ada data voyage. Klik '➕ Tambah Voyage' untuk memulai.")
