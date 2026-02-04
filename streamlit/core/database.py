import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@st.cache_resource
def get_engine() -> Engine:
    try:
        return create_engine(DB_URL, echo=False, pool_pre_ping=True, pool_size=10, max_overflow=20, pool_recycle=1800)
    except Exception as e:
        st.error(f"Gagal membuat engine database: {e}"); return None

def get_connection():
    engine = get_engine()
    if engine is None: return None
    try: return engine.connect()
    except SQLAlchemyError as e: st.error(f"Kesalahan koneksi database: {e}"); return None

def run_query(query, params=None):
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    try:
        with engine.connect() as conn:
            if params: return pd.read_sql(text(query), conn, params=params)
            else: return pd.read_sql(text(query), conn)
    except Exception as e: print(f"Query error: {e}"); return pd.DataFrame()

# --- FLEET QUERIES ---
@st.cache_data(ttl=60)
def get_fleet_status():
    query = "SELECT COUNT(*) as total_vessels, SUM(CASE WHEN LOWER(va.status) = 'operating' THEN 1 ELSE 0 END) as operating, SUM(CASE WHEN LOWER(va.status) IN ('maintenance', 'mtc') THEN 1 ELSE 0 END) as maintenance, SUM(CASE WHEN LOWER(va.status) = 'idle' THEN 1 ELSE 0 END) as idle FROM operation.vessels v join operation.vessel_activities va on v.code_vessel = va.id_vessel where va.seq_activity in (select max(vva.seq_activity) from operation.vessels vv join operation.vessel_activities vva on vv.code_vessel = vva.id_vessel group by vva.id_vessel)"
    df = run_query(query)
    if df.empty: return {"total_vessels": 0, "operating": 0, "maintenance": 0, "idle": 0}
    return df.astype(int).iloc[0].to_dict()

@st.cache_data(ttl=30)
def get_vessel_position():
    query = "SELECT DISTINCT ON (vp.id_vessel) vp.id_vessel as \"code_vessel\", 'Nama Kapal' as \"Nama Kapal\", v.status as \"Status\", vp.latitude, vp.longitude, vp.speed, 0 as heading, vp.created_at as \"Terakhir Update\" FROM operation.vessel_positions vp JOIN operation.vessels v ON vp.id_vessel = v.code_vessel ORDER BY vp.id_vessel, vp.created_at DESC;"
    return run_query(query)

@st.cache_data(ttl=30)
def get_path_vessel(vessel_id):
    query = "SELECT latitude, longitude, 0 as heading, speed, created_at FROM operation.vessel_positions WHERE id_vessel = :vessel_id ORDER BY created_at DESC;"
    return run_query(query, params={"vessel_id": vessel_id})

@st.cache_data(ttl=60)
def get_vessel_list():
    query = "SELECT code_vessel FROM operation.vessels"
    return run_query(query)

@st.cache_data(ttl=300)
def get_fleet_daily_activity():
    query = "SELECT v.code_vessel, TO_CHAR(vp.created_at, 'Dy') as day_name, EXTRACT(ISODOW FROM vp.created_at) as day_num, COUNT(DISTINCT DATE_TRUNC('hour', vp.created_at)) as active_hours FROM operation.vessel_positions vp JOIN operation.vessels v ON vp.id_vessel = v.code_vessel WHERE vp.created_at >= NOW() - INTERVAL '7 days' AND vp.speed > 0.5 GROUP BY 1, 2, 3 ORDER BY day_num"
    return run_query(query)

@st.cache_data(ttl=300)
def get_vessel_utilization_stats():
    query = "SELECT v.name as vessel_name, SUM(EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600) as total_hours, SUM(CASE WHEN LOWER(va.status) NOT IN ('idle', 'maintenance', 'docking') THEN EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600 ELSE 0 END) as productive_hours FROM operation.vessel_activities va JOIN operation.vessels v ON va.id_vessel = v.code_vessel WHERE va.start_date >= NOW() - INTERVAL '30 days' GROUP BY v.name"
    df = run_query(query)
    if not df.empty:
        df['utilization_rate'] = (df['productive_hours'] / df['total_hours']) * 100
        df['utilization_rate'] = df['utilization_rate'].fillna(0)
    return df

