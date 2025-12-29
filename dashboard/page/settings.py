import streamlit as st
from back.query.update import update_password

def render_settings_page():
    st.markdown("## ⚙️ Account Settings")
    with st.container():
        st.warning("⚠️ Security Zone")
        u = st.session_state.username
        c_pass = st.text_input("Current Password", type="password")
        n_pass = st.text_input("New Password", type="password")
        cn_pass = st.text_input("Confirm Password", type="password")
        
        if st.button("Update Credential"):
            if n_pass != cn_pass:
                st.error("passwords do not match")
            else:
                success, msg = update_password(u, c_pass, n_pass)
                if success: st.success(msg)
                else: st.error(msg)
