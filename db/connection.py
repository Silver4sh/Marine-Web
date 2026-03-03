import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load .env from the streamlit project root (override=True ensures .env always wins)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)

# ── Resolve DB credentials ────────────────────────────────────────────────────
# Priority: st.secrets (Streamlit Cloud) → DB_URL env var → individual DB_* vars

def _get_db_url() -> str:
    """Resolve the database URL from available credential sources."""
    # 1. Try st.secrets (works locally via .streamlit/secrets.toml AND on Cloud)
    try:
        db_secrets = st.secrets["database"]
        # Try full URL first
        if db_secrets.get("DB_URL"):
            return db_secrets["DB_URL"]
        # Build URL from individual keys
        host = db_secrets["DB_HOST"]
        user = db_secrets["DB_USER"]
        pw   = db_secrets["DB_PASS"]
        name = db_secrets["DB_NAME"]
        port = db_secrets.get("DB_PORT", "5432")
        return f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{name}"
    except (KeyError, FileNotFoundError):
        pass  # secrets.toml not present or [database] section missing

    # 2. Full URL from env var
    url_override = os.getenv("DB_URL", "")
    if url_override:
        return url_override

    # 3. Individual env vars (local development fallback)
    user = os.getenv("DB_USER", "postgres")
    pw   = os.getenv("DB_PASS", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")
    return f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{name}"


@st.cache_resource
def get_engine() -> Engine:
    db_url = _get_db_url()
    try:
        engine = create_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=7,
            pool_recycle=600,
            pool_timeout=30,
            connect_args={
                "sslmode":             "require",  # Required for Supabase
                "connect_timeout":     15,
                "keepalives":          1,
                "keepalives_idle":     30,
                "keepalives_interval": 5,
                "keepalives_count":    3,
                "options":             "-c statement_timeout=30000 -c lock_timeout=10000",
            }
        )
        return engine
    except Exception as e:
        st.error(f"Gagal membuat koneksi database: {e}")
        return None


def get_connection():
    engine = get_engine()
    if engine is None:
        return None
    try:
        return engine.connect()
    except SQLAlchemyError as e:
        st.error(f"Kesalahan koneksi database: {e}")
        return None


def run_query(query, params=None):
    """Execute a SQL query and return results as a DataFrame."""
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
