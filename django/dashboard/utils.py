from django.db import connection
import pandas as pd
import numpy as np

def run_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=columns)

def get_financial_metrics():
    query = "SELECT COALESCE(SUM(total_amount), 0) as total_revenue, COUNT(DISTINCT id_order) as completed_orders FROM operation.payments WHERE status = 'Completed'"
    df = run_query(query)
    if df.empty: return {"total_revenue": 0, "completed_orders": 0, "delta_revenue": 0.0}
    current = df.iloc[0]
    metrics = {"total_revenue": float(current["total_revenue"]), "completed_orders": int(current["completed_orders"]), "delta_revenue": 0.0}
    return metrics

def get_revenue_analysis():
    query = "SELECT DATE_TRUNC('month', payment_date) as month, SUM(total_amount) as revenue FROM operation.payments WHERE status = 'Completed' GROUP BY 1 ORDER BY 1 DESC"
    return run_query(query)

def get_revenue_cycle_metrics():
    query = "SELECT DATE_TRUNC('month', o.order_date) as month, AVG(EXTRACT(DAY FROM (p.payment_date - o.order_date))) as avg_days_to_cash, SUM(p.total_amount) as realized_revenue, SUM(CASE WHEN p.status = 'Completed' THEN 1 ELSE 0 END) as paid_count, COUNT(o.code_order) as total_orders FROM operation.orders o JOIN operation.payments p ON o.code_order = p.id_order WHERE o.order_date >= NOW() - INTERVAL '6 months' GROUP BY 1 ORDER BY 1 DESC"
    return run_query(query)

def get_order_stats():
    query = "SELECT COUNT(*) as total_orders, SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed, SUM(CASE WHEN status = 'In Completed' THEN 1 ELSE 0 END) as in_completed, SUM(CASE WHEN status = 'On Progress' THEN 1 ELSE 0 END) as on_progress, SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed FROM operation.orders"
    df = run_query(query)
    if df.empty: return {"total_orders": 0, "completed": 0, "in_completed": 0, "on_progress": 0, "failed": 0}
    return df.astype(int).iloc[0].to_dict()

def get_data_water():
    query = "SELECT bsh.id_buoy, s.latitude, s.longitude, bsh.salinitas as salinitas, bsh.turbidity as turbidity, bsh.current as current, bsh.oxygen as oxygen, bsh.tide as tide, bsh.density as density, bsh.created_at as latest_timestamp FROM operation.buoy_sensor_histories bsh JOIN operation.buoys b ON b.code_buoy = bsh.id_buoy JOIN operation.sites s ON s.code_site = b.id_site ORDER BY bsh.created_at DESC"
    return run_query(query)

def get_environmental_anomalies():
    query = "WITH stats AS (SELECT id_buoy, AVG(salinitas) as avg_sal, STDDEV(salinitas) as std_sal, AVG(turbidity) as avg_tur, STDDEV(turbidity) as std_tur FROM operation.buoy_sensor_histories WHERE created_at >= NOW() - INTERVAL '30 days' GROUP BY id_buoy) SELECT h.id_buoy, h.created_at, h.salinitas, h.turbidity, (h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0) as sal_z_score, (h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0) as tur_z_score FROM operation.buoy_sensor_histories h JOIN stats s ON h.id_buoy = s.id_buoy WHERE h.created_at >= NOW() - INTERVAL '7 days' AND (ABS((h.salinitas - s.avg_sal) / NULLIF(s.std_sal, 0)) > 2 OR ABS((h.turbidity - s.avg_tur) / NULLIF(s.std_tur, 0)) > 2) ORDER BY h.created_at DESC"
    return run_query(query)

def get_buoy_fleet():
    q1 = "SELECT b.code_buoy, b.status, '85%' as battery, MAX(bsh.created_at) as last_update, s.name as location FROM operation.buoys b LEFT JOIN operation.buoy_sensor_histories bsh ON b.code_buoy = bsh.id_buoy LEFT JOIN operation.sites s ON b.id_site = s.code_site GROUP BY b.code_buoy, b.status, s.name"
    df = run_query(q1)
    return df

