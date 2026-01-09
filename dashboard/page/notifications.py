import streamlit as st
import datetime
import textwrap
from back.src.n_logic import generate_insights, get_notification_id
from back.query.queries import get_fleet_status, get_financial_metrics, get_clients_summary, get_logs
from back.query.config_queries import get_system_settings

# --- Optimized Data Loading ---
@st.cache_data(ttl=60, show_spinner=False)
def load_notification_data(role):
    """
    Fetch all necessary data for notifications in one go.
    Cached for 60s to reduce DB load.
    """
    return {
        "fleet": get_fleet_status(),
        "financial": get_financial_metrics(),
        "settings": get_system_settings(),
        "clients": get_clients_summary(),
        "logs": get_logs()
    }

def update_notification_status(notif_id, new_status):
    st.session_state.notification_states[notif_id] = new_status

def restore_notification(notif_id):
    if notif_id in st.session_state.notification_states:
        del st.session_state.notification_states[notif_id]

def render_item(item, status):
    """
    Renders a clean, minimalist interactive notification card.
    """
    notif_id = item['id']
    
    # Category Icons
    icons = {
        "FLEET": "🚢",
        "FINANCIAL": "💰",
        "SYSTEM": "🖥️",
        "CLIENTS": "👥",
        "ALERT": "⚠️"
    }
    category = item.get('category', 'ALERT').upper()
    icon = icons.get(category, "🔔")

    # Styles mapped by status
    styles = {
        'inbox': {'bg': 'rgba(255, 255, 255, 0.05)', 'border': 'transparent', 'text': '#f8fafc', 'dot': True},
        'done':  {'bg': 'rgba(20, 83, 45, 0.2)', 'border': '#22c55e',      'text': '#f0fdf4', 'dot': False},
        'trash': {'bg': 'rgba(0, 0, 0, 0.2)',    'border': 'transparent',  'text': '#64748b', 'dot': False}
    }
    style = styles.get(status, styles['inbox'])
    
    # HTML Component
    dot_html = '<span style="height:8px;width:8px;background:#0ea5e9;border-radius:50%;display:inline-block;margin-right:8px;"></span>' if style['dot'] else ''
    
    # HTML Component (Flattened to ensure no Markdown Code Block issues)
    bg = style['bg']
    border = style['border']
    text_color = style['text']
    dot_margin = '26px' if style['dot'] else '6px'
    
    html_content = (
        f'<div style="background:{bg}; border-left:3px solid {border}; padding:12px; border-radius:6px; margin-bottom:8px; transition: all 0.2s;">'
        f'    <div style="display:flex; justify-content:space-between; align-items:center;">'
        f'        <div style="display:flex; align-items:center;">'
        f'            {dot_html}'
        f'            <span style="font-size:16px; margin-right:6px;">{icon}</span>'
        f'            <strong style="color:{text_color}; font-size:14px; letter-spacing: 0.5px;">{category}</strong>'
        f'        </div>'
        f'        <small style="color:#94a3b8; font-size:11px; font-family:monospace;">{item.get("time_str", "")}</small>'
        f'    </div>'
        f'    <div style="color:{text_color}; font-size:13px; margin-top:6px; padding-left:{dot_margin}; line-height: 1.4; opacity: 0.9;">'
        f'        {item["message"]}'
        f'    </div>'
        f'</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Actions
    c1, c2 = st.columns([0.8, 0.2])
    with c2:
        if status == 'inbox':
            ca, cb = st.columns(2)
            ca.button("✅", key=f"d_{notif_id}", help="Mark as Done", 
                      on_click=update_notification_status, args=(notif_id, 'done'), use_container_width=True)
            cb.button("🗑️", key=f"t_{notif_id}", help="Move to Trash", 
                      on_click=update_notification_status, args=(notif_id, 'trash'), use_container_width=True)
            
        elif status == 'done':
             st.button("🗑️", key=f"td_{notif_id}", help="Move to Trash", 
                       on_click=update_notification_status, args=(notif_id, 'trash'), use_container_width=True)

        elif status == 'trash':
             st.button("♻️", key=f"r_{notif_id}", help="Restore", 
                       on_click=restore_notification, args=(notif_id,), use_container_width=True)

@st.dialog("🔔 Notification Center")
def show_notification_dialog():
    if 'notification_states' not in st.session_state:
        st.session_state.notification_states = {}

    data = load_notification_data(st.session_state.user_role)
    
    # Logic Processing
    raw = generate_insights(data['fleet'], data['financial'], st.session_state.user_role, data['settings'], data['clients'])
    
    # Process & Deduplicate
    all_items = []
    
    # 1. Alerts
    for i in raw:
        i['id'] = get_notification_id(i.get('category', 'Alert'), i['message'], "dynamic")
        i['time_str'] = "Just Now"
        all_items.append(i)
        
    # 2. Logs
    logs = data['logs']
    if not logs.empty:
        for _, row in logs.head(10).iterrows():
            ts = row['changed_at']
            if isinstance(ts, str): ts = datetime.datetime.now() # Fallback
            
            msg = f"{row['action']} on {row['table_name']}"
            all_items.append({
                "id": get_notification_id("System", msg, str(ts)),
                "category": "System",
                "message": msg,
                "time_str": ts.strftime("%H:%M") if hasattr(ts, 'strftime') else "Today",
                "level": "info"
            })

    # Filtering
    views = {'inbox': [], 'done': [], 'trash': []}
    for item in all_items:
        state = st.session_state.notification_states.get(item['id'], 'inbox')
        views[state].append(item)

    # UI
    tabs = st.tabs([f"Inbox ({len(views['inbox'])})", f"Done ({len(views['done'])})", f"Trash ({len(views['trash'])})"])
    
    for tab, state in zip(tabs, ['inbox', 'done', 'trash']):
        with tab:
            if not views[state]:
                st.caption("No notifications here." if state != 'inbox' else "You're all caught up!")
            else:
                for item in views[state]:
                    render_item(item, state)
            
            if state == 'trash' and views['trash']:
                 if st.button("Empty Trash", use_container_width=True):
                     st.toast("Trash cleared")
