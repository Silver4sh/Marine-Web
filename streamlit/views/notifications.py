import streamlit as st
import datetime
from core import (
    get_fleet_status, get_financial_metrics, get_system_settings,
    get_clients_summary, get_logs, get_notification_id, generate_insights
)


@st.cache_data(ttl=60, show_spinner=False)
def load_notification_data(role):
    return {
        "fleet":     get_fleet_status(),
        "financial": get_financial_metrics(),
        "settings":  get_system_settings(),
        "clients":   get_clients_summary(),
        "logs":      get_logs()
    }


def count_unread_notifications(role):
    """Returns count of inbox (unread) notifications for badge display."""
    try:
        data = load_notification_data(role)
        raw = generate_insights(
            data['fleet'], data['financial'], role, data['settings'], data['clients']
        )
        if 'notification_states' not in st.session_state:
            return len(raw)
        unread = sum(
            1 for i in raw
            if st.session_state.notification_states.get(
                get_notification_id(i.get('category', 'Alert'), i['message'], "dynamic"), 'inbox'
            ) == 'inbox'
        )
        return unread
    except Exception:
        return 0


def update_notification_status(notif_id, new_status):
    st.session_state.notification_states[notif_id] = new_status


def restore_notification(notif_id):
    if notif_id in st.session_state.notification_states:
        del st.session_state.notification_states[notif_id]


def render_notification_item(item, status):
    notif_id = item['id']
    icons = {"FLEET": "🚢", "FINANCIAL": "💰", "SYSTEM": "🖥️", "CLIENTS": "👥", "ALERT": "⚠️"}
    category = item.get('category', 'ALERT').upper()
    cat_ind = {"FLEET": "ARMADA", "FINANCIAL": "KEUANGAN", "SYSTEM": "SISTEM",
               "CLIENTS": "KLIEN", "ALERT": "PERINGATAN"}
    cat_display = cat_ind.get(category, category)
    icon = icons.get(category, "🔔")

    styles = {
        'inbox': {'bg': 'rgba(255,255,255,0.04)', 'border': 'rgba(14,165,233,0.3)',  'text': '#f0f6ff', 'dot': True},
        'done':  {'bg': 'rgba(34,197,94,0.1)',    'border': 'rgba(34,197,94,0.4)',   'text': '#f0fdf4', 'dot': False},
        'trash': {'bg': 'rgba(0,0,0,0.15)',       'border': 'transparent',           'text': '#4a6080', 'dot': False},
    }
    style = styles.get(status, styles['inbox'])
    dot_html = '<span style="width:7px;height:7px;background:#0ea5e9;border-radius:50%;display:inline-block;margin-right:8px;box-shadow:0 0 6px #0ea5e9;flex-shrink:0;"></span>' if style['dot'] else ''

    col_content, col_btns = st.columns([0.84, 0.16] if status == 'inbox' else [0.90, 0.10])

    with col_content:
        st.markdown(f"""
            <div style="
                background: {style['bg']};
                border: 1px solid {style['border']};
                border-radius: 12px;
                padding: 12px 16px;
                margin-bottom: 6px;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div style="display:flex; align-items:center;">
                        {dot_html}
                        <span style="font-size:15px; margin-right:7px;">{icon}</span>
                        <strong style="color:{style['text']}; font-size:0.83rem; font-family:'Outfit',sans-serif; letter-spacing:0.04em;">{cat_display}</strong>
                    </div>
                    <small style="color:#4a6080; font-size:0.72rem;">{item.get('time_str', '')}</small>
                </div>
                <div style="color:{style['text']}; font-size:0.83rem; line-height:1.5; opacity:0.88;">{item['message']}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_btns:
        st.write("")
        if status == 'inbox':
            ca, cb = st.columns(2)
            ca.button("✅", key=f"d_{notif_id}",  on_click=update_notification_status,
                      args=(notif_id, 'done'),  use_container_width=True)
            cb.button("🗑️", key=f"t_{notif_id}", on_click=update_notification_status,
                      args=(notif_id, 'trash'), use_container_width=True)
        elif status == 'done':
            st.button("🗑️", key=f"td_{notif_id}", on_click=update_notification_status,
                      args=(notif_id, 'trash'), use_container_width=True)
        elif status == 'trash':
            st.button("♻️", key=f"r_{notif_id}", on_click=restore_notification,
                      args=(notif_id,), use_container_width=True)


def show_notification_dialog():
    """Renders the notification panel inline (no dialog decorator needed)."""
    if 'notification_states' not in st.session_state:
        st.session_state.notification_states = {}

    data = load_notification_data(st.session_state.user_role)
    raw = generate_insights(
        data['fleet'], data['financial'], st.session_state.user_role,
        data['settings'], data['clients']
    )

    all_items = []
    for i in raw:
        i['id'] = get_notification_id(i.get('category', 'Alert'), i['message'], "dynamic")
        i['time_str'] = "Baru Saja"
        all_items.append(i)

    logs = data['logs']
    if not logs.empty:
        for _, row in logs.head(10).iterrows():
            ts = row['changed_at']
            if isinstance(ts, str):
                ts = datetime.datetime.now()
            msg = f"{row['action']} pada {row['table_name']}"
            all_items.append({
                "id": get_notification_id("System", msg, str(ts)),
                "category": "System",
                "message": msg,
                "time_str": ts.strftime("%H:%M") if hasattr(ts, 'strftime') else "Hari Ini",
                "level": "info"
            })

    views = {'inbox': [], 'done': [], 'trash': []}
    for item in all_items:
        state = st.session_state.notification_states.get(item['id'], 'inbox')
        views[state].append(item)

    # Header
    st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
            <span style="font-size:1.5rem;">🔔</span>
            <div style="font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:800;color:#f0f6ff;">Pusat Notifikasi</div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        f"📬 Masuk ({len(views['inbox'])})",
        f"✅ Selesai ({len(views['done'])})",
        f"🗑️ Sampah ({len(views['trash'])})"
    ])

    for tab, state in zip(tabs, ['inbox', 'done', 'trash']):
        with tab:
            if not views[state]:
                empty_msg = {
                    'inbox': "✨ Semua sudah dibaca!",
                    'done':  "Belum ada notifikasi yang diselesaikan.",
                    'trash': "Sampah kosong."
                }
                st.caption(empty_msg.get(state, "Tidak ada notifikasi."))
            else:
                for item in views[state]:
                    render_notification_item(item, state)

            if state == 'trash' and views['trash']:
                if st.button("🧹 Kosongkan Sampah", use_container_width=True, key="clear_trash"):
                    for item in views['trash']:
                        if item['id'] in st.session_state.notification_states:
                            del st.session_state.notification_states[item['id']]
                    st.toast("🗑️ Sampah berhasil dikosongkan!")
                    st.rerun()
