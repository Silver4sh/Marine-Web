import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

# Environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@st.cache_resource
def get_engine() -> Engine:
    """
    Membuat dan menyimpan engine database dengan optimasi pooling.
    """
    try:
        return create_engine(
            DB_URL, 
            echo=False, 
            pool_pre_ping=True,
            pool_size=10,        
            max_overflow=20,     
            pool_recycle=1800    
        )
    except Exception as e:
        st.error(f"Gagal membuat engine database: {e}")
        return None

def get_connection():
    """Mendapatkan koneksi dari engine yang tersimpan."""
    engine = get_engine()
    if engine is None:
        return None
        
    try:
        return engine.connect()
    except SQLAlchemyError as e:
        st.error(f"Kesalahan koneksi database: {e}")
        return None

def run_query(query, params=None):
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()

    try:
        with engine.connect() as conn:
            if params:
                df = pd.read_sql(text(query), conn, params=params)
            else:
                df = pd.read_sql(text(query), conn)
            return df
    except Exception as e:
        print(f"Query error: {e}") 
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_fleet_status():
    query = """
    SELECT 
        COUNT(*) as total_vessels,
        SUM(CASE WHEN LOWER(status) = 'operating' THEN 1 ELSE 0 END) as operating,
        SUM(CASE WHEN LOWER(status) IN ('maintenance', 'mtc') THEN 1 ELSE 0 END) as maintenance,
        SUM(CASE WHEN LOWER(status) = 'idle' THEN 1 ELSE 0 END) as idle
    FROM operation.vessels
    """
    df = run_query(query)
    if df.empty:
        return {"total_vessels": 0, "operating": 0, "maintenance": 0, "idle": 0}
    return df.astype(int).iloc[0].to_dict()

@st.cache_data(ttl=30)
def get_vessel_position():
    query = """
    SELECT DISTINCT ON (vp.id_vessel)
           vp.id_vessel as "code_vessel",
           'Nama Kapal' as "Nama Kapal",
           v.status as "Status",
           vp.latitude,
           vp.longitude,
           vp.speed,
           0 as heading,
           vp.created_at as "Terakhir Update"
    FROM operation.vessel_positions vp
    JOIN operation.vessels v ON vp.id_vessel = v.code_vessel
    ORDER BY vp.id_vessel, vp.created_at DESC;
    """
    return run_query(query)

@st.cache_data(ttl=30)
def get_path_vessel(vessel_id):
    query = """
    SELECT latitude, longitude, 0 as heading, speed, created_at
    FROM operation.vessel_positions
    WHERE id_vessel = :vessel_id
    ORDER BY created_at DESC;
    """
    return run_query(query, params={"vessel_id": vessel_id})

@st.cache_data(ttl=60)
def get_data_water():
    query = """
    SELECT
        bsh.id_buoy,
        s.latitude,
        s.longitude,
        bsh.salinitas as salinitas,
        bsh.turbidity as turbidity,
        bsh.current as current,
        bsh.oxygen as oxygen,
        bsh.tide as tide,
        bsh.density as density,
        bsh.created_at as latest_timestamp
    FROM operation.buoy_sensor_histories bsh
    JOIN operation.buoys b ON b.code_buoy = bsh.id_buoy
    JOIN operation.sites s ON s.code_site = b.id_site
    ORDER BY bsh.created_at DESC
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_sensor_trends(buoy_id=None):
    params = {}
    where_clause = ""
    if buoy_id:
        where_clause = "WHERE bsh.id_buoy = :buoy_id"
        params["buoy_id"] = buoy_id
        
    query = f"""
    SELECT 
        created_at,
        salinitas,
        turbidity,
        current,
        oxygen
    FROM operation.buoy_sensor_histories bsh
    {where_clause}
    ORDER BY created_at ASC
    """
    return run_query(query, params)

@st.cache_data(ttl=3600)
def get_buoy_list():
    query = "SELECT DISTINCT id_buoy FROM operation.buoy_sensor_histories ORDER BY id_buoy"
    return run_query(query)

@st.cache_data(ttl=600)
def get_buoy_date_range(buoy_id):
    query = """
    SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
    FROM operation.buoy_sensor_histories
    WHERE id_buoy = :buoy_id
    """
    return run_query(query, params={"buoy_id": buoy_id})

@st.cache_data(ttl=60)
def get_buoy_history(buoy_id, start_date, end_date):
    query = """
    SELECT
        bsh.id_buoy,
        bsh.salinitas,
        bsh.turbidity,
        bsh.current,
        bsh.oxygen,
        bsh.tide,
        bsh.density,
        s.latitude,
        s.longitude,
        bsh.created_at
    FROM operation.buoy_sensor_histories bsh
    JOIN operation.buoys b ON bsh.id_buoy = b.code_buoy 
    JOIN operation.sites s ON b.id_site = s.code_site 
    WHERE bsh.id_buoy = :buoy_id
      AND bsh.created_at >= :start_date
      AND bsh.created_at <= :end_date
    ORDER BY bsh.created_at ASC
    """
    return run_query(query, params={
        "buoy_id": buoy_id,
        "start_date": start_date,
        "end_date": end_date
    })

@st.cache_data(ttl=600)
def get_global_date_range():
    query = """
    SELECT MIN(created_at) as min_date, MAX(created_at) as max_date
    FROM operation.buoy_sensor_histories
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_aggregated_buoy_history(start_date, end_date):
    query = """
    SELECT
        date_trunc('hour', created_at) as created_at,
        AVG(salinitas) as salinitas,
        AVG(turbidity) as turbidity,
        AVG(current) as current,
        AVG(oxygen) as oxygen,
        AVG(tide) as tide,
        AVG(density) as density
    FROM operation.buoy_sensor_histories
    WHERE created_at >= :start_date AND created_at <= :end_date
    GROUP BY 1
    ORDER BY 1 ASC
    """
    return run_query(query, params={
        "start_date": start_date,
        "end_date": end_date
    })

