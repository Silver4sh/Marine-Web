import pandas as pd
import numpy as np
import hashlib
from sklearn.metrics import r2_score
from dashboard.config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS

def get_notification_id(category, message, time_val):
    """Generate ID stabil untuk notifikasi."""
    raw = f"{category}|{message}|{str(time_val)}"
    return hashlib.md5(raw.encode()).hexdigest()

def generate_insights(fleet, financial, role, settings, clients_df):
    """
    Menghasilkan daftar wawasan/alert berdasarkan data sistem.
    """
    insights = []
    
    # --- Wawasan Keuangan ---
    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        rev = financial.get('total_revenue', 0)
        target = float(settings.get("revenue_target_monthly", 5000000000))
        
        if target > 0:
            achieved = (rev / target) * 100
            if achieved < 50 and rev > 0:
                 insights.append({
                     "level": "error",
                     "message": f"📉 **Target Meleset**: Hanya {achieved:.1f}% target bulanan (Rp {target/1e9:.1f}M) tercapai. Tingkatkan penjualan.",
                     "category": "Keuangan"
                 })
            elif achieved > 100:
                 insights.append({
                     "level": "success",
                     "message": f"🎉 **Target Terlampaui**: Pendapatan {achieved:.1f}% dari target! Kinerja luar biasa.",
                     "category": "Keuangan"
                 })

        delta_rev = financial.get('delta_revenue', 0.0)
        if delta_rev < -10:
            insights.append({
                "level": "warning",
                "message": f"⚠️ **Peringatan Pendapatan**: Pendapatan turun {abs(delta_rev):.1f}% bulan-ke-bulan. Selidiki volume pesanan.",
                "category": "Keuangan"
            })
        elif delta_rev > 15:
            insights.append({
                "level": "success",
                "message": f"🚀 **Pertumbuhan**: Pertumbuhan pendapatan kuat sebesar {delta_rev:.1f}%! Pertahankan strategi.",
                "category": "Keuangan"
            })
            
    # --- Risiko Churn ---
    if not clients_df.empty and 'status' in clients_df.columns:
        threshold = int(settings.get("churn_risk_threshold", 3))
        inactive_count = len(clients_df[clients_df['status'] == 'Inactive'])
        if inactive_count >= threshold:
             insights.append({
                 "level": "error",
                 "message": f"🚨 **Peringatan Churn**: {inactive_count} klien 'Tidak Aktif'. Ambang batas ({threshold}) terlampaui. Hubungi CSM segera.",
                 "category": "Klien"
             })

    # --- Wawasan Armada ---
    total_vessel = max(fleet.get('total_vessels', 1), 1)
    maint_ratio = (fleet.get('maintenance', 0) / total_vessel) * 100
    
    if maint_ratio > 30:
        insights.append({
            "level": "warning",
            "message": f"🛠️ **Efisiensi Armada**: Rasio pemeliharaan tinggi ({maint_ratio:.0f}%). Kapasitas operasional terdampak.",
            "category": "Armada"
        })
    elif fleet.get('operating', 0) > (total_vessel * 0.8):
        insights.append({
            "level": "success",
            "message": f"✅ **Utilisasi Tinggi**: Lebih dari 80% armada aktif. Pertimbangkan penambahan kapasitas.",
            "category": "Armada"
        })
        
    return insights

def calculate_advanced_forecast(df, months=6):
    """
    Prakiraan Otomatis: Menguji beberapa model dan memilih yang terbaik.
    """
    if df.empty or 'revenue' not in df.columns or len(df) < 3:
        return pd.DataFrame()

    df = df.sort_values('month').copy()
    df['timestamp'] = df['month'].map(pd.Timestamp.timestamp)
    X = df['timestamp'].values
    y = df['revenue'].values
    
    X_norm = (X - X[0]) / (X[-1] - X[0])
    results = {}
    
    # Model 1: Linear
    try:
        coeffs_lin = np.polyfit(X_norm, y, 1)
        poly_lin = np.poly1d(coeffs_lin)
        y_pred_lin = poly_lin(X_norm)
        r2_lin = r2_score(y, y_pred_lin)
        results['Linear'] = {'model': poly_lin, 'r2': r2_lin, 'type': 'poly'}
    except: results['Linear'] = {'r2': -999}

    # Model 2: Exponential
    try:
        y_log = np.log(y + 1) 
        coeffs_exp = np.polyfit(X_norm, y_log, 1)
        y_pred_exp = np.exp(np.poly1d(coeffs_exp)(X_norm))
        r2_exp = r2_score(y, y_pred_exp)
        results['Exponential'] = {'coeffs': coeffs_exp, 'r2': r2_exp, 'type': 'exp'}
    except: results['Exponential'] = {'r2': -999}
        
    # Model 3: Polynomial
    try:
        coeffs_poly = np.polyfit(X_norm, y, 2)
        poly_poly = np.poly1d(coeffs_poly)
        y_pred_poly = poly_poly(X_norm)
        r2_poly = r2_score(y, y_pred_poly)
        results['Polynomial'] = {'model': poly_poly, 'r2': r2_poly, 'type': 'poly'}
    except: results['Polynomial'] = {'r2': -999}

    best_model_name = max(results, key=lambda k: results[k]['r2'])
    best_model = results[best_model_name]
    
    last_date = df['month'].iloc[-1]
    last_ts = X[-1]
    step = (X[-1] - X[0]) / (len(X) - 1)
    
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, months + 1)]
    future_X_raw = [last_ts + (step * i) for i in range(1, months + 1)]
    future_X_norm = (np.array(future_X_raw) - X[0]) / (X[-1] - X[0])
    
    if best_model['type'] == 'poly':
        forecast_values = best_model['model'](future_X_norm)
    else: 
        coeffs = best_model['coeffs']
        forecast_values = np.exp(np.poly1d(coeffs)(future_X_norm))
        
    uncertainty_factor = np.linspace(0.05, 0.20, num=months)
    
    forecast_df = pd.DataFrame({
        'month': future_dates,
        'revenue': forecast_values,
        'type': 'Prakiraan',
        'lower_bound': forecast_values * (1 - uncertainty_factor),
        'upper_bound': forecast_values * (1 + uncertainty_factor),
        'model_name': best_model_name
    })
    
    forecast_df['revenue'] = forecast_df['revenue'].apply(lambda x: max(x, 0))
    forecast_df['lower_bound'] = forecast_df['lower_bound'].apply(lambda x: max(x, 0))
    
    return forecast_df
