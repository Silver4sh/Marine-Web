import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load .env from the streamlit project root (two levels above db/connection.py)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "marine_db")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"

@st.cache_resource
def get_engine() -> Engine:
    missing = [k for k, v in {"DB_USER": DB_USER, "DB_HOST": DB_HOST,
                               "DB_PORT": DB_PORT, "DB_NAME": DB_NAME}.items() if not v]
    if missing:
        st.error(f"❌ Konfigurasi database tidak lengkap. Cek file .env — kolom kosong: {', '.join(missing)}")
        return None
    try:
        return create_engine(
            DB_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1200,
            pool_timeout=30,
            connect_args={
                "connect_timeout": 10,
                "options": "-c statement_timeout=30000 -c lock_timeout=10000"
            }
        )
    except Exception as e:
        st.error(f"Gagal membuat engine database: {e}")
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
