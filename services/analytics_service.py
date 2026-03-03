import pandas as pd
import numpy as np
from config.settings import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM


def generate_insights(fleet: dict, financial: dict, role: str, settings: dict, clients_df) -> list:
    """
    Generate system-wide alert insights based on cross-domain data.
    Returns a list of insight dicts (level, message, category).
    """
    insights = []

    # ── Financial alerts (Admin / Finance / MarCom only) ──────────────────────
    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        rev = float(financial.get("total_revenue", 0) or 0) if financial else 0.0
        target = float(settings.get("revenue_target_monthly", 5_000_000_000) or 5_000_000_000)
        if target > 0:
            achieved = (rev / target) * 100
            if achieved < 50 and rev > 0:
                insights.append({
                    "level": "error",
                    "message": f"📉 Target Meleset: Hanya {achieved:.1f}% dari target bulanan yang tercapai.",
                    "category": "FINANCIAL"
                })
            elif achieved > 100:
                insights.append({
                    "level": "success",
                    "message": f"🎉 Target Terlampaui: Pendapatan sudah {achieved:.1f}% dari target!",
                    "category": "FINANCIAL"
                })

    # ── Client churn alert ────────────────────────────────────────────────────
    if clients_df is not None and not clients_df.empty and "churn_risk" in clients_df.columns:
        inactive = len(clients_df[clients_df["churn_risk"] == "Tinggi"])
        threshold = int(settings.get("churn_risk_threshold", 3) or 3)
        if inactive >= threshold:
            insights.append({
                "level": "error",
                "message": f"🚨 Peringatan Churn: {inactive} klien berisiko tinggi perlu tindak lanjut.",
                "category": "CLIENTS"
            })

    # ── Fleet maintenance overload ────────────────────────────────────────────
    if fleet:
        total = max(fleet.get("total_vessels", 1), 1)
        maint = fleet.get("maintenance", 0)
        maint_ratio = (maint / total) * 100
        if maint_ratio > 30:
            insights.append({
                "level": "warning",
                "message": f"🛠️ Kelebihan Perawatan: {maint_ratio:.0f}% armada sedang dalam maintenance.",
                "category": "FLEET"
            })

    return insights


# ─────────────────────────────────────────────────────────────────────────────
# Forecast & Statistics
# ─────────────────────────────────────────────────────────────────────────────

def calculate_advanced_forecast(df: pd.DataFrame, months: int = 6) -> pd.DataFrame:
    """
    Linear regression forecast on monthly revenue data.
    Applies X-normalisation to avoid floating-point issues with large timestamps.
    Returns extended DataFrame with forecast rows (type='Prakiraan') and
    uncertainty bands (lower_bound / upper_bound).
    """
    if df is None or df.empty or "revenue" not in df.columns or len(df) < 3:
        return pd.DataFrame()

    df = df.sort_values("month").copy()

    try:
        X = df["month"].apply(lambda t: t.timestamp()).values.astype(float)
        y = df["revenue"].values.astype(float)

        x_range = X[-1] - X[0]
        if x_range == 0:
            return pd.DataFrame()

        X_norm  = (X - X[0]) / x_range
        coeffs  = np.polyfit(X_norm, y, 1)
        p       = np.poly1d(coeffs)
        model_name = "Regresi Linear"

    except Exception:
        return pd.DataFrame()

    step        = x_range / max(len(X) - 1, 1)
    future_dates = [df["month"].iloc[-1] + pd.DateOffset(months=i) for i in range(1, months + 1)]
    future_X_raw  = np.array([X[-1] + step * i for i in range(1, months + 1)])
    future_X_norm = (future_X_raw - X[0]) / x_range

    forecast = p(future_X_norm)
    uncert   = np.linspace(0.05, 0.20, months)

    return pd.DataFrame({
        "month":       future_dates,
        "revenue":     forecast,
        "type":        "Prakiraan",
        "lower_bound": forecast * (1 - uncert),
        "upper_bound": forecast * (1 + uncert),
        "model_name":  model_name,
    })


def calculate_moving_average(df: pd.DataFrame, col: str = "revenue", window: int = 3) -> pd.Series:
    """
    Rolling simple moving average over `window` periods.
    Returns a Series aligned to df's index; NaNs in warm-up period are forward-filled.
    """
    if df is None or df.empty or col not in df.columns:
        return pd.Series(dtype=float)
    return df[col].rolling(window=window, min_periods=1).mean().round(0)


def calculate_correlation(df: pd.DataFrame, numeric_cols: list = None) -> pd.DataFrame:
    """
    Compute Pearson correlation matrix.
    Only includes columns with non-zero variance to avoid NaN rows.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    if numeric_cols:
        valid_cols = [c for c in numeric_cols if c in df.columns]
        if len(valid_cols) < 2:
            return pd.DataFrame()
        df = df[valid_cols].copy()
    else:
        df = df.select_dtypes(include=[np.number]).copy()

    # Drop zero-variance columns
    df = df.loc[:, df.std() > 0]
    if df.shape[1] < 2:
        return pd.DataFrame()

    return df.corr(method="pearson").round(2)
