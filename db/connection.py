import os
import streamlit as st
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load .env from project root (override=True so .env always wins over shell env)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)


# ── Resolve DATABASE_URL ──────────────────────────────────────────────────────
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
        "DATABASE_URL tidak ditemukan. "
        "Pastikan .env atau .streamlit/secrets.toml sudah dikonfigurasi."
    )


def get_raw_connection():
    """Return a raw psycopg2 connection. Caller is responsible for closing it."""
    url = _get_database_url()
    parsed = urlparse(url)
    try:
        connection = psycopg2.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            dbname=parsed.path.lstrip("/"),
            sslmode="require",
            connect_timeout=15,
        )
        return connection
    except Exception as e:
        st.error(f"Kesalahan koneksi: {e}")
        return None


@st.cache_resource
def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine."""
    raw_url = _get_database_url()
    # SQLAlchemy needs postgresql+psycopg2:// driver prefix
    db_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
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
                "sslmode":         "require",
                "connect_timeout": 15,
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
