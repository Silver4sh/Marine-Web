import pandas as pd
import numpy as np
import hashlib
from sklearn.metrics import r2_score
from streamlit.core.config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM

def get_notification_id(category, message, time_val):
    return hashlib.md5(f"{category}|{message}|{str(time_val)}".encode()).hexdigest()

def generate_insights(fleet, financial, role, settings, clients_df):
    insights = []
    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        rev = financial.get('total_revenue', 0)
        target = float(settings.get("revenue_target_monthly", 5000000000))
        if target > 0:
            achieved = (rev / target) * 100
            if achieved < 50 and rev > 0: insights.append({"level": "error", "message": f"📉 Target Meleset: Hanya {achieved:.1f}% tercapai.", "category": "Keuangan"})
            elif achieved > 100: insights.append({"level": "success", "message": f"🎉 Target Terlampaui: {achieved:.1f}%!", "category": "Keuangan"})
            
    if not clients_df.empty:
        inactive = len(clients_df[clients_df['status'] == 'Inactive'])
        if inactive >= int(settings.get("churn_risk_threshold", 3)): insights.append({"level": "error", "message": f"🚨 Peringatan Churn: {inactive} klien tidak aktif.", "category": "Klien"})
        
    maint_ratio = (fleet.get('maintenance', 0) / max(fleet.get('total_vessels', 1), 1)) * 100
    if maint_ratio > 30: insights.append({"level": "warning", "message": f"🛠️ Efisiensi Armada: {maint_ratio:.0f}% dalam perawatan.", "category": "Armada"})
    return insights

def calculate_advanced_forecast(df, months=6):
    if df.empty or 'revenue' not in df.columns or len(df) < 3: return pd.DataFrame()
    df = df.sort_values('month').copy()
    X = df['month'].map(pd.Timestamp.timestamp).values
    y = df['revenue'].values
    X_norm = (X - X[0]) / (X[-1] - X[0])
    
    try:
        p = np.poly1d(np.polyfit(X_norm, y, 1))
        r2 = r2_score(y, p(X_norm))
        best_model = {'model': p, 'r2': r2, 'type': 'poly', 'name': 'Linear'}
    except: best_model = {'r2': -999}
    
    # Simple forecast logic
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