def get_buoy_history(buoy_id):
    query = "SELECT id_buoy, created_at, salinitas, turbidity, oxygen, density, current, tide FROM operation.buoy_sensor_histories WHERE id_buoy = %s ORDER BY created_at ASC"
    return run_query(query, params=[buoy_id])

def get_client_stats():
    query = "SELECT COUNT(code_client) as total_clients, SUM(CASE WHEN created_at <= NOW() - INTERVAL '21 days' and status = 'Active' THEN 1 ELSE 0 END) as new_clients,  SUM(CASE WHEN created_at <= NOW() - INTERVAL '21 days' and status <> 'Active' THEN 1 ELSE 0 END) as deactive_clients FROM operation.clients"
    df = run_query(query)
    if df.empty: return {"total_clients": 0, "new_clients": 0, "deactive_clients": 0}
    return {"total_clients": int(df.iloc[0]["total_clients"]), "new_clients": int(df.iloc[0]["new_clients"]), "deactive_clients": int(df.iloc[0]["deactive_clients"])}

def calculate_advanced_forecast(df, months=6):
    if df.empty or 'revenue' not in df.columns or len(df) < 3: return pd.DataFrame()
    df = df.sort_values('month').copy()
    
    if not pd.api.types.is_datetime64_any_dtype(df['month']):
        df['month'] = pd.to_datetime(df['month'])

    X = df['month'].map(pd.Timestamp.timestamp).values
    y = df['revenue'].astype(float).values
    X_norm = (X - X[0]) / (X[-1] - X[0])
    
    try:
        p = np.poly1d(np.polyfit(X_norm, y, 1))
        best_model = {'model': p, 'type': 'poly', 'name': 'Linear'}
    except: 
        return pd.DataFrame()
    
    last_ts = X[-1]
    step = (X[-1] - X[0]) / (len(X) - 1)
    future_dates = [df['month'].iloc[-1] + pd.DateOffset(months=i) for i in range(1, months + 1)]
    future_X_raw = [last_ts + (step * i) for i in range(1, months + 1)]
    future_X_norm = (np.array(future_X_raw) - X[0]) / (X[-1] - X[0])
    
    forecast_values = best_model['model'](future_X_norm)
    uncert = np.linspace(0.05, 0.20, months)
    
    return pd.DataFrame({
        'month': future_dates, 'revenue': forecast_values, 'type': 'Prakiraan',
        'lower_bound': forecast_values * (1 - uncert), 'upper_bound': forecast_values * (1 + uncert),
        'model_name': best_model['name']
    })

def calculate_correlation(df, numeric_cols=None):
    if df.empty: return pd.DataFrame()
    
    if numeric_cols:
        df = df[numeric_cols]
    else:
        df = df.select_dtypes(include=[np.number])
        
    if df.shape[1] < 2: return pd.DataFrame()
    
    corr_matrix = df.corr(method='pearson').round(2)
    return corr_matrix

def get_all_surveys():
    # Adjusted to join with standard Django auth_user table
    query = "SELECT s.id, s.project_name, s.code_report, s.date_survey, s.comment, si.name as site_name, v.name as vessel_name, u.username as surveyor_name FROM operation.surveys s LEFT JOIN operation.sites si ON s.id_site = si.code_site LEFT JOIN operation.vessels v ON s.id_vessel = v.code_vessel LEFT JOIN auth_user u ON s.id_user = u.id ORDER BY s.date_survey DESC"
    return run_query(query)

# --- ADVANCED INSIGHTS (Ported from Streamlit) ---

