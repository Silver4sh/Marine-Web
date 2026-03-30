"""db/repos/survey.py — moved from db/repositories/survey_repo.py"""
import streamlit as st
import pandas as pd
from db.connection import sb_table


@st.cache_data(ttl=60)
def get_all_surveys() -> pd.DataFrame:
    surveys = pd.DataFrame(sb_table("survey", "daily_report_survey_activity")
        .select("id, code_report, project_name, date_survey, id_site, id_vessel, id_user, comment")
        .order("date_survey", desc=True).execute().data)
    if surveys.empty:
        return pd.DataFrame()
    sites   = pd.DataFrame(sb_table("operation", "sites").select("code_site").execute().data)
    vessels = pd.DataFrame(sb_table("operation", "vessels").select("code_vessel, name").execute().data)
    users   = pd.DataFrame(sb_table("operation", "users").select("code_user, name").execute().data)
    df = surveys\
        .merge(sites,   left_on="id_site",   right_on="code_site",   how="left")\
        .merge(vessels, left_on="id_vessel", right_on="code_vessel", how="left")\
        .merge(users,   left_on="id_user",   right_on="code_user",   how="left")\
        .rename(columns={"code_site": "site_name", "name_x": "vessel_name", "name_y": "surveyor_name"})
    return df[["id", "code_report", "project_name", "date_survey",
               "site_name", "vessel_name", "surveyor_name", "comment"]]


def create_survey_report(data: dict) -> tuple[bool, str]:
    try:
        sb_table("survey", "daily_report_survey_activity").insert({
            "project_name": data["project_name"],
            "code_report":  data["code_report"],
            "id_site":      data["id_site"],
            "id_vessel":    data["id_vessel"],
            "id_user":      data["id_user"],
            "date_survey":  str(data["date_survey"]),
            "comment":      data["comment"],
        }).execute()
        return True, "Laporan berhasil dibuat."
    except Exception as e:
        return False, str(e)
