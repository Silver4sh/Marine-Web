"""
views/admin.py
==============
UI layer untuk Panel Admin.

Tanggung jawab:
  - Manajemen pengguna (tambah / edit / hapus)
  - Ganti kata sandi untuk akun sendiri
  - Log audit sistem

Semua operasi DB dipanggil melalui fungsi di core — tidak ada query langsung di sini.
"""
import streamlit as st

from core import (
    get_all_users, create_new_user, update_user_status,
    update_user_role, delete_user, update_password, get_logs,
)
from core.config import ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE

_ALL_ROLES = [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE]


# ---------------------------------------------------------------------------
# Dialogs (private — hanya dipanggil dari render_user_management_tab)
# ---------------------------------------------------------------------------

@st.dialog("Tambah Pengguna Baru")
def _add_user_dialog() -> None:
    with st.form("add_user_form"):
        new_user = st.text_input("Username (ID)")
        new_pass = st.text_input("Kata Sandi", type="password")
        new_role = st.selectbox("Peran", _ALL_ROLES)

        if st.form_submit_button("✅ Buat Pengguna", type="primary"):
            if not new_user or not new_pass:
                st.warning("Harap isi semua kolom.")
                return
            success, msg = create_new_user(new_user, new_pass, new_role)
            if success:
                st.success(msg)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(msg)


@st.dialog("Edit Pengguna")
def _edit_user_dialog(user_row) -> None:
    st.write(f"Mengedit: **{user_row['username']}**")

    current_role   = user_row['role']
    current_status = user_row['user_status']
    role_idx       = _ALL_ROLES.index(current_role) if current_role in _ALL_ROLES else 0

    c1, c2 = st.columns(2)
    with c1:
        new_role = st.selectbox("Peran", _ALL_ROLES, index=role_idx)
    with c2:
        new_status = st.radio("Status", ["Active", "Inactive"],
                              index=0 if current_status == "Active" else 1,
                              horizontal=True)

    if st.button("💾 Simpan Perubahan", type="primary"):
        if new_role != current_role:
            update_user_role(user_row['username'], new_role)
        if new_status != current_status:
            update_user_status(user_row['username'], new_status)
        st.success("Pengguna berhasil diperbarui!")
        st.cache_data.clear()
        st.rerun()


@st.dialog("Hapus Pengguna")
def _delete_user_dialog(username: str) -> None:
    st.warning(f"Apakah Anda yakin ingin menghapus pengguna **{username}**?")
    st.write("Tindakan ini **tidak dapat dibatalkan**.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Ya, Hapus", type="primary", width='stretch'):
            if delete_user(username):
                st.success(f"Pengguna {username} dihapus.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Gagal menghapus pengguna.")
    with c2:
        if st.button("Batal", width='stretch'):
            st.rerun()


# ---------------------------------------------------------------------------
# Tab renderers (private)
# ---------------------------------------------------------------------------

def _render_user_management() -> None:
    """Tab: Manajemen Pengguna."""
    st.caption("Kelola akses dan peran sistem.")

    users_df = get_all_users()

    col_head, col_btn = st.columns([6, 2])
    with col_btn:
        if st.button("➕ Tambah Pengguna", width='stretch'):
            _add_user_dialog()

    if users_df.empty:
        st.info("Tidak ada pengguna ditemukan.")
        return

    st.dataframe(
        users_df[['username', 'role', 'user_status', 'last_login']],
        width='stretch',
        column_config={
            "username":    "ID Pengguna",
            "user_status": st.column_config.Column("Status", width="small"),
            "last_login":  st.column_config.DatetimeColumn("Terakhir Login", format="D MMM, HH:mm"),
        },
    )

    st.markdown("### 🛠️ Tindakan")
    c_sel, c_edit, c_del = st.columns([3, 1, 1])

    with c_sel:
        selected = st.selectbox("Pilih Pengguna:", users_df['username'].tolist())

    if not selected:
        return

    user_row = users_df[users_df['username'] == selected].iloc[0]

    with c_edit:
        st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("✏️ Edit", width='stretch'):
            _edit_user_dialog(user_row)

    with c_del:
        st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Hapus", type="primary", width='stretch'):
            if selected == st.session_state.username:
                st.error("Tidak dapat menghapus akun yang sedang digunakan!")
            else:
                _delete_user_dialog(selected)


def _render_account_settings() -> None:
    """Tab: Pengaturan Akun (ganti password)."""
    st.warning("⚠️ Zona Keamanan — Perubahan kata sandi berlaku segera.")

    c_pass  = st.text_input("Kata Sandi Saat Ini",        type="password")
    n_pass  = st.text_input("Kata Sandi Baru",             type="password")
    cn_pass = st.text_input("Konfirmasi Kata Sandi Baru",  type="password")

    if st.button("🔒 Perbarui Kredensial", type="primary"):
        if n_pass != cn_pass:
            st.error("Kata sandi baru dan konfirmasi tidak cocok.")
            return
        success, msg = update_password(st.session_state.username, c_pass, n_pass)
        if success:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")


def _render_audit_log() -> None:
    """Tab: Log Audit Sistem."""
    st.write("Entri terbaru dari Log Audit Sistem")
    df = get_logs()
    if df.empty:
        st.info("Tidak ada log audit ditemukan.")
        return
    st.dataframe(
        df, hide_index=True, width='stretch',
        column_config={
            "changed_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, HH:mm"),
        },
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_admin_page() -> None:
    """Entry point halaman Admin — dipanggil dari main.py."""
    st.markdown("## 👨‍💼 Panel Admin")

    tab1, tab2, tab3 = st.tabs(["👥 Manajemen Pengguna", "🔑 Pengaturan Akun", "📋 Log Audit"])

    with tab1:
        _render_user_management()
    with tab2:
        _render_account_settings()
    with tab3:
        _render_audit_log()