@st.cache_data(ttl=300)
def get_logistics_performance():
    query = "SELECT destination, COUNT(*) as total_trips, AVG(EXTRACT(EPOCH FROM (actual_delivery_date - scheduled_delivery_date))/3600) as avg_delay_hours, SUM(CASE WHEN actual_delivery_date > scheduled_delivery_date THEN 1 ELSE 0 END) as late_trips FROM operation.orders WHERE actual_delivery_date IS NOT NULL AND scheduled_delivery_date IS NOT NULL GROUP BY destination ORDER BY avg_delay_hours DESC"
    return run_query(query)

# --- FINANCIAL & ORDERS QUERIES ---
@st.cache_data(ttl=300)
def get_financial_metrics():
    query = "SELECT COALESCE(SUM(total_amount), 0) as total_revenue, COUNT(DISTINCT id_order) as completed_orders FROM operation.payments WHERE status = 'Completed'"
    df = run_query(query)
    if df.empty: return {"total_revenue": 0, "completed_orders": 0, "delta_revenue": 0.0}
    current = df.iloc[0]
    metrics = {"total_revenue": float(current["total_revenue"]), "completed_orders": int(current["completed_orders"]), "delta_revenue": 0.0}
    return metrics

@st.cache_data(ttl=300)
def get_client_stats():
    query = "SELECT COUNT(code_client) as total_clients, SUM(CASE WHEN created_at <= NOW() - INTERVAL '21 days' and status = 'Active' THEN 1 ELSE 0 END) as new_clients,  SUM(CASE WHEN created_at <= NOW() - INTERVAL '21 days' and status <> 'Active' THEN 1 ELSE 0 END) as deactive_clients FROM operation.clients"
    df = run_query(query)
    if df.empty: return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}
    return {"total_clients": int(df.iloc[0]["total_clients"]), "new_clients": int(df.iloc[0]["new_clients"]), "deactive_clients": int(df.iloc[0]["deactive_clients"])}

@st.cache_data(ttl=300)
def get_revenue_analysis():
    query = "SELECT DATE_TRUNC('month', payment_date) as month, SUM(total_amount) as revenue FROM operation.payments WHERE status = 'Completed' GROUP BY 1 ORDER BY 1 DESC"
    return run_query(query)

@st.cache_data(ttl=300)
def get_revenue_by_service():
    query = "SELECT c.industry as \"Layanan\", SUM(p.total_amount) as \"Nilai\" FROM operation.payments p JOIN operation.orders o ON p.id_order = o.code_order JOIN operation.clients c ON o.id_client = c.code_client WHERE p.status = 'Completed' GROUP BY c.industry ORDER BY \"Nilai\" DESC"
    return run_query(query)

@st.cache_data(ttl=300)
def get_order_stats():
    query = "SELECT COUNT(*) as total_orders, SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed, SUM(CASE WHEN status = 'In Completed' THEN 1 ELSE 0 END) as in_completed, SUM(CASE WHEN status = 'On Progress' THEN 1 ELSE 0 END) as on_progress, SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed FROM operation.orders"
    df = run_query(query)
    if df.empty: return {"total_orders": 0, "completed": 0, "in_completed": 0, "on_progress": 0, "failed": 0}
    return df.astype(int).iloc[0].to_dict()

@st.cache_data(ttl=1800) # Increased TTL to 30 mins
def get_revenue_cycle_metrics():
    query = "SELECT DATE_TRUNC('month', o.order_date) as month, AVG(EXTRACT(DAY FROM (p.payment_date - o.order_date))) as avg_days_to_cash, SUM(p.total_amount) as realized_revenue, SUM(CASE WHEN p.status = 'Completed' THEN 1 ELSE 0 END) as paid_count, COUNT(o.code_order) as total_orders FROM operation.orders o JOIN operation.payments p ON o.code_order = p.id_order WHERE o.order_date >= NOW() - INTERVAL '6 months' GROUP BY 1 ORDER BY 1 DESC"
    return run_query(query)

