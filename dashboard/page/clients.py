import streamlit as st
from back.query.queries import get_clients_summary

def render_clients_page():
    st.markdown("## 👥 Client Portfolio")
    df = get_clients_summary()
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Total Clients", len(df))
        c2.metric("Active Regions", df['region'].nunique())
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No client data found.")