@st.cache_data(ttl=300)
def get_financial_metrics():
    query = """
    SELECT 
        COALESCE(SUM(total_amount), 0) as total_revenue,
        COUNT(DISTINCT id_order) as completed_orders,
        DATE_TRUNC('month', payment_date)::DATE AS payment_day
    FROM operation.payments
    WHERE status = 'Payed'
    GROUP BY DATE_TRUNC('month', payment_date)
    ORDER BY payment_day DESC;
    """
    df = run_query(query)
    
    if df.empty:
        return {
            "total_revenue": 0, 
            "completed_orders": 0, 
            "delta_revenue": 0.0,
            "delta_orders": 0.0
        }
    
    current = df.iloc[0]
    curr_rev = float(current["total_revenue"])
    curr_orders = int(current["completed_orders"])
    
    metrics = {
        "total_revenue": curr_rev,
        "completed_orders": curr_orders,
        "delta_revenue": 0.0,
        "delta_orders": 0.0
    }
    
    if len(df) > 1:
        previous = df.iloc[1]
        
        if previous["total_revenue"] > 0:
            metrics["delta_revenue"] = ((current["total_revenue"] - previous["total_revenue"]) / previous["total_revenue"]) * 100
            
        if previous["completed_orders"] > 0:
            metrics["delta_orders"] = ((current["completed_orders"] - previous["completed_orders"]) / previous["completed_orders"]) * 100
            
    return metrics

@st.cache_data(ttl=300)
def get_revenue_analysis():
    query = """
    SELECT 
        DATE_TRUNC('month', payment_date) as month,
        SUM(total_amount) as revenue
    FROM operation.payments
    WHERE status = 'Payed'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_order_stats():
    query = """
    SELECT 
        COUNT(*) as total_orders,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN status = 'In Completed' THEN 1 ELSE 0 END) as in_completed,
        SUM(CASE WHEN status = 'On Progress' THEN 1 ELSE 0 END) as on_progress,
        SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed
    FROM operation.orders
    """
    df = run_query(query)
    if df.empty:
        return {"total_orders": 0, "completed": 0, "in_completed": 0, "on_progress": 0, "failed": 0}
    return df.astype(int).iloc[0].to_dict()

@st.cache_data(ttl=300)
def get_revenue_by_service():
    query = """
    SELECT 
        c.industry as "Layanan",
        SUM(p.total_amount) as "Nilai"
    FROM operation.payments p
    JOIN operation.orders o ON p.id_order = o.id
    JOIN operation.clients c ON o.id_client = c.code_client
    WHERE p.status = 'Payed'
    GROUP BY c.industry
    ORDER BY "Nilai" DESC
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_fleet_daily_activity():
    query = """
    SELECT 
        v.code_vessel,
        TO_CHAR(vp.created_at, 'Dy') as day_name,
        EXTRACT(ISODOW FROM vp.created_at) as day_num,
        COUNT(DISTINCT DATE_TRUNC('hour', vp.created_at)) as active_hours
    FROM operation.vessel_positions vp
    JOIN operation.vessels v ON vp.id_vessel = v.code_vessel
    WHERE vp.created_at >= NOW() - INTERVAL '7 days'
      AND vp.speed > 0.5
    GROUP BY 1, 2, 3
    ORDER BY day_num
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_clients_summary():
    query = """
    SELECT 
        c.code_client,
        c.name,
        c.industry,
        c.region,
        c.status,
        COUNT(DISTINCT o.id) as total_orders,
        COALESCE(SUM(p.total_amount), 0) as ltv
    FROM operation.clients c
    LEFT JOIN operation.orders o ON c.code_client = o.id_client
    LEFT JOIN operation.payments p ON o.id = p.id_order AND p.status = 'Payed'
    GROUP BY c.code_client, c.name, c.industry, c.region, c.status
    ORDER BY ltv DESC
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_logs():
    query = """
    SELECT 
        changed_by,
        table_name,
        "action",
        old_data,
        new_data,
        changed_at        
    FROM audit.audit_logs
    WHERE created_at <= NOW() - interval '7 days'
    ORDER BY created_at desc
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_vessel_list():
    query = """
    SELECT 
        code_vessel
    FROM operation.vessels
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_vessel_utilization_stats():
    query = """
    SELECT 
        v.name as vessel_name,
        SUM(EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600) as total_hours,
        SUM(CASE WHEN LOWER(va.status) NOT IN ('idle', 'maintenance', 'docking') 
            THEN EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600 
            ELSE 0 END) as productive_hours
    FROM operation.vessel_activities va
    JOIN operation.vessels v ON va.id_vessel = v.code_vessel
    WHERE va.start_date >= NOW() - INTERVAL '30 days'
    GROUP BY v.name
    """
    df = run_query(query)
    if not df.empty:
        df['utilization_rate'] = (df['productive_hours'] / df['total_hours']) * 100
        df['utilization_rate'] = df['utilization_rate'].fillna(0)
    return df

