import streamlit as st
import pandas as pd
from streamlit.core import (
    ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE,
    get_all_users, create_new_user, update_user_status, update_user_role, delete_user,
    update_password, get_logs
)

# --- DIALOGS ---
@st.dialog("Tambah Pengguna Baru")
def add_user_dialog():
    with st.form("add_user_form"):
        new_user = st.text_input("Username (ID)")
        new_pass = st.text_input("Kata Sandi", type="password")
        new_role = st.selectbox("Peran", [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE])
        
        if st.form_submit_button("Buat Pengguna"):
            if new_user and new_pass:
                success, msg = create_new_user(new_user, new_pass, new_role)
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.rerun()
                else: st.error(msg)
            else: st.warning("Harap isi semua kolom.")

@st.dialog("Edit Pengguna")
def edit_user_dialog(user_row):
    st.write(f"Mengedit: **{user_row['username']}**")
    current_role = user_row['role']
    current_status = user_row['user_status']
    
    col1, col2 = st.columns(2)
    with col1:
        new_role = st.selectbox("Peran", [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE], 
                              index=[ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE].index(current_role) if current_role in [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE] else 0)
    with col2:
        new_status = st.radio("Status", ["Active", "Inactive"], index=0 if current_status == "Active" else 1, horizontal=True)
                            
    if st.button("Simpan Perubahan", type="primary"):
        if new_role != current_role: update_user_role(user_row['username'], new_role)
        if new_status != current_status: update_user_status(user_row['username'], new_status)
        st.success("Pengguna berhasil diperbarui!")
        st.cache_data.clear()
        st.rerun()

@st.dialog("Hapus Pengguna")
def delete_user_dialog(username):
    st.warning(f"Apakah Anda yakin ingin menghapus pengguna **{username}**?")
    st.write("Tindakan ini tidak dapat dibatalkan.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ya, Hapus", type="primary"):
            if delete_user(username):
                st.success(f"Pengguna {username} dihapus.")
                st.cache_data.clear()
                st.rerun()
            else: st.error("Gagal menghapus pengguna.")
    with col2:
        if st.button("Batal"): st.rerun()

# --- SUB-PAGES ---
def render_user_management_tab():
    st.caption("Kelola akses dan peran sistem.")
    users_df = get_all_users()
    
    col_head1, col_head2 = st.columns([6, 2])
    with col_head2:
        if st.button("➕ Tambah Pengguna", use_container_width=True): add_user_dialog()

    if not users_df.empty:
        st.dataframe(
            users_df[['username', 'role', 'user_status', 'last_login']],
            use_container_width=True,
            column_config={
                "username": "ID Pengguna",
                "user_status": st.column_config.Column("Status", width="small"),
                "last_login": st.column_config.DatetimeColumn("Terakhir Login", format="D MMM, HH:mm")
            }
        )
        
        st.markdown("### 🛠️ Tindakan")
        c_sel, c_btn1, c_btn2 = st.columns([2, 1, 1])
        with c_sel:
            selected_user = st.selectbox("Pilih Pengguna:", users_df['username'].tolist())
        
        if selected_user:
            user_row = users_df[users_df['username'] == selected_user].iloc[0]
            with c_btn1:
                st.write(""); st.write("")
                if st.button("✏️ Edit", use_container_width=True): edit_user_dialog(user_row)
            with c_btn2:
                st.write(""); st.write("")
                if st.button("🗑️ Hapus", type="primary", use_container_width=True):
                    if selected_user == st.session_state.username: st.error("Tidak dapat menghapus diri sendiri!")
                    else: delete_user_dialog(selected_user)
    else: st.info("Tidak ada pengguna ditemukan.")

def render_settings_tab():
    with st.container():
        st.warning("⚠️ Zona Keamanan")
        u = st.session_state.username
        c_pass = st.text_input("Kata Sandi Saat Ini", type="password")
        n_pass = st.text_input("Kata Sandi Baru", type="password")
        cn_pass = st.text_input("Konfirmasi Kata Sandi Baru", type="password")
        
        if st.button("Perbarui Kredensial"):
            if n_pass != cn_pass: st.error("Kata sandi tidak cocok")
            else:
                success, msg = update_password(u, c_pass, n_pass)
                if success: st.success(msg)
                else: st.error(msg)

def render_audit_tab():
    st.write("Entri terbaru dari Log Sistem")
    df = get_logs()
    if not df.empty:
        st.dataframe(df, hide_index=True, use_container_width=True, column_config={"created_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, HH:mm")})
    else: st.info("Tidak ada log audit ditemukan.")

def render_admin_page():
    st.markdown("## 👨‍💼 Panel Admin")
    
    tab1, tab2, tab3 = st.tabs(["Manajemen Pengguna", "Pengaturan Akun", "Log Audit"])
    
    with tab1: render_user_management_tab()
    with tab2: render_settings_tab()
    with tab3: render_audit_tab()
