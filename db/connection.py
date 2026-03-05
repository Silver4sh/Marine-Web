import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    return create_client(
        st.secrets.DB_ACCESS.DATABASE_URL,
        st.secrets.DB_ACCESS.database,
    )