# --- ENVIRONMENTAL & OTHER QUERIES ---
@st.cache_data(ttl=60)
def get_data_water():
    query = "SELECT bsh.id_buoy, s.latitude, s.longitude, bsh.salinitas as salinitas, bsh.turbidity as turbidity, bsh.current as current, bsh.oxygen as oxygen, bsh.tide as tide, bsh.density as density, bsh.created_at as latest_timestamp FROM operation.buoy_sensor_histories bsh JOIN operation.buoys b ON b.code_buoy = bsh.id_buoy JOIN operation.sites s ON s.code_site = b.id_site ORDER BY bsh.created_at DESC"
    return run_query(query)

@st.cache_data(ttl=300)
def get_clients_summary():
    query = "SELECT c.code_client, c.name, c.industry, c.region, c.status, COUNT(DISTINCT o.id) as total_orders, COALESCE(SUM(p.total_amount), 0) as ltv FROM operation.clients c LEFT JOIN operation.orders o ON c.code_client = o.id_client LEFT JOIN operation.payments p ON o.id = p.id_order AND p.status = 'Payed' GROUP BY c.code_client, c.name, c.industry, c.region, c.status ORDER BY ltv DESC"
    return run_query(query)

@st.cache_data(ttl=60)
def get_logs():
    query = "SELECT changed_by, table_name, \"action\", old_data, new_data, changed_at FROM audit.audit_logs WHERE created_at <= NOW() - interval '7 days' ORDER BY created_at desc"
    return run_query(query)

@st.cache_data(ttl=60)
def get_environmental_anomalies():
    query = "WITH stats AS (SELECT id_buoy, AVG(salinitas) as avg_sal, STDDEV(salinitas) as std_sal, AVG(turbidity) as avg_tur, STDDEV(turbidity) as std_tur FROM operation.buoy_sensor_histories WHERE created_at >= NOW() - INTERVAL '30 days' GROUP BY id_buoy) SELECT h.id_buoy, h.created_at, h.salinitas, h.turbidity, (h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0) as sal_z_score, (h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0) as tur_z_score FROM operation.buoy_sensor_histories h JOIN stats s ON h.id_buoy = s.id_buoy WHERE h.created_at >= NOW() - INTERVAL '7 days' AND (ABS((h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0)) > 2 OR ABS((h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0)) > 2) ORDER BY h.created_at DESC"
    return run_query(query)

