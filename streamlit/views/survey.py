"""
views/survey.py
===============
UI layer untuk halaman Laporan Survei Harian.

Tanggung jawab:
  - Daftar survey dengan search
  - Form buat laporan baru

Backend data loading (sites, vessels, users) di-cache — tidak query ulang tiap submit.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from core.database import (
    get_all_surveys,
    create_survey_report,
    run_query,
)


# ---------------------------------------------------------------------------
# Data loaders (cached — tidak di-query ulang setiap render)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def _load_sites() -> pd.DataFrame:
    """Ambil daftar site aktif untuk dropdown form."""
    return run_query(
        "SELECT code_site, code_site || ' - ' || location AS label "
        "FROM operation.sites WHERE status = 'Active'"
    )


@st.cache_data(ttl=300, show_spinner=False)
def _load_vessels() -> pd.DataFrame:
    """Ambil daftar kapal aktif untuk dropdown form."""
    return run_query(
        "SELECT code_vessel, name FROM operation.vessels WHERE status = 'Active'"
    )


# ---------------------------------------------------------------------------
# Tab renderers (private)
# ---------------------------------------------------------------------------

def _render_survey_list() -> None:
    """Tab 1: Daftar semua laporan survei."""
    df = get_all_surveys()
    if df.empty:
        st.info("Belum ada laporan survei.")
        return

    search = st.text_input("🔍 Cari Laporan (Proyek, Kode, Kapal):", "")
    if search:
        mask = (
            df['project_name'].str.contains(search, case=False, na=False)
            | df['code_report'].str.contains(search, case=False, na=False)
            | df['vessel_name'].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "date_survey":    st.column_config.DatetimeColumn("Tanggal",  format="D MMM YYYY"),
            "project_name":   "Proyek",
            "code_report":    "Kode",
            "site_name":      "Site",
            "vessel_name":    "Kapal",
            "surveyor_name":  "Surveyor",
            "comment":        "Komentar",
        },
    )


def _render_create_form() -> None:
    """Tab 2: Form pembuatan laporan survei baru."""
    st.subheader("Buat Laporan Baru")

    sites_df   = _load_sites()
    vessels_df = _load_vessels()

    site_codes    = sites_df['code_site'].tolist()    if not sites_df.empty   else []
    site_labels   = sites_df['label'].tolist()        if not sites_df.empty   else []
    vessel_codes  = vessels_df['code_vessel'].tolist() if not vessels_df.empty else []
    vessel_labels = vessels_df['name'].tolist()        if not vessels_df.empty else []

    def _site_label(code):
        return site_labels[site_codes.index(code)] if code in site_codes else code

    def _vessel_label(code):
        return vessel_labels[vessel_codes.index(code)] if code in vessel_codes else code

    with st.form("create_survey_form"):
        c1, c2 = st.columns(2)

        with c1:
            project_name = st.text_input("Nama Proyek *")
            code_report  = st.text_input("Kode Laporan (Unik) *",
                                          help="Contoh: SRV-2025-001")
            id_site = st.selectbox(
                "Site",
                options=site_codes,
                format_func=_site_label,
            ) if site_codes else st.text_input("Site (tidak ada data)")

            id_vessel = st.selectbox(
                "Kapal",
                options=vessel_codes,
                format_func=_vessel_label,
            ) if vessel_codes else st.text_input("Kapal (tidak ada data)")

        with c2:
            current_user = st.session_state.get('username', 'N/A')
            st.text_input("Surveyor (Anda)", value=current_user, disabled=True)
            date_survey = st.date_input("Tanggal Survei", datetime.now())
            comment     = st.text_area("Komentar / Catatan", height=120)

        if st.form_submit_button("💾 Simpan Laporan", type="primary", width='stretch'):
            if not project_name or not code_report:
                st.error("❌ Nama Proyek dan Kode Laporan wajib diisi.")
                return

            data = {
                "project_name": project_name,
                "code_report":  code_report,
                "id_site":      id_site,
                "id_vessel":    id_vessel,
                "id_user":      current_user,
                "date_survey":  date_survey,
                "comment":      comment,
            }
            success, msg = create_survey_report(data)
            if success:
                st.success(f"✅ {msg}")
                st.cache_data.clear()
            else:
                st.error(f"❌ Gagal: {msg}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_survey_page() -> None:
    """Entry point halaman Survey — dipanggil dari main.py."""
    st.title("📋 Laporan Survei Harian")

    tab1, tab2 = st.tabs(["📜 Daftar Laporan", "➕ Buat Laporan Baru"])
    with tab1:
        _render_survey_list()
    with tab2:
        _render_create_form()
