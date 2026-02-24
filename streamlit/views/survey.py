import streamlit as st
import pandas as pd
from datetime import datetime
from core.database import (
    get_all_surveys,
    create_survey_report,
    run_query,
)


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


def render_survey_list():
    df = get_all_surveys()

    if df.empty:
        st.info("Belum ada laporan survei yang dibuat.")
        return

    # Summary metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Laporan", len(df))
    if 'vessel_name' in df.columns:
        c2.metric("Kapal Berbeda", df['vessel_name'].nunique())
    if 'date_survey' in df.columns:
        try:
            latest = pd.to_datetime(df['date_survey']).max()
            c3.metric("Survei Terbaru", latest.strftime("%d %b %Y") if pd.notnull(latest) else "—")
        except Exception:
            pass

    st.divider()

    # Search Filter
    search = st.text_input("", placeholder="🔍  Cari laporan (proyek, kode, kapal)...",
                           label_visibility="collapsed")
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
            "date_survey":    st.column_config.DatetimeColumn("Tanggal", format="D MMM YYYY"),
            "project_name":   "Proyek",
            "code_report":    "Kode",
            "site_name":      "Site",
            "vessel_name":    "Kapal",
            "surveyor_name":  "Surveyor",
            "comment":        "Komentar"
        },
        width="stretch",
        hide_index=True
    )


def render_create_survey_form():
    tab1, tab2 = st.tabs(["Daftar Survey", "Buat Survey"])
    with tab1:
        _section_header("📜", "Daftar Survey", "Data survei harian")
        render_survey_list()

    with tab2:
        _section_header("✏️", "Buat Survey", "Isi data survei harian")
        with st.form("create_survey_form"):
            col1, col2 = st.columns(2)

            with col1:
                project_name = st.text_input("Nama Proyek", placeholder="Contoh: Survei Selat Malaka")

                # Auto-generate code report based on date + timestamp
                auto_code = f"SRV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                code_report = st.text_input(
                    "Kode Laporan",
                    value=auto_code,
                    help="Di-generate otomatis berdasarkan tanggal dan waktu. Bisa diubah jika diperlukan."
                )

                # Site dropdown
                sites_df = run_query(
                    "SELECT code_site, code_site || ' - ' || location as label "
                    "FROM operation.sites WHERE status = 'Active'"
                )
                site_opts   = sites_df['code_site'].tolist() if not sites_df.empty else []
                site_labels = sites_df['label'].tolist()    if not sites_df.empty else []
                id_site = st.selectbox(
                    "Site",
                    options=site_opts,
                    format_func=lambda x: site_labels[site_opts.index(x)] if x in site_opts else x
                )

                # Vessel dropdown
                vessels_df = run_query(
                    "SELECT code_vessel, name FROM operation.vessels WHERE status = 'Active'"
                )
                vessel_opts   = vessels_df['code_vessel'].tolist() if not vessels_df.empty else []
                vessel_labels = vessels_df['name'].tolist()        if not vessels_df.empty else []
                id_vessel = st.selectbox(
                    "Kapal",
                    options=vessel_opts,
                    format_func=lambda x: vessel_labels[vessel_opts.index(x)] if x in vessel_opts else x
                )

            with col2:
                current_user = st.session_state.get('username', 'N/A')
                st.text_input("Surveyor (Anda)", value=current_user, disabled=True)
                date_survey = st.date_input("Tanggal Survei", datetime.now())
                comment = st.text_area("Komentar / Catatan", placeholder="Catatan kondisi lapangan, temuan, dll...", height=120)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("💾 Simpan Laporan", type="primary", width="stretch")

            if submitted:
                if not project_name or not code_report:
                    st.error("❌ Nama Proyek dan Kode Laporan wajib diisi.")
                else:
                    data = {
                        "project_name": project_name,
                        "code_report":  code_report,
                        "id_site":      id_site,
                        "id_vessel":    id_vessel,
                        "id_user":      current_user,
                        "date_survey":  date_survey,
                        "comment":      comment
                    }
                    success, msg = create_survey_report(data)
                    if success:
                        st.success(f"✅ {msg}")
                        st.cache_data.clear()
                        st.rerun()  # Reset form and refresh list
                    else:
                        st.error(f"❌ Gagal: {msg}")

def render_buoy_data_form():
    tab1, tab2 = st.tabs(["Daftar data Buoy", "Buat data Buoy"])
    
    with tab1:
        st.info("Fitur riwayat data buoy akan segera hadir.")

    with tab2:
        _section_header("📡", "Input Data Buoy", "Masukkan data (.dat, .xlsx, .csv) dari buoy untuk kalkulasi rata-rata")

        uploaded_file = st.file_uploader("Upload File Data Buoy", type=["dat", "xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, skiprows=[0,2,3], na_values="NAN")
                df = df.dropna()
                
                if 'TIMESTAMP' in df.columns:
                    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    df = df.dropna(subset=['TIMESTAMP'])
                    df = df.sort_values(by='TIMESTAMP')

                mapping_kolom = {
                    'Hsig1_3': 'tinggi_gelombang_signifikan',
                    'Hsig': 'tinggi_gelombang_maks',
                    'Tzuc': 'periode_nol_crossing',
                    'Tpeak': 'periode_puncak',
                    'WL_av': 'rata_rata_level_air',
                    'WL_max': 'level_air_maksimum'
                }
                df.rename(columns=mapping_kolom, inplace=True)

                st.success("✅ File berhasil di-parse dan diproses!")
                
                if 'TIMESTAMP' in df.columns:
                    df = df.set_index('TIMESTAMP')
                
                st.subheader("Informasi Gelombang & Level Air (Mapped Data)")
                st.dataframe(df, width = "stretch")
                
                csv_data = df.to_csv(index=True).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Data Bersih (CSV)",
                    data=csv_data,
                    file_name="wlr_data_bersih.csv",
                    mime="text/csv",
                    key="download_clean_wlr"
                )

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat membaca atau memproses file: {str(e)}")

def render_survey_page():
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">📋</div>
            <div>
                <p class="page-header-title">Laporan Survei Harian</p>
                <p class="page-header-subtitle">Field survey reports & documentation</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ DaftarSurvey", "➕ Data Buoy"])

    with tab1:
        render_create_survey_form()

    with tab2:
        render_buoy_data_form()