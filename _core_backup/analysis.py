import pandas as pd
import numpy as np
import hashlib
from sklearn.metrics import r2_score
from .config import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM


def get_notification_id(category, message, time_val):
    return hashlib.md5(f"{category}|{message}|{str(time_val)}".encode()).hexdigest()


def generate_insights(fleet, financial, role, settings, clients_df):
    """Generate system insights.
    NOTE: category keys must match the icon/display dict in notifications.py:
    FLEET | FINANCIAL | CLIENTS | SYSTEM | ALERT
    """
    insights = []

    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        rev = financial.get('total_revenue', 0) if financial else 0
        target = float(settings.get("revenue_target_monthly", 5000000000) if settings else 5000000000)
        if target > 0:
            achieved = (rev / target) * 100
            if achieved < 50 and rev > 0:
                insights.append({
                    "level": "error",
                    "message": f"📉 Target Meleset: Hanya {achieved:.1f}% tercapai.",
                    "category": "FINANCIAL"
                })
            elif achieved > 100:
                insights.append({
                    "level": "success",
                    "message": f"🎉 Target Terlampaui: {achieved:.1f}%!",
                    "category": "FINANCIAL"
                })

    if clients_df is not None and not clients_df.empty and 'status' in clients_df.columns:
        inactive = len(clients_df[clients_df['status'] == 'Inactive'])
        threshold = int(settings.get("churn_risk_threshold", 3) if settings else 3)
        if inactive >= threshold:
            insights.append({
                "level": "error",
                "message": f"🚨 Peringatan Churn: {inactive} klien tidak aktif.",
                "category": "CLIENTS"
            })

    if fleet:
        maint_ratio = (fleet.get('maintenance', 0) / max(fleet.get('total_vessels', 1), 1)) * 100
        if maint_ratio > 30:
            insights.append({
                "level": "warning",
                "message": f"🛠️ Efisiensi Armada: {maint_ratio:.0f}% dalam perawatan.",
                "category": "FLEET"
            })

    return insights


def calculate_advanced_forecast(df, months=6):
    """Forecast future revenue using linear regression.
    Returns empty DataFrame on any failure instead of crashing.
    """
    if df is None or df.empty or 'revenue' not in df.columns or len(df) < 3:
        return pd.DataFrame()

    df = df.sort_values('month').copy()

    try:
        X = df['month'].apply(lambda t: t.timestamp()).values.astype(float)
        y = df['revenue'].values.astype(float)

        x_range = X[-1] - X[0]
        if x_range == 0:
            return pd.DataFrame()

        X_norm = (X - X[0]) / x_range

        coeffs = np.polyfit(X_norm, y, 1)
        p = np.poly1d(coeffs)
        r2 = r2_score(y, p(X_norm))
        model_name = 'Regresi Linear'

    except Exception:
        return pd.DataFrame()

    # Build future dates & normalize
    step = x_range / max(len(X) - 1, 1)
    future_dates = [df['month'].iloc[-1] + pd.DateOffset(months=i) for i in range(1, months + 1)]
    future_X_raw = np.array([X[-1] + (step * i) for i in range(1, months + 1)])
    future_X_norm = (future_X_raw - X[0]) / x_range

    forecast_values = p(future_X_norm)
    uncert = np.linspace(0.05, 0.20, months)

    return pd.DataFrame({
        'month': future_dates,
        'revenue': forecast_values,
        'type': 'Prakiraan',
        'lower_bound': forecast_values * (1 - uncert),
        'upper_bound': forecast_values * (1 + uncert),
        'model_name': model_name
    })


def calculate_correlation(df, numeric_cols=None):
    """
    Computes Pearson correlation matrix for specified numeric columns.
    Returns a formatted dataframe suitable for heatmap visualization.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    if numeric_cols:
        valid_cols = [c for c in numeric_cols if c in df.columns]
        if len(valid_cols) < 2:
            return pd.DataFrame()
        df = df[valid_cols]
    else:
        df = df.select_dtypes(include=[np.number])

    if df.shape[1] < 2:
        return pd.DataFrame()

    # Drop zero-variance columns (corr would be NaN)
    df = df.loc[:, df.std() > 0]
    if df.shape[1] < 2:
        return pd.DataFrame()

    corr_matrix = df.corr(method='pearson').round(2)
    return corr_matrix
