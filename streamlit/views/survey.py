
import streamlit as st
import pandas as pd
from datetime import datetime
from core.database import (
    get_all_surveys, 
    create_survey_report, 
    get_connection,
    run_query,
    get_engine
)
from sqlalchemy import text

def render_survey_page():
    st.title("📋 Laporan Survei Harian")
    
    tab1, tab2 = st.tabs(["📜 Daftar Laporan", "➕ Buat Laporan Baru"])
    
    with tab1:
        render_survey_list()
        
    with tab2:
        render_create_survey_form()

def render_survey_list():
    df = get_all_surveys()
    
    if df.empty:
        st.info("Belum ada laporan survei.")
        return

    # Search Filter
    search = st.text_input("Cari Laporan (Proyek, Kode, Kapal):", "")
    if search:
        mask = (
            df['project_name'].str.contains(search, case=False, na=False) |
            df['code_report'].str.contains(search, case=False, na=False) |
            df['vessel_name'].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    
    st.dataframe(
        df,
        column_config={
            "date_survey": st.column_config.DatetimeColumn("Tanggal", format="D MMM YYYY"),
            "project_name": "Proyek",
            "code_report": "Kode",
            "site_name": "Site",
            "vessel_name": "Kapal",
            "surveyor_name": "Surveyor",
            "comment": "Komentar"
        },
        use_container_width=True,
        hide_index=True
    )

def render_create_survey_form():
    st.subheader("Buat Laporan Baru")
    
    with st.form("create_survey_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Nama Proyek")
            # Generate Code Automatically based on date/sequence could be better, but manual for now
            code_report = st.text_input("Kode Laporan (Unik)", help="Contoh: SRV-2023-001")
            
            # Fetch options for dropdowns
            sites_df = run_query("SELECT code_site, code_site || ' - ' || location as label FROM operation.sites WHERE status = 'Active'")
            site_opts = sites_df['code_site'].tolist() if not sites_df.empty else []
            site_labels = sites_df['label'].tolist() if not sites_df.empty else []
            
            id_site = st.selectbox("Site", options=site_opts, format_func=lambda x: site_labels[site_opts.index(x)] if x in site_opts else x)
            
            vessels_df = run_query("SELECT code_vessel, name FROM operation.vessels WHERE status = 'Active'")
            vessel_opts = vessels_df['code_vessel'].tolist() if not vessels_df.empty else []
            vessel_labels = vessels_df['name'].tolist() if not vessels_df.empty else []
            
            id_vessel = st.selectbox("Kapal", options=vessel_opts, format_func=lambda x: vessel_labels[vessel_opts.index(x)] if x in vessel_opts else x)
            
        with col2:
            current_user = st.session_state.get('username', 'N/A')
            st.text_input("Surveyor (Anda)", value=current_user, disabled=True)
            
            # User ID needs to be fetched from username
            # For simplicity, we assume username = code_user or we act as admin
            # Ideally we fetch the user ID from session/database
            
            date_survey = st.date_input("Tanggal Survei", datetime.now())
            comment = st.text_area("Komentar / Catatan", height=100)

        submitted = st.form_submit_button("Simpan Laporan")
        
        if submitted:
            if not project_name or not code_report:
                st.error("Nama Proyek dan Kode Laporan wajib diisi.")
            else:
                # Prepare data
                data = {
                    "project_name": project_name,
                    "code_report": code_report,
                    "id_site": id_site,
                    "id_vessel": id_vessel,
                    "id_user": current_user, # Assuming code_user is username
                    "date_survey": date_survey,
                    "comment": comment
                }
                
                success, msg = create_survey_report(data)
                if success:
                    st.success(msg)
                    st.cache_data.clear() # Clear cache to refresh list
                    # Optional: Rerun to clear form
                else:
                    st.error(f"Gagal: {msg}")
