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

@st.dialog("Add New User")
def add_user_dialog():
    with st.form("add_user_form"):
        new_user = st.text_input("Username (ID)")
        new_pass = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE])
        
        if st.form_submit_button("Create User"):
            if new_user and new_pass:
                success, msg = create_new_user(new_user, new_pass, new_role)
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please fill all fields.")

@st.dialog("Edit User")
def edit_user_dialog(user_row):
    st.write(f"Editing: **{user_row['username']}**")
    
    current_role = user_row['role']
    current_status = user_row['user_status']
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_role = st.selectbox("Role", 
                              [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE], 
                              index=[ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE].index(current_role) if current_role in [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE] else 0)
        
    with col2:
        new_status = st.radio("Status", ["Active", "Inactive"], 
                            index=0 if current_status == "Active" else 1,
                            horizontal=True)
                            
    if st.button("Save Changes", type="primary"):
        # Update Role
        if new_role != current_role:
            update_user_role(user_row['username'], new_role)
            
        # Update Status
        if new_status != current_status:
            update_user_status(user_row['username'], new_status)
            
        st.success("User updated successfully!")
        st.cache_data.clear()
        st.rerun()

@st.dialog("Delete User")
def delete_user_dialog(username):
    st.warning(f"Are you sure you want to delete user **{username}**?")
    st.write("This action cannot be undone.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete", type="primary"):
            if delete_user(username):
                st.success(f"User {username} deleted.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to delete user.")
    with col2:
        if st.button("Cancel"):
            st.rerun()

def render_user_management_page():
    st.markdown("## 👨‍💼 User Management")
    st.caption("Manage system access and roles.")

    # --- 1. User List & Actions ---
    users_df = get_all_users()
    
    # Header Actions
    col_head1, col_head2 = st.columns([6, 2])
    with col_head1:
        st.write("") # Spacer
    with col_head2:
        if st.button("➕ Add New User", use_container_width=True):
            add_user_dialog()

    st.markdown("---")
    
    # --- 2. Data Table with Actions ---
    if not users_df.empty:
        # Display as a clean dataframe
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
        c_sel, c_btn1, c_btn2 = st.columns([2, 1, 1])
        
        with c_sel:
            selected_user = st.selectbox("Select User to Manage:", users_df['username'].tolist())
            
        if selected_user:
            user_row = users_df[users_df['username'] == selected_user].iloc[0]
            
            with c_btn1:
                st.write("") # Align with selectbox
                st.write("")
                if st.button("✏️ Edit User", use_container_width=True):
                    edit_user_dialog(user_row)
                    
            with c_btn2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete User", type="primary", use_container_width=True):
                    if selected_user == st.session_state.username:
                        st.error("Cannot delete self!")
                    else:
                        delete_user_dialog(selected_user)

    else:
        st.info("No users found.")
