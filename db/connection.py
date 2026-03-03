import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load .env from the streamlit project root
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"))

# ── Resolve DB credentials ────────────────────────────────────────────────────
# Priority: st.secrets (Streamlit Cloud) → DB_URL env var → individual DB_* vars

def _get_db_url() -> str:
    """Resolve the database URL from available credential sources."""
    # 1. Try st.secrets (Streamlit Cloud deployment)
    try:
        secrets = st.secrets.get("database", {})
        if secrets.get("DB_URL"):
            return secrets["DB_URL"]
        if all(secrets.get(k) for k in ("DB_HOST", "DB_USER", "DB_PASS", "DB_NAME")):
            port = secrets.get("DB_PORT", "5432")
            return (
                f"postgresql+psycopg2://{secrets['DB_USER']}:{secrets['DB_PASS']}"
                f"@{secrets['DB_HOST']}:{port}/{secrets['DB_NAME']}"
            )
    except Exception:
        pass  # Not running in Streamlit Cloud or secrets not configured

    # 2. Full URL from env var
    url_override = os.getenv("DB_URL", "")
    if url_override:
        return url_override

    # 3. Individual env vars (local development)
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
    if engine is None: return None
    try: return engine.connect()
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
