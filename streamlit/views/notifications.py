"""
views/notifications.py
======================
UI layer untuk panel notifikasi.

Tanggung jawab:
  - Merender item notifikasi (inbox, selesai, sampah)
  - Mengelola state notifikasi via session_state
  - TIDAK ada logika bisnis — hanya presentasi
"""
import datetime
import streamlit as st

from core import (
    get_fleet_status, get_financial_metrics, get_system_settings,
    get_clients_summary, get_logs, get_notification_id, generate_insights,
)


# ---------------------------------------------------------------------------
# Data loading (backend — hanya satu fungsi)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60, show_spinner=False)
def _load_data(role: str) -> dict:
    """Memuat semua data yang dibutuhkan panel notifikasi."""
    return {
        "fleet":     get_fleet_status(),
        "financial": get_financial_metrics(),
        "settings":  get_system_settings(),
        "clients":   get_clients_summary(),
        "logs":      get_logs(),
    }


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def _ensure_state() -> None:
    if 'notification_states' not in st.session_state:
        st.session_state.notification_states = {}


def update_notification_status(notif_id: str, new_status: str) -> None:
    st.session_state.notification_states[notif_id] = new_status


def restore_notification(notif_id: str) -> None:
    st.session_state.notification_states.pop(notif_id, None)


# ---------------------------------------------------------------------------
# Item builder (backend data → UI-ready list)
# ---------------------------------------------------------------------------

def _build_notification_items(role: str) -> list[dict]:
    """Gabungkan AI insights dan log sistem menjadi list item notifikasi."""
    data    = _load_data(role)
    raw     = generate_insights(
        data['fleet'], data['financial'], role, data['settings'], data['clients']
    )

    items: list[dict] = []

    for i in raw:
        i['id']       = get_notification_id(i.get('category', 'Alert'), i['message'], "dynamic")
        i['time_str'] = "Baru Saja"
        items.append(i)

    logs = data['logs']
    if not logs.empty:
        for _, row in logs.head(10).iterrows():
            ts  = row['changed_at']
            if isinstance(ts, str):
                ts = datetime.datetime.now()
            msg = f"{row['action']} pada {row['table_name']}"
            items.append({
                "id":       get_notification_id("System", msg, str(ts)),
                "category": "System",
                "message":  msg,
                "time_str": ts.strftime("%H:%M") if hasattr(ts, 'strftime') else "Hari Ini",
                "level":    "info",
            })

    return items


# ---------------------------------------------------------------------------
# UI helpers (private)
# ---------------------------------------------------------------------------

_ICONS = {
    "FLEET": "🚢", "FINANCIAL": "💰", "SYSTEM": "🖥️",
    "CLIENTS": "👥", "ALERT": "⚠️",
}
_CAT_LABELS = {
    "FLEET": "ARMADA", "FINANCIAL": "KEUANGAN", "SYSTEM": "SISTEM",
    "CLIENTS": "KLIEN", "ALERT": "PERINGATAN",
}
_ITEM_STYLES = {
    'inbox': {'bg': 'rgba(255,255,255,0.05)', 'border': 'transparent', 'text': '#f8fafc', 'dot': True},
    'done':  {'bg': 'rgba(20,83,45,0.2)',     'border': '#22c55e',      'text': '#f0fdf4', 'dot': False},
    'trash': {'bg': 'rgba(0,0,0,0.2)',        'border': 'transparent',  'text': '#64748b', 'dot': False},
}


def _render_item_card(item: dict, status: str) -> None:
    """Merender kartu notifikasi dan tombol aksi."""
    notif_id    = item['id']
    category    = item.get('category', 'ALERT').upper()
    icon        = _ICONS.get(category, "🔔")
    label       = _CAT_LABELS.get(category, category)
    style       = _ITEM_STYLES.get(status, _ITEM_STYLES['inbox'])
    dot_html    = (
        '<span style="height:8px;width:8px;background:#0ea5e9;'
        'border-radius:50%;display:inline-block;margin-right:8px;"></span>'
        if style['dot'] else ''
    )

    st.markdown(
        f'<div style="background:{style["bg"]};border-left:3px solid {style["border"]};'
        f'padding:12px;border-radius:6px;margin-bottom:8px;">'
        f'  <div style="display:flex;justify-content:space-between;align-items:center;">'
        f'    <div style="display:flex;align-items:center;">'
        f'      {dot_html}'
        f'      <span style="font-size:16px;margin-right:6px;">{icon}</span>'
        f'      <strong style="color:{style["text"]};font-size:14px;">{label}</strong>'
        f'    </div>'
        f'    <small style="color:#94a3b8;font-size:11px;">{item.get("time_str","")}</small>'
        f'  </div>'
        f'  <div style="color:{style["text"]};font-size:13px;margin-top:6px;">'
        f'    {item["message"]}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Action buttons — right-aligned
    _, col_btn = st.columns([0.8, 0.2])
    with col_btn:
        if status == 'inbox':
            ca, cb = st.columns(2)
            ca.button("✅", key=f"d_{notif_id}",  on_click=update_notification_status,
                      args=(notif_id, 'done'),  width='stretch')
            cb.button("🗑️", key=f"t_{notif_id}", on_click=update_notification_status,
                      args=(notif_id, 'trash'), width='stretch')
        elif status == 'done':
            st.button("🗑️", key=f"td_{notif_id}", on_click=update_notification_status,
                      args=(notif_id, 'trash'), width='stretch')
        elif status == 'trash':
            st.button("♻️", key=f"r_{notif_id}", on_click=restore_notification,
                      args=(notif_id,), width='stretch')


def _clear_trash() -> None:
    """Kosongkan semua item yang berstatus trash dari session_state."""
    to_delete = [k for k, v in st.session_state.notification_states.items() if v == 'trash']
    for k in to_delete:
        del st.session_state.notification_states[k]
    st.toast("🗑️ Sampah berhasil dikosongkan!")
    st.rerun()


# ---------------------------------------------------------------------------
# Entry point (dialog)
# ---------------------------------------------------------------------------

@st.dialog("🔔 Pusat Notifikasi")
def show_notification_dialog() -> None:
    """Dialog panel notifikasi — dipanggil dari main.py."""
    _ensure_state()

    all_items = _build_notification_items(st.session_state.user_role)

    # Kategorikan item berdasarkan state
    views: dict[str, list] = {'inbox': [], 'done': [], 'trash': []}
    for item in all_items:
        state = st.session_state.notification_states.get(item['id'], 'inbox')
        views[state].append(item)

    tab_labels = [
        f"📬 Masuk ({len(views['inbox'])})",
        f"✅ Selesai ({len(views['done'])})",
        f"🗑️ Sampah ({len(views['trash'])})",
    ]
    tabs = st.tabs(tab_labels)

    for tab, state in zip(tabs, ['inbox', 'done', 'trash']):
        with tab:
            if not views[state]:
                msg = "✨ Semua sudah dibaca!" if state == 'inbox' else "Tidak ada item."
                st.caption(msg)
            else:
                for item in views[state]:
                    _render_item_card(item, state)

            if state == 'trash' and views['trash']:
                if st.button("🧹 Kosongkan Sampah", width='stretch', key="clear_trash"):
                    _clear_trash()