def get_operational_anomalies():
    """
    Detects operational inefficiencies:
    1. Ghost Operation: Status 'Operating' but Speed < 0.5 knots (faking work/engine issue).
    2. Unauthorized Move: Status not 'Operating'/'Moving' but Speed > 2 knots (drifting/unauthorized).
    """
    query = """
    WITH recent_pos AS (
        SELECT id_vessel, speed, created_at, latitude, longitude
        FROM operation.vessel_positions
        WHERE created_at >= NOW() - INTERVAL '24 hour'
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

def get_environmental_compliance_dashboard():
    """
    Aggregates environmental risk factors.
    Returns daily stats on high turbidity events reported by Buoys.
    """
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

def get_client_reliability_scoring():
    """
    Scores clients based on:
    - Payment Speed (lower delay is better)
    - Total Monied Value (higher LTV is better)
    """
    query = """
    WITH payment_stats AS (
        SELECT 
            id_order,
            SUM(total_amount) as total_paid,
            MAX(payment_date) as last_payment_date
        FROM operation.payments
        WHERE status = 'Completed'
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
        JOIN payment_stats ps ON o.code_order = ps.id_order
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

def get_vessel_utilization_stats():
    query = "SELECT v.name as vessel_name, SUM(EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600) as total_hours, SUM(CASE WHEN LOWER(va.status) NOT IN ('idle', 'maintenance', 'docking') THEN EXTRACT(EPOCH FROM (COALESCE(va.end_date, NOW()) - va.start_date))/3600 ELSE 0 END) as productive_hours FROM operation.vessel_activities va JOIN operation.vessels v ON va.id_vessel = v.code_vessel WHERE va.start_date >= NOW() - INTERVAL '30 days' GROUP BY v.name"
    df = run_query(query)
    if not df.empty:
        df['utilization_rate'] = (df['productive_hours'] / df['total_hours']) * 100
        df['utilization_rate'] = df['utilization_rate'].fillna(0)
    return df

def get_logistics_performance():
    query = "SELECT destination, COUNT(*) as total_trips, AVG(EXTRACT(EPOCH FROM (actual_delivery_date - scheduled_delivery_date))/3600) as avg_delay_hours, SUM(CASE WHEN actual_delivery_date > scheduled_delivery_date THEN 1 ELSE 0 END) as late_trips FROM operation.orders WHERE actual_delivery_date IS NOT NULL AND scheduled_delivery_date IS NOT NULL GROUP BY destination ORDER BY avg_delay_hours DESC"
    return run_query(query)

def create_survey_report(data):
    try:
        query = "INSERT INTO operation.surveys (project_name, code_report, id_site, id_vessel, id_user, date_survey, comment, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"
        params = [
            data['project_name'], data['code_report'], data['id_site'], 
            data['id_vessel'], data['id_user'], data['date_survey'], data['comment']
        ]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
        return True, "Laporan berhasil dibuat."
    except Exception as e:
        return False, str(e)

# Added missed functions
def get_clients_summary():
    query = "SELECT c.code_client, c.name, c.industry, c.region, c.status, COUNT(DISTINCT o.code_order) as total_orders, COALESCE(SUM(p.total_amount), 0) as ltv FROM operation.clients c LEFT JOIN operation.orders o ON c.code_client = o.id_client LEFT JOIN operation.payments p ON o.code_order = p.id_order AND p.status = 'Completed' GROUP BY c.code_client, c.name, c.industry, c.region, c.status ORDER BY ltv DESC"
    return run_query(query)

def get_system_logs(limit=50):
    query = "SELECT changed_by, table_name, action, old_data, new_data, changed_at FROM audit.audit_logs ORDER BY changed_at DESC LIMIT %s"
    return run_query(query, params=[limit])

def get_notification_items():
    # Mocking notification generation
    notifications = []
    
    # Check Fleet
    fleet = get_buoy_fleet()
    if not fleet.empty and 'status' in fleet.columns:
        inactive = fleet[fleet['status'] != 'Active']
        if not inactive.empty:
            notifications.append({
                'category': 'FLEET',
                'message': f"{len(inactive)} Buoy dalam kondisi Tidak Aktif/Maintenance.",
                'time': 'Hari Ini',
                'status': 'inbox'
            })
            
    # Check revenue (Example)
    rev = get_financial_metrics()
    if rev.get('delta_revenue', 0) < 0:
         notifications.append({
                'category': 'FINANCIAL',
                'message': "Pendapatan turun dibandingkan periode sebelumnya.",
                'time': 'Hari Ini',
                'status': 'inbox'
            })
            
    return notifications
