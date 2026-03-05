import streamlit as st
import pandas as pd
from db.connection import get_supabase


@st.cache_data(ttl=60)
def get_all_surveys():
    sb = get_supabase()
    surveys = pd.DataFrame(sb.schema("survey").table("daily_report_survey_activity")
        .select("id, code_report, project_name, date_survey, id_site, id_vessel, id_user, comment")
        .order("date_survey", desc=True).execute().data)
    if surveys.empty:
        return pd.DataFrame()

    sites   = pd.DataFrame(sb.schema("operation").table("sites")
        .select("code_site").execute().data)
    vessels = pd.DataFrame(sb.schema("operation").table("vessels")
        .select("code_vessel, name").execute().data)
    users   = pd.DataFrame(sb.schema("operation").table("users")
        .select("code_user, name").execute().data)

    df = surveys.merge(sites,   left_on="id_site",   right_on="code_site",   how="left")
    df = df.merge(vessels, left_on="id_vessel", right_on="code_vessel", how="left")
    df = df.merge(users,   left_on="id_user",   right_on="code_user",   how="left")

    df = df.rename(columns={
        "code_site":   "site_name",
        "name_x":      "vessel_name",
        "name_y":      "surveyor_name",
    })
    return df[["id", "code_report", "project_name", "date_survey",
               "site_name", "vessel_name", "surveyor_name", "comment"]]


def create_survey_report(data):
    try:
        sb = get_supabase()
        sb.schema("survey").table("daily_report_survey_activity").insert({
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
