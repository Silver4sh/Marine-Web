import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

def calculate_advanced_forecast(df, months=6):
    """
    Auto-Adaptive Forecast: Tests multiple models and selects the best fit.
    Models:
    1. Linear (y = mx + c): For steady trends.
    2. Exponential (log(y) = mx + c): For rapid compounding growth.
    3. Polynomial (Degree 2): For accelerating/turning trends.
    """
    if df.empty or 'revenue' not in df.columns or len(df) < 3:
        return pd.DataFrame()

    df = df.sort_values('month').copy()
    
    # Prepare data
    df['timestamp'] = df['month'].map(pd.Timestamp.timestamp)
    X = df['timestamp'].values
    y = df['revenue'].values
    
    # Normalize X for numerical stability (start from 0)
    X_norm = (X - X[0]) / (X[-1] - X[0])
    
    results = {}
    
    # --- Model 1: Linear Regression ---
    try:
        coeffs_lin = np.polyfit(X_norm, y, 1)
        poly_lin = np.poly1d(coeffs_lin)
        y_pred_lin = poly_lin(X_norm)
        r2_lin = r2_score(y, y_pred_lin)
        results['Linear'] = {'model': poly_lin, 'r2': r2_lin, 'type': 'poly'}
    except:
        results['Linear'] = {'r2': -999}

    # --- Model 2: Exponential (Log-Linear) ---
    try:
        # Fit linear model to log(y)
        # Avoid log(0)
        y_log = np.log(y + 1) 
        coeffs_exp = np.polyfit(X_norm, y_log, 1)
        # y = exp(mx + c)
        y_pred_exp = np.exp(np.poly1d(coeffs_exp)(X_norm))
        r2_exp = r2_score(y, y_pred_exp)
        results['Exponential'] = {'coeffs': coeffs_exp, 'r2': r2_exp, 'type': 'exp'}
    except:
        results['Exponential'] = {'r2': -999}
        
    # --- Model 3: Polynomial (Degree 2) ---
    try:
        coeffs_poly = np.polyfit(X_norm, y, 2)
        poly_poly = np.poly1d(coeffs_poly)
        y_pred_poly = poly_poly(X_norm)
        r2_poly = r2_score(y, y_pred_poly)
        results['Polynomial'] = {'model': poly_poly, 'r2': r2_poly, 'type': 'poly'}
    except:
        results['Polynomial'] = {'r2': -999}

    # --- Select Best Model ---
    best_model_name = max(results, key=lambda k: results[k]['r2'])
    best_model = results[best_model_name]
    
    # --- Generate Forecast ---
    last_date = df['month'].iloc[-1]
    
    # Future X generation
    # Time step is roughly 30 days
    last_ts = X[-1]
    step = (X[-1] - X[0]) / (len(X) - 1)
    
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, months + 1)]
    future_X_raw = [last_ts + (step * i) for i in range(1, months + 1)]
    # Normalize with same scale as training
    future_X_norm = (np.array(future_X_raw) - X[0]) / (X[-1] - X[0])
    
    if best_model['type'] == 'poly':
        forecast_values = best_model['model'](future_X_norm)
    else: # exp
        coeffs = best_model['coeffs']
        forecast_values = np.exp(np.poly1d(coeffs)(future_X_norm))
        
    # --- Uncertainty / Confidence Interval (Simplified) ---
    # We use roughly 10-20% margin expanding over time to represent uncertainty
    # This is a heuristic since proper CI for non-linear models is complex for this scope
    uncertainty_factor = np.linspace(0.05, 0.20, num=months) # 5% to 20%
    
    forecast_df = pd.DataFrame({
        'month': future_dates,
        'revenue': forecast_values,
        'type': 'Forecast',
        'lower_bound': forecast_values * (1 - uncertainty_factor),
        'upper_bound': forecast_values * (1 + uncertainty_factor),
        'model_name': best_model_name
    })
    
    # Ensure no negative revenue
    forecast_df['revenue'] = forecast_df['revenue'].apply(lambda x: max(x, 0))
    forecast_df['lower_bound'] = forecast_df['lower_bound'].apply(lambda x: max(x, 0))
    
    return forecast_df
