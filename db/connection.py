import hashlib
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load .env (untuk DATABASE_URL fallback)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)


@st.cache_resource
def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    return create_client(
        st.secrets.DB_ACCESS.SUPABASE_URL,
        st.secrets.DB_ACCESS.SUPABASE_KEY,
    )


# ── Resolve DATABASE_URL ───────────────────────────────────────────────────────
# Priority: st.secrets (Streamlit Cloud / secrets.toml) → DATABASE_URL env var

def _get_database_url() -> str:
    """Return the full DATABASE_URL from secrets or environment."""
    # 1. Try st.secrets (works for Streamlit Cloud AND local .streamlit/secrets.toml)
    try:
        url = st.secrets["database"]["DATABASE_URL"]
        if url:
            return url
    except (KeyError, FileNotFoundError):
        pass

    # 2. Fall back to .env DATABASE_URL
    url = os.getenv("DATABASE_URL", "")
    if url:
        return url

    raise RuntimeError(
        "DATABASE_URL tidak ditemukan. ")


# ── SQLAlchemy Engine (untuk raw SQL kompleks) ─────────────────────────────────

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError

    @st.cache_resource
    def _build_engine(url_hash: str) -> Engine:
        """Internal: build SQLAlchemy engine (cached by URL hash)."""
        raw_url = _get_database_url()
        db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return create_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=7,
            pool_recycle=600,
            pool_timeout=30,
            connect_args={
                "sslmode":         "require",
                "connect_timeout": 15,
            },
        )

    def get_engine() -> Engine:
        """Return a SQLAlchemy engine, invalidated whenever DATABASE_URL changes."""
        raw_url = _get_database_url()
        url_hash = hashlib.md5(raw_url.encode()).hexdigest()
        return _build_engine(url_hash)

    def get_connection():
        """Return a SQLAlchemy connection object."""
        engine = get_engine()
        if engine is None:
            return None
        try:
            return engine.connect()
        except SQLAlchemyError as e:
            st.error(f"Kesalahan koneksi: {e}")
            return None

    def run_query(query, params=None) -> pd.DataFrame:
        """Execute a raw SQL query via Supabase Postgres and return results as a DataFrame."""
        engine = get_engine()
        if engine is None:
            return pd.DataFrame()
        try:
            with engine.connect() as conn:
                stmt = text(query) if isinstance(query, str) else query
                result = conn.execute(stmt, params or {})
                rows = result.fetchall()
                if not rows:
                    return pd.DataFrame()
                return pd.DataFrame(rows, columns=list(result.keys()))
        except Exception as e:
            print(f"Query error: {e}")
            return pd.DataFrame()

except ImportError:
    # Fallback jika sqlalchemy tidak tersedia
    def get_engine():
        raise RuntimeError("SQLAlchemy tidak tersedia. Install dengan: pip install sqlalchemy psycopg2-binary")

    def get_connection():
        raise RuntimeError("SQLAlchemy tidak tersedia.")

    def run_query(query, params=None) -> pd.DataFrame:
        raise RuntimeError("SQLAlchemy tidak tersedia.")
