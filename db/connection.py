import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    return create_client(
        st.secrets.DB_ACCESS.DATABASE_URL,
        st.secrets.DB_ACCESS.database,
    )


def sb_table(schema: str, table: str):
    """Shorthand: get_supabase().schema(schema).table(table)."""
    return get_supabase().schema(schema).table(table)