# --- SYSTEM SETTINGS ---
def init_settings_table():
    engine = get_engine()
    if not engine: return
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS operation.system_settings (key VARCHAR(50) PRIMARY KEY, value TEXT, description TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"))
            res = conn.execute(text("SELECT count(*) FROM operation.system_settings")).scalar()
            if res == 0:
                defaults = [("app_name", "MarineOS Dashboard", "Nama Aplikasi"), ("maintenance_mode", "false", "Mode Perawatan"), ("revenue_target_monthly", "5000000000", "Target Pendapatan"), ("churn_risk_threshold", "3", "Ambang Batas Churn"), ("theme_color", "#0ea5e9", "Warna Tema")]
                for k, v, d in defaults: conn.execute(text("INSERT INTO operation.system_settings (key, value, description) VALUES (:k, :v, :d)"), {"k": k, "v": v, "d": d})
    except Exception as e: print(f"Error initializing settings: {e}")

@st.cache_data(ttl=60)
def get_system_settings():
    init_settings_table()
    query = "SELECT key, value, description FROM operation.system_settings"
    df = run_query(query)
    if df.empty: return {}
    return pd.Series(df.value.values, index=df.key).to_dict()

def update_system_setting(key, value):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.system_settings SET value = :value, updated_at = NOW() WHERE key = :key"), {"value": str(value), "key": key})
            st.cache_data.clear(); return True
    except: return False

# --- USER MANAGEMENT ---
def get_all_users(): return run_query("SELECT u.code_user, um.id_user as username, u.role, u.status as user_status, um.status as account_status, um.last_login FROM operation.users u JOIN operation.user_managements um ON u.code_user = um.id_user ORDER BY u.code_user ASC")

def create_new_user(username, password, role):
    try:
        with get_engine().begin() as conn:
            if conn.execute(text("SELECT 1 FROM operation.users WHERE code_user = :u"), {"u": username}).fetchone(): return False, "Pengguna sudah ada."
            conn.execute(text("INSERT INTO operation.users (code_user, role, status) VALUES (:u, :r, 'Active')"), {"u": username, "r": role})
            conn.execute(text("INSERT INTO operation.user_managements (id_user, password, status) VALUES (:u, :p, 'Active')"), {"u": username, "p": password})
            return True, "Berhasil dibuat."
    except Exception as e: return False, str(e)

def update_user_status(username, new_status):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.users SET status = :s WHERE code_user = :u"), {"s": new_status, "u": username})
            conn.execute(text("UPDATE operation.user_managements SET status = :s WHERE id_user = :u"), {"s": new_status, "u": username})
            return True
    except: return False

def update_user_role(username, new_role):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.users SET role = :r WHERE code_user = :u"), {"r": new_role, "u": username})
            return True
    except: return False

def delete_user(username):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("DELETE FROM operation.user_managements WHERE id_user = :u"), {"u": username})
            conn.execute(text("DELETE FROM operation.users WHERE code_user = :u"), {"u": username})
            return True
    except: return False

def update_last_login_optimized(username, password):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.user_managements SET last_login = CURRENT_TIMESTAMP WHERE id_user = :u AND password = :p"), {"u": username, "p": password})
            return True
    except: return False

def update_password(username, old_pass, new_pass):
    if old_pass == new_pass: return False, "Kata sandi identik"
    try:
        with get_engine().begin() as conn:
            res = conn.execute(text("SELECT 1 FROM operation.user_managements WHERE id_user = :u AND password = :p"), {"u": username, "p": old_pass}).fetchone()
            if not res: return False, "Kredensial salah"
            conn.execute(text("UPDATE operation.user_managements SET password = :np, updated_at = CURRENT_TIMESTAMP WHERE id_user = :u"), {"np": new_pass.strip(), "u": username})
            return True, "Berhasil"
    except Exception as e: return False, str(e)

@st.cache_data(ttl=57)
def get_buoy_fleet():
    # 1. Fetch Active Buoys (User removed location, that's fine, View handles it)
    q1 = "SELECT b.code_buoy, b.status, '85%' as battery, MAX(bsh.created_at) as last_update FROM operation.buoys b LEFT JOIN operation.buoy_sensor_histories bsh ON b.code_buoy = bsh.id_buoy GROUP BY b.code_buoy, b.status"
    df1 = run_query(q1)
    
    # 2. Fetch Maintenance Buoys (from buoy_mtc_histories)
    # Alias id_buoy to code_buoy to match q1 and View expectations
    q2 = "SELECT id_buoy as code_buoy, 'Maintenance' as status, '0%' as battery, NULL::timestamp as last_update FROM operation.buoy_mtc_histories"
    df2 = run_query(q2)
    
    # Combine results
    frames = []
    if not df1.empty: frames.append(df1)
    if not df2.empty: frames.append(df2)
    
    if frames:
        return pd.concat(frames, ignore_index=True).sort_values('code_buoy')
    return pd.DataFrame()

@st.cache_data(ttl=60)
def get_buoy_history(buoy_id):
    query = "SELECT id_buoy, created_at, salinitas, turbidity, oxygen, density, current, tide FROM operation.buoy_sensor_histories WHERE id_buoy = :buoy_id ORDER BY created_at ASC"
    df = run_query(query, params={"buoy_id": buoy_id})
    return df

