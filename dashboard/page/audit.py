import streamlit as st
from back.query.queries import get_logs

@st.dialog("Audit Logs")
def view_audit_logs():
    st.write("Recent entries from Vibrocore Logs")
    df = get_logs()
    if not df.empty:
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "created_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, h:mm a")
            }
        )
    else:
        st.info("No audit logs found.")
