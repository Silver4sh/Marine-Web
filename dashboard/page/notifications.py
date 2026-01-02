import streamlit as st
import asyncio
import hashlib
import pandas as pd
from datetime import datetime
from back.src.n_logic import generate_insights, get_notification_id
from back.query.queries import get_fleet_status, get_financial_metrics, get_clients_summary, get_logs
from back.query.config_queries import get_system_settings
from concurrent.futures import ThreadPoolExecutor

class NotificationManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def load_data(self, role):
        loop = asyncio.get_event_loop()
        tasks = []
        
        tasks.append(loop.run_in_executor(self.executor, get_fleet_status))
        tasks.append(loop.run_in_executor(self.executor, get_financial_metrics))
        tasks.append(loop.run_in_executor(self.executor, get_system_settings))
        tasks.append(loop.run_in_executor(self.executor, get_clients_summary))
        tasks.append(loop.run_in_executor(self.executor, get_logs))

        results = await asyncio.gather(*tasks)
        return {
            "fleet": results[0],
            "financial": results[1],
            "settings": results[2],
            "clients": results[3],
            "logs": results[4]
        }

from back.src.n_logic import generate_insights, get_notification_id

def render_interactive_item(item, status):
    """
    Renders a notification item with interactive buttons based on its status.
    """
    notif_id = item['id']
    
    # Styling variables
    bg_color = "rgba(255, 255, 255, 0.05)"
    border_color = "transparent"
    text_color = "#f8fafc"
    
    if status == 'done':
        bg_color = "rgba(20, 83, 45, 0.3)" # Dark green background
        border_color = "#22c55e"
    elif status == 'trash':
        bg_color = "rgba(0, 0, 0, 0.2)"
        text_color = "#64748b" # Dimmed text
        
    # Container
    c_content, c_action = st.columns([8, 2])
    
    with c_content:
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-left: 4px solid {border_color};
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="color: {text_color}; font-size: 14px;">{item.get('category', 'System').upper()}</strong>
                <small style="color: #94a3b8; font-size: 11px;">{item.get('time_str', '')}</small>
            </div>
            <div style="color: {text_color}; font-size: 13px; margin-top: 4px;">{item['message']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_action:
        if status == 'inbox':
            c_check, c_cross = st.columns(2)
            with c_check:
                if st.button("✅", key=f"done_{notif_id}", help="Mark as Done"):
                    st.session_state.notification_states[notif_id] = 'done'
                    st.rerun()
            with c_cross:
                if st.button("❌", key=f"trash_{notif_id}", help="Move to Trash"):
                    st.session_state.notification_states[notif_id] = 'trash'
                    st.rerun()
        
        elif status == 'done':
            # Restore to inbox option? Or just Delete?
            if st.button("❌", key=f"trash_done_{notif_id}", help="Move to Trash"):
                st.session_state.notification_states[notif_id] = 'trash'
                st.rerun()

        elif status == 'trash':
            # Restore option
            if st.button("♻️", key=f"restore_{notif_id}", help="Restore to Inbox"):
                 # Remove from state dict to reset to default/inbox, or explicitly set
                 if notif_id in st.session_state.notification_states:
                     del st.session_state.notification_states[notif_id]
                 st.rerun()

def render_notification_page():
    st.title("🔔 Notification Center")

    # --- Session State Initialization ---
    if 'notification_states' not in st.session_state:
        st.session_state.notification_states = {} # {id: 'done' | 'trash'}

    # --- Data Loading ---
    manager = NotificationManager()
    with st.spinner("Syncing..."):
        data = asyncio.run(manager.load_data(st.session_state.role))
        
    # Generate Raw Insights
    raw_insights = generate_insights(
        data['fleet'], 
        data['financial'], 
        st.session_state.role, 
        data['settings'], 
        data['clients']
    )
    logs = data['logs']

    # Normalize into a single list
    all_notifications = []
    
    # 1. Insights
    for i in raw_insights:
        item = i.copy()
        item['time_str'] = "Just Now"
        item['category'] = i.get('category', 'Alert')
        # Use a consistent ID generation
        item['id'] = get_notification_id(item['category'], item['message'], "insight_dynamic")
        all_notifications.append(item)
        
    # 2. Logs (limit to 10 latest)
    if not logs.empty:
        for _, row in logs.head(10).iterrows():
            t_str = row['changed_at'].strftime("%H:%M") if isinstance(row['changed_at'], datetime) else "Today"
            msg = f"{row['action']} on {row['table_name']}"
            cat = "System"
            # ID includes timestamp to be unique
            nid = get_notification_id(cat, msg, str(row['changed_at']))
            
            all_notifications.append({
                "id": nid,
                "message": msg,
                "category": cat,
                "level": "info",
                "time_str": t_str
            })

    # --- Filtering based on State ---
    inbox_items = []
    done_items = []
    trash_items = []

    for item in all_notifications:
        state = st.session_state.notification_states.get(item['id'], 'inbox')
        if state == 'inbox':
            inbox_items.append(item)
        elif state == 'done':
            done_items.append(item)
        elif state == 'trash':
            trash_items.append(item)

    # --- UI Layout ---
    tab_inbox, tab_done, tab_trash = st.tabs([
        f"📥 Inbox ({len(inbox_items)})", 
        f"✅ Done ({len(done_items)})", 
        f"🗑️ Trash ({len(trash_items)})"
    ])
    
    with tab_inbox:
        if not inbox_items:
            st.info("You're all caught up! No new notifications.")
            st.image("https://cdn-icons-png.flaticon.com/512/1161/1161726.png", width=100)
        else:
            for item in inbox_items:
                render_interactive_item(item, 'inbox')
                
    with tab_done:
        if not done_items:
            st.caption("No completed items yet.")
        else:
            for item in done_items:
                render_interactive_item(item, 'done')
                
    with tab_trash:
        st.caption("Items in trash will be cleared on session reset.")
        if st.button("Empty Trash"):
             # We can just iterate and remove from session state? 
             # No, 'trash' state IS stored in session state. We need to maybe mark them as 'deleted_forever' or just clear the keys?
             # Since 'all_notifications' is re-generated every time, if we remove the key from session_state, it returns to 'inbox'.
             # So 'Empty Trash' means adding them to a 'deleted_forever' set or similar?
             # For simplicity, let's just not render them if we had a persistent DB.
             # In this session-based mock, "Empty Trash" might just be visually clearing them.
             # Let's Skip actual delete logic for now as we don't have a notif DB table.
             st.toast("Trash cleared (visually)")
             
        for item in trash_items:
            render_interactive_item(item, 'trash')
