import streamlit as st
import pandas as pd
from back.query.user_queries import (
    get_all_users, 
    create_new_user, 
    update_user_status, 
    update_user_role, 
    delete_user
)
from back.src.constants import ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE

def render_user_management_page():
    st.markdown("## 👨‍💼 User Management")
    st.caption("Manage system access and roles.")

    # --- 1. User List & Actions ---
    users_df = get_all_users()
    
    # "Add User" Expander
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form"):
            c1, c2, c3 = st.columns(3)
            new_user = c1.text_input("Username (ID)")
            new_pass = c2.text_input("Password", type="password")
            new_role = c3.selectbox("Role", [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE])
            
            submitted = st.form_submit_button("Create User")
            if submitted:
                if new_user and new_pass:
                    success, msg = create_new_user(new_user, new_pass, new_role)
                    if success:
                        st.balloons()
                        st.success(msg)
                        st.cache_data.clear() # Clear cache to refresh list
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill all fields.")

    st.markdown("---")
    
    # --- 2. Data Table with Actions ---
    if not users_df.empty:
        # Convert to editor for quick status updates? 
        # Or better: Simple table + Action buttons per row (more control)
        
        # Display as a clean dataframe first
        st.dataframe(
            users_df[['username', 'role', 'user_status', 'last_login']],
            use_container_width=True,
            column_config={
                "username": "User ID",
                "user_status": st.column_config.Column("Status", width="small"),
                "last_login": st.column_config.DatetimeColumn("Last Login", format="D MMM, HH:mm")
            }
        )
        
        st.markdown("### 🛠️ Actions")
        
        # Selection for Edit/Delete
        c_sel, c_act = st.columns([1, 3])
        
        with c_sel:
            selected_user = st.selectbox("Select User to Edit:", users_df['username'].tolist())
            
        if selected_user:
            user_row = users_df[users_df['username'] == selected_user].iloc[0]
            
            with st.container(border=True):
                st.markdown(f"**Managing: `{selected_user}`**")
                
                c1, c2, c3 = st.columns(3)
                
                # Edit Role
                with c1:
                    current_role = user_row['role']
                    new_role_val = st.selectbox("Change Role", [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE], 
                                              index=[ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE].index(current_role) if current_role in [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE] else 0)
                    if st.button("Update Role"):
                        if update_user_role(selected_user, new_role_val):
                            st.success("Role updated!")
                            st.cache_data.clear()
                            st.rerun()
                            
                # Edit Status
                with c2:
                    current_status = user_row['user_status']
                    new_status_val = st.radio("Account Status", ["Active", "Inactive"], horizontal=True, 
                                            index=0 if current_status == "Active" else 1)
                    if st.button("Update Status"):
                         if update_user_status(selected_user, new_status_val):
                            st.success("Status updated!")
                            st.cache_data.clear()
                            st.rerun()

                # Delete
                with c3:
                    st.write("")
                    st.write("") # Spacer
                    if st.button("🗑️ Delete User", type="primary"):
                        if selected_user == st.session_state.username:
                            st.error("You cannot delete yourself!")
                        else:
                            if delete_user(selected_user):
                                st.success(f"User {selected_user} deleted.")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Failed to delete.")

    else:
        st.info("No users found.")
