import os
import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load .env from project root (override=True so .env always wins over shell env)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)


# ── Resolve DB credentials ────────────────────────────────────────────────────
# Priority: st.secrets (Streamlit Cloud / .streamlit/secrets.toml) → .env

def _get_credentials() -> dict:
    """Return a dict of DB credentials from secrets or env vars."""
    # 1. Try st.secrets (works for Streamlit Cloud AND local secrets.toml)
    try:
        s = st.secrets["database"]
        return {
            "user":     s["DB_USER"],
            "password": s["DB_PASS"],
            "host":     s["DB_HOST"],
            "port":     str(s.get("DB_PORT", "5432")),
            "dbname":   s["DB_NAME"],
        }
    except (KeyError, FileNotFoundError):
        pass  # secrets.toml absent or [database] section missing

    # 2. Fall back to .env / environment variables
    return {
        "user":     os.getenv("user", ""),
        "password": os.getenv("password", ""),
        "host":     os.getenv("host", "localhost"),
        "port":     os.getenv("port", "5432"),
        "dbname":   os.getenv("dbname", "postgres"),
    }


def get_raw_connection():
    """Return a raw psycopg2 connection. Caller is responsible for closing it."""
    creds = _get_credentials()
    try:
        connection = psycopg2.connect(
            user=creds["user"],
            password=creds["password"],
            host=creds["host"],
            port=creds["port"],
            dbname=creds["dbname"],
            sslmode="require",
            connect_timeout=15,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=5,
            keepalives_count=3,
            options="-c statement_timeout=30000 -c lock_timeout=10000",
        )
        return connection
    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return None


@st.cache_resource
def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine built from resolved credentials."""
    creds = _get_credentials()
    db_url = (
        f"postgresql+psycopg2://{creds['user']}:{creds['password']}"
        f"@{creds['host']}:{creds['port']}/{creds['dbname']}"
    )
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
                "sslmode":             "require",
                "connect_timeout":     15,
                "keepalives":          1,
                "keepalives_idle":     30,
                "keepalives_interval": 5,
                "keepalives_count":    3,
                "options":             "-c statement_timeout=30000 -c lock_timeout=10000",
            },
        )
        return engine
    except Exception as e:
        st.error(f"Gagal membuat koneksi database: {e}")
        return None


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
