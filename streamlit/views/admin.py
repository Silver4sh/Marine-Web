import streamlit as st
import pandas as pd
from core import (
    get_all_users, create_new_user, update_user_status, update_user_role, delete_user,
    update_password, get_logs
)
from core.config import ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE


def _section_header(icon, title, subtitle=""):
    sub = f'<div style="font-size:0.78rem;color:#8ba3c0;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;margin-top:4px;">
            <span style="font-size:1.15rem;">{icon}</span>
            <div>
                <div style="font-family:'Outfit',sans-serif;font-size:0.95rem;font-weight:800;color:#f0f6ff;letter-spacing:-0.01em;">{title}</div>
                {sub}
            </div>
        </div>
    """, unsafe_allow_html=True)


def _init_admin_state():
    for key in ['admin_panel', 'admin_edit_user', 'admin_delete_user']:
        if key not in st.session_state:
            st.session_state[key] = None


# --- INLINE PANELS (replacing dialog) ---

def _render_add_user_panel():
    st.markdown("""
        <div style="background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.25);
                    border-radius:14px;padding:20px;margin-bottom:16px;">
            <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#f0f6ff;margin-bottom:14px;">
                ➕ Tambah Pengguna Baru
            </div>
    """, unsafe_allow_html=True)

    with st.form("add_user_form", clear_on_submit=True):
        new_user = st.text_input("Username (ID)")
        new_pass = st.text_input("Kata Sandi", type="password")
        new_role = st.selectbox("Peran", [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE])
        c1, c2 = st.columns(2)
        submitted = c1.form_submit_button("✅ Buat Pengguna", type="primary", use_container_width=True)
        cancelled = c2.form_submit_button("↩️ Batal", use_container_width=True)

        if submitted:
            if new_user and new_pass:
                success, msg = create_new_user(new_user, new_pass, new_role)
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.session_state.admin_panel = None
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Harap isi semua kolom.")
        if cancelled:
            st.session_state.admin_panel = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_edit_user_panel(user_row):
    st.markdown(f"""
        <div style="background:rgba(129,140,248,0.08);border:1px solid rgba(129,140,248,0.25);
                    border-radius:14px;padding:20px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
                <div style="width:36px;height:36px;border-radius:50%;
                    background:linear-gradient(135deg,#0ea5e9,#818cf8);
                    display:flex;align-items:center;justify-content:center;
                    font-weight:800;color:white;font-size:1.1rem;font-family:'Outfit',sans-serif;
                    flex-shrink:0;">{user_row['username'][0].upper()}</div>
                <div>
                    <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#f0f6ff;">{user_row['username']}</div>
                    <div style="font-size:0.78rem;color:#8ba3c0;">Edit akses dan peran</div>
                </div>
            </div>
    """, unsafe_allow_html=True)

    current_role   = user_row['role']
    current_status = user_row['user_status']
    roles = [ROLE_ADMIN, ROLE_OPERATIONS, ROLE_MARCOM, ROLE_FINANCE]

    col1, col2 = st.columns(2)
    with col1:
        new_role = st.selectbox("Peran", roles,
                                index=roles.index(current_role) if current_role in roles else 0)
    with col2:
        new_status = st.radio("Status", ["Active", "Inactive"],
                              index=0 if current_status == "Active" else 1,
                              horizontal=True)

    c1, c2 = st.columns(2)
    if c1.button("💾 Simpan", type="primary", use_container_width=True):
        if new_role   != current_role:   update_user_role(user_row['username'], new_role)
        if new_status != current_status: update_user_status(user_row['username'], new_status)
        st.success("✅ Pengguna berhasil diperbarui!")
        st.cache_data.clear()
        st.session_state.admin_panel = None
        st.rerun()
    if c2.button("↩️ Batal", use_container_width=True):
        st.session_state.admin_panel = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_delete_user_panel(username):
    st.markdown(f"""
        <div style="background:rgba(244,63,94,0.1);border:1px solid rgba(244,63,94,0.3);
                    border-radius:14px;padding:20px;margin-bottom:16px;text-align:center;">
            <div style="font-size:2rem;margin-bottom:8px;">⚠️</div>
            <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#f0f6ff;margin-bottom:4px;">
                Hapus Pengguna
            </div>
            <div style="color:#8ba3c0;font-size:0.88rem;">
                Anda akan menghapus <strong style="color:#f43f5e;">{username}</strong>.
                Tindakan ini tidak dapat dibatalkan.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Ya, Hapus", type="primary", use_container_width=True):
            if delete_user(username):
                st.success(f"Pengguna {username} berhasil dihapus.")
                st.cache_data.clear()
                st.session_state.admin_panel = None
                st.rerun()
            else:
                st.error("Gagal menghapus pengguna.")
    with col2:
        if st.button("↩️ Batal", use_container_width=True):
            st.session_state.admin_panel = None
            st.rerun()


# --- SUB-PAGES ---

def render_user_management_tab():
    _init_admin_state()
    st.caption("Kelola akses, peran, dan status akun sistem.")
    users_df = get_all_users()

    col_head1, col_head2 = st.columns([6, 2])
    with col_head2:
        if st.button("➕ Tambah Pengguna", use_container_width=True, type="primary"):
            st.session_state.admin_panel = 'add'

    # Inline panels
    if st.session_state.get('admin_panel') == 'add':
        _render_add_user_panel()
    elif st.session_state.get('admin_panel') == 'edit' and st.session_state.get('admin_edit_user') is not None:
        _render_edit_user_panel(st.session_state.admin_edit_user)
    elif st.session_state.get('admin_panel') == 'delete' and st.session_state.get('admin_delete_user') is not None:
        _render_delete_user_panel(st.session_state.admin_delete_user)

    if not users_df.empty:
        st.dataframe(
            users_df[['username', 'role', 'user_status', 'last_login']],
            use_container_width=True,
            column_config={
                "username":    "ID Pengguna",
                "user_status": st.column_config.Column("Status", width="small"),
                "last_login":  st.column_config.DatetimeColumn("Terakhir Login", format="D MMM, HH:mm")
            }
        )

        st.divider()
        _section_header("🛠️", "Tindakan Pengguna")

        c_sel, c_btn1, c_btn2 = st.columns([3, 1, 1])
        with c_sel:
            selected_user = st.selectbox("Pilih Pengguna:", users_df['username'].tolist(),
                                         label_visibility="collapsed")

        if selected_user:
            user_row = users_df[users_df['username'] == selected_user].iloc[0]
            with c_btn1:
                if st.button("✏️ Edit", use_container_width=True):
                    st.session_state.admin_panel = 'edit'
                    st.session_state.admin_edit_user = user_row
                    st.rerun()
            with c_btn2:
                if st.button("🗑️ Hapus", type="primary", use_container_width=True):
                    if selected_user == st.session_state.username:
                        st.error("❌ Tidak dapat menghapus akun sendiri!")
                    else:
                        st.session_state.admin_panel = 'delete'
                        st.session_state.admin_delete_user = selected_user
                        st.rerun()
    else:
        st.info("Tidak ada pengguna ditemukan.")


def render_settings_tab():
    _section_header("🔐", "Keamanan Akun", "Ubah kata sandi akun Anda")

    st.markdown("""
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);
                    border-radius:12px;padding:12px 16px;margin-bottom:18px;
                    display:flex;gap:10px;align-items:center;">
            <span style="font-size:1.2rem;">⚠️</span>
            <div style="font-size:0.85rem;color:#f0f6ff;">Zona Keamanan — Pastikan gunakan kata sandi yang kuat.</div>
        </div>
    """, unsafe_allow_html=True)

    u       = st.session_state.username
    c_pass  = st.text_input("Kata Sandi Saat Ini",       type="password", placeholder="••••••••")
    n_pass  = st.text_input("Kata Sandi Baru",            type="password", placeholder="Minimal 6 karakter")
    cn_pass = st.text_input("Konfirmasi Kata Sandi Baru", type="password", placeholder="Ulangi kata sandi baru")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Perbarui Kredensial", type="primary", use_container_width=True):
        if n_pass != cn_pass:
            st.error("❌ Kata sandi baru tidak cocok.")
        elif len(n_pass) < 6:
            st.warning("⚠️ Kata sandi minimal 6 karakter.")
        else:
            success, msg = update_password(u, c_pass, n_pass)
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")


def render_audit_tab():
    _section_header("📜", "Log Audit", "Rekam jejak aktivitas sistem terkini")
    df = get_logs()
    if not df.empty:
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "changed_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, HH:mm")
            }
        )
    else:
        st.info("Tidak ada log audit ditemukan.")


def render_admin_page():
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">👨‍💼</div>
            <div>
                <p class="page-header-title">Panel Admin</p>
                <p class="page-header-subtitle">User management, security &amp; audit logs</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👤 Manajemen Pengguna", "🔐 Pengaturan Akun", "📜 Log Audit"])

    with tab1: render_user_management_tab()
    with tab2: render_settings_tab()
    with tab3: render_audit_tab()