# --- ADVANCED INSIGHTS ---
@st.cache_data(ttl=60)
def get_operational_anomalies():
    """
    Detects operational inefficiencies:
    1. Ghost Operation: Status 'Operating' but Speed < 0.5 knots (faking work/engine issue).
    2. Unauthorized Move: Status not 'Operating'/'Moving' but Speed > 2 knots (drifting/unauthorized).
    """
    # Optimized: Filter by Time FIRST to leverage idx_vp_created_at
    query = """
    WITH recent_pos AS (
        SELECT id_vessel, speed, created_at, latitude, longitude
        FROM operation.vessel_positions
        WHERE created_at >= NOW() - INTERVAL '1 hour'
    )
    SELECT 
        vp.id_vessel,
        v.name,
        v.status as reported_status,
        vp.speed,
        vp.latitude,
        vp.longitude,
        vp.created_at,
        CASE 
            WHEN LOWER(v.status) = 'operating' AND vp.speed < 0.5 THEN 'Ghost Operation (Low Speed)'
            WHEN LOWER(v.status) IN ('idle', 'maintenance', 'docking') AND vp.speed > 2.0 THEN 'Unauthorized Movement'
            ELSE 'Normal'
        END as anomaly_type
    FROM recent_pos vp
    JOIN operation.vessels v ON vp.id_vessel = v.code_vessel
    WHERE 
        (LOWER(v.status) = 'operating' AND vp.speed < 0.5)
        OR 
        (LOWER(v.status) IN ('idle', 'maintenance', 'docking') AND vp.speed > 2.0)
    ORDER BY vp.created_at DESC
    LIMIT 20
    """
    return run_query(query)

@st.cache_data(ttl=3600)  # Increased TTL to 1 hour
def get_environmental_compliance_dashboard():
    """
    Aggregates environmental risk factors.
    Returns daily stats on high turbidity events reported by Buoys.
    """
    # Optimized: Removed MAX() to save some scans if not strictly needed, 
    # but kept for now. Date Trunc can slow things down on huge datasets without index expression, 
    # but idx_bsh_created helps filter range first.
    query = """
    SELECT 
        DATE_TRUNC('day', created_at) as monitor_date,
        COUNT(*) as total_readings,
        SUM(CASE WHEN turbidity > 50 THEN 1 ELSE 0 END) as high_turbidity_events,
        AVG(turbidity) as avg_turbidity
    FROM operation.buoy_sensor_histories
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY 1
    ORDER BY 1 DESC
    """
    return run_query(query)

@st.cache_data(ttl=3600) # Increased TTL to 1 hour
def get_client_reliability_scoring():
    """
    Scores clients based on:
    - Payment Speed (lower delay is better)
    - Total Monied Value (higher LTV is better)
    """
    # Optimized: Aggregation in CTE before Join
    query = """
    WITH payment_stats AS (
        SELECT 
            id_order,
            SUM(total_amount) as total_paid,
            MAX(payment_date) as last_payment_date
        FROM operation.payments
        WHERE status = 'Payed'
        GROUP BY 1
    ),
    client_metrics AS (
        SELECT 
            c.code_client,
            c.name,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(ps.total_paid), 0) as total_revenue,
            AVG(EXTRACT(DAY FROM (ps.last_payment_date - o.order_date))) as avg_payment_delay_days
        FROM operation.clients c
        JOIN operation.orders o ON c.code_client = o.id_client
        JOIN payment_stats ps ON CAST(o.id AS VARCHAR) = ps.id_order
        GROUP BY 1, 2
    )
    SELECT 
        code_client,
        name,
        total_revenue,
        COALESCE(avg_payment_delay_days, 0) as avg_payment_delay,
        (
            (total_revenue / 100000000) * 0.6
            - 
            (COALESCE(avg_payment_delay_days, 30) / 10) * 0.4
        ) as reliability_score
    FROM client_metrics
    ORDER BY reliability_score DESC
    """
    return run_query(query)