@st.cache_data(ttl=300)
def get_revenue_cycle_metrics():
    query = """
    SELECT 
        DATE_TRUNC('month', o.order_date) as month,
        AVG(EXTRACT(DAY FROM (p.payment_date - o.order_date))) as avg_days_to_cash,
        SUM(p.total_amount) as realized_revenue,
        SUM(CASE WHEN p.status = 'Payed' THEN 1 ELSE 0 END) as paid_count,
        COUNT(o.id) as total_orders
    FROM operation.orders o
    JOIN operation.payments p ON o.id = p.id_order
    WHERE o.order_date >= NOW() - INTERVAL '6 months'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)

@st.cache_data(ttl=60)
def get_environmental_anomalies():
    query = """
    WITH stats AS (
        SELECT 
            id_buoy,
            AVG(salinitas) as avg_sal,
            STDDEV(salinitas) as std_sal,
            AVG(turbidity) as avg_tur,
            STDDEV(turbidity) as std_tur
        FROM operation.buoy_sensor_histories
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY id_buoy
    )
    SELECT 
        h.id_buoy,
        h.created_at,
        h.salinitas,
        h.turbidity,
        (h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0) as sal_z_score,
        (h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0) as tur_z_score
    FROM operation.buoy_sensor_histories h
    JOIN stats s ON h.id_buoy = s.id_buoy
    WHERE h.created_at >= NOW() - INTERVAL '7 days'
      AND (
          ABS((h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0)) > 2
          OR 
          ABS((h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0)) > 2
      )
    ORDER BY h.created_at DESC
    LIMIT 50
    """
    return run_query(query)

@st.cache_data(ttl=300)
def get_logistics_performance():
    query = """
    SELECT 
        destination,
        COUNT(*) as total_trips,
        AVG(EXTRACT(EPOCH FROM (actual_delivery_date - scheduled_delivery_date))/3600) as avg_delay_hours,
        SUM(CASE WHEN actual_delivery_date > scheduled_delivery_date THEN 1 ELSE 0 END) as late_trips
    FROM operation.orders
    WHERE actual_delivery_date IS NOT NULL 
      AND scheduled_delivery_date IS NOT NULL
    GROUP BY destination
    ORDER BY avg_delay_hours DESC
    """
    return run_query(query)

def init_settings_table():
    engine = get_engine()
    if not engine: return
    
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS operation.system_settings (
                    key VARCHAR(50) PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            res = conn.execute(text("SELECT count(*) FROM operation.system_settings")).scalar()
            if res == 0:
                defaults = [
                    ("app_name", "MarineOS Dashboard", "Application Name displayed in header"),
                    ("maintenance_mode", "false", "Enable maintenance mode overlay"),
                    ("revenue_target_monthly", "5000000000", "Monthly Revenue Target (IDR)"),
                    ("churn_risk_threshold", "3", "Number of high-risk clients to trigger alert"),
                    ("theme_color", "#0ea5e9", "Primary accent color hex code")
                ]
                for k, v, d in defaults:
                    conn.execute(
                        text("INSERT INTO operation.system_settings (key, value, description) VALUES (:k, :v, :d)"),
                        {"k": k, "v": v, "d": d}
                    )
    except Exception as e:
        print(f"Error initializing settings: {e}")

@st.cache_data(ttl=60)
def get_system_settings():
    init_settings_table()
    query = "SELECT key, value, description FROM operation.system_settings"
    df = run_query(query)
    if df.empty: return {}
    return pd.Series(df.value.values, index=df.key).to_dict()

def update_system_setting(key, value):
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            query = text("UPDATE operation.system_settings SET value = :value, updated_at = NOW() WHERE key = :key")
            conn.execute(query, {"value": str(value), "key": key})
            st.cache_data.clear()
            return True
    except Exception as e:
        st.error(f"Gagal memperbarui pengaturan: {e}")
        return False

def get_all_users():
    query = """
    SELECT 
        u.code_user,
        um.id_user as username,
        u.role,
        u.status as user_status,
        um.status as account_status,
        um.last_login
    FROM operation.users u
    JOIN operation.user_managements um ON u.code_user = um.id_user
    ORDER BY u.code_user ASC
    """
    return run_query(query)

def create_new_user(username, password, role):
    engine = get_engine()
    if not engine:
        return False, "Koneksi database gagal."

    try:
        with engine.begin() as conn:
            check_q = text("SELECT 1 FROM operation.users WHERE code_user = :username")
            res = conn.execute(check_q, {"username": username}).fetchone()
            if res:
                return False, f"Pengguna '{username}' sudah ada."

            insert_user = text("""
                INSERT INTO operation.users (code_user, role, status)
                VALUES (:username, :role, 'Active')
            """)
            conn.execute(insert_user, {"username": username, "role": role})

            insert_auth = text("""
                INSERT INTO operation.user_managements (id_user, password, status)
                VALUES (:username, :password, 'Active')
            """)
            conn.execute(insert_auth, {"username": username, "password": password})
            
            return True, "Pengguna berhasil dibuat."
    except Exception as e:
        return False, f"Gagal membuat pengguna: {e}"

def update_user_status(username, new_status):
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            q1 = text("UPDATE operation.users SET status = :status WHERE code_user = :username")
            conn.execute(q1, {"status": new_status, "username": username})
            
            q2 = text("UPDATE operation.user_managements SET status = :status WHERE id_user = :username")
            conn.execute(q2, {"status": new_status, "username": username})
            return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False

def update_user_role(username, new_role):
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            q = text("UPDATE operation.users SET role = :role WHERE code_user = :username")
            conn.execute(q, {"role": new_role, "username": username})
            return True
    except Exception as e:
        print(f"Error updating role: {e}")
        return False

def delete_user(username):
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            q1 = text("DELETE FROM operation.user_managements WHERE id_user = :username")
            conn.execute(q1, {"username": username})
            
            q2 = text("DELETE FROM operation.users WHERE code_user = :username")
            conn.execute(q2, {"username": username})
            return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def update_last_login_optimized(username, password):
    engine = get_engine()
    if not engine: return False
    try:
        with engine.begin() as conn:
            update_query = text("""
                UPDATE operation.user_managements
                SET last_login = CURRENT_TIMESTAMP
                WHERE id_user = :user_id AND password = :pwd
            """)
            conn.execute(update_query, {"user_id": username, "pwd": password})
        return True
    except Exception as e:
        print(f"Update last_login error: {e}")
        return False

def update_password(username, old_pass, new_pass):
    if not username or not old_pass or not new_pass:
        return False, "Semua kolom harus diisi"
    
    if old_pass == new_pass:
        return False, "Kata sandi baru tidak boleh sama dengan kata sandi lama"
    
    engine = get_engine()
    if not engine: return False, "Koneksi database gagal"
    try:
        with engine.begin() as conn:
            query = text("""
                SELECT 
                    um.id_user,
                    u.role,
                    u.status as user_status,
                    um.status as account_status
                FROM operation.user_managements um
                JOIN operation.users u ON um.id_user = u.code_user
                WHERE um.id_user = :username
                    AND um.password = :password
                    AND um.status = 'Active'
                    AND u.status = 'Active'
                    AND u.role IN ('Finance', 'Admin')
            """)
            
            res = conn.execute(query, {
                "username": username, 
                "password": old_pass
            }).fetchone()
            
            if not res:
                return False, "Username atau kata sandi lama salah"
            
            update_query = text("""
                UPDATE operation.user_managements
                SET password = :new_password,
                updated_at = CURRENT_TIMESTAMP
                WHERE id_user = :user_id 
                    AND password = :old_password
            """)
            
            result = conn.execute(update_query, {
                "user_id": username, 
                "old_password": old_pass, 
                "new_password": new_pass.strip()
            })
            
            if result.rowcount > 0:
                return True, "Kata sandi berhasil diperbarui"
            else:
                return False, "Gagal memperbarui kata sandi"
            
    except Exception as e:
        st.error(f"Kesalahan database: {e}")
        return False, f"Terjadi kesalahan sistem: {str(e)}"
