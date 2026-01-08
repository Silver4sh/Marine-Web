import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

# Environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Validate environment variables
if not all([DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME]):
    missing = [v for v in ["DB_USER", "DB_PASS", "DB_HOST", "DB_PORT", "DB_NAME"] if not os.getenv(v)]
    st.error(f"Missing environment variables: {', '.join(missing)}. Please check your .env file.")
    DB_URL = None
else:
    DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@st.cache_resource
def get_engine() -> Engine:
    """
    Create and cache the database engine with connection pooling optimization.
    Pool size and recycle time are tuned for Streamlit performance.
    """
    if DB_URL is None:
        return None
    try:
        return create_engine(
            DB_URL, 
            echo=False, 
            pool_pre_ping=True,
            pool_size=10,        # Keep 10 connections open
            max_overflow=20,     # Allow 20 more during peak
            pool_recycle=1800    # Recycle connections every 30 mins
        )
    except Exception as e:
        st.error(f"Failed to create database engine: {e}")
        return None

def get_connection():
    """Get a connection from the cached engine with error handling."""
    engine = get_engine()
    if engine is None:
        return None
        
    try:
        return engine.connect()
    except SQLAlchemyError as e:
        st.error(f"Database connection error: {e}")
        return None

