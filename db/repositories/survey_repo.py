import streamlit as st
from db.connection import run_query, get_engine
from sqlalchemy import text

@st.cache_data(ttl=60)
def get_all_surveys():
    query = """
    SELECT 
        s.id,
        s.code_report,
        s.project_name,
        s.date_survey,
        si.code_site as site_name,
        v.name as vessel_name,
        u.name as surveyor_name,
        s.comment
    FROM survey.daily_report_survey_activity s
    LEFT JOIN operation.sites si ON s.id_site = si.code_site
    LEFT JOIN operation.vessels v ON s.id_vessel = v.code_vessel
    LEFT JOIN operation.users u ON s.id_user = u.code_user
    ORDER BY s.date_survey DESC
    """
    return run_query(query)

def create_survey_report(data):
    try:
        with get_engine().begin() as conn:
            stmt = text("""
                INSERT INTO survey.daily_report_survey_activity 
                (project_name, code_report, id_site, id_vessel, id_user, date_survey, comment)
                VALUES (:project, :code, :site, :vessel, :user, :date, :comment)
                RETURNING id
            """)
            conn.execute(stmt, {
                "project": data['project_name'],
                "code": data['code_report'],
                "site": data['id_site'],
                "vessel": data['id_vessel'],
                "user": data['id_user'],
                "date": data['date_survey'],
                "comment": data['comment']
            })
            return True, "Laporan berhasil dibuat."
    except Exception as e:
        return False, str(e)
