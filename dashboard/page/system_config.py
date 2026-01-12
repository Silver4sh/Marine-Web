import streamlit as st
from back.query.queries import get_system_settings, update_system_setting

def render_system_config_page():
    st.markdown("## 🔧 System Configuration")
    st.caption("Global application settings. Changes affect all users immediately.")
    
    settings = get_system_settings()
    
    if not settings:
        st.warning("Could not load settings. Database might be initializing...")
        return

    # --- General Settings ---
    with st.container(border=True):
        st.markdown("### 🌍 General")
        
        # App Name
        curr_name = settings.get("app_name", "MarineOS")
        new_name = st.text_input("Application Name", value=curr_name)
        if new_name != curr_name:
            if st.button("Save Name"):
                update_system_setting("app_name", new_name)
                st.success("App Name Updated!")
                st.rerun()

        # Maintenance Mode
        curr_maint = settings.get("maintenance_mode", "false").lower() == "true"
        new_maint = st.toggle("Maintenance Mode", value=curr_maint, help="Show warning banner to non-admins?")
        if new_maint != curr_maint:
            update_system_setting("maintenance_mode", "true" if new_maint else "false")
            st.toast("Maintenance Mode Updated!")
            st.rerun()

    # --- Analytics Thresholds ---
    with st.container(border=True):
        st.markdown("### 📊 Analytics Targets")
        
        c1, c2 = st.columns(2)
        
        with c1:
            # Revenue Target
            curr_target = float(settings.get("revenue_target_monthly", 5000000000))
            new_target = st.number_input("Monthly Revenue Target (IDR)", value=curr_target, step=100000000.0)
            if new_target != curr_target:
                if st.button("Update Target"):
                    update_system_setting("revenue_target_monthly", str(new_target))
                    st.success("Target Updated!")
                    st.rerun()
                    
        with c2:
            # Churn Risk Threshold
            curr_churn = int(settings.get("churn_risk_threshold", 3))
            new_churn = st.number_input("High Risk Client Threshold (Alert)", value=curr_churn, min_value=1)
            if new_churn != curr_churn:
                if st.button("Update Churn Threshold"):
                    update_system_setting("churn_risk_threshold", str(new_churn))
                    st.success("Threshold Updated!")
                    st.rerun()

    # --- UI Preferences ---
    with st.container(border=True):
        st.markdown("### 🎨 Appearance")
        curr_color = settings.get("theme_color", "#0ea5e9")
        new_color = st.color_picker("Primary Accent Color", value=curr_color)
        
        if new_color != curr_color:
            if st.button("Save Color"):
                update_system_setting("theme_color", new_color)
                st.success("Theme Color Updated! (Refresh to see changes)")
                st.rerun()
