import hashlib
from back.src.constants import ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM, ROLE_OPERATIONS

def get_notification_id(category, message, time_val):
    """Generate a stable ID for a notification based on its content."""
    raw = f"{category}|{message}|{str(time_val)}"
    return hashlib.md5(raw.encode()).hexdigest()

def generate_insights(fleet, financial, role, settings, clients_df):
    """
    Generate a list of insights/alerts based on system data.
    Returns a list of dicts: {'level': 'info'|'warning'|'success'|'error', 'message': str, 'category': str}
    """
    insights = []
    
    # --- Financial Insight (Admin/Finance/Marcom) ---
    if role in [ROLE_ADMIN, ROLE_FINANCE, ROLE_MARCOM]:
        rev = financial.get('total_revenue', 0)
        target = float(settings.get("revenue_target_monthly", 5000000000))
        
        # Revenue vs Target
        if target > 0:
            achieved = (rev / target) * 100
            if achieved < 50 and rev > 0:
                 insights.append({
                     "level": "error",
                     "message": f"📉 **Target Miss**: Only {achieved:.1f}% of monthly target (IDR {target/1e9:.1f}B) achieved. Push for closing deals.",
                     "category": "Financial"
                 })
            elif achieved > 100:
                 insights.append({
                     "level": "success",
                     "message": f"🎉 **Target Smashed**: Revenue is {achieved:.1f}% of target! Excellent performance.",
                     "category": "Financial"
                 })

        delta_rev = financial.get('delta_revenue', 0.0)
        if delta_rev < -10:
            insights.append({
                "level": "warning",
                "message": f"⚠️ **Revenue Alert**: Revenue dropped by {abs(delta_rev):.1f}% month-over-month. Investigate low order volume.",
                "category": "Financial"
            })
        elif delta_rev > 15:
            insights.append({
                "level": "success",
                "message": f"🚀 **Growth**: Strong revenue growth of {delta_rev:.1f}%! Maintain current acquisition strategy.",
                "category": "Financial"
            })
            
    # --- Churn Risk (from Clients) ---
    if not clients_df.empty and 'status' in clients_df.columns:
        threshold = int(settings.get("churn_risk_threshold", 3))
        inactive_count = len(clients_df[clients_df['status'] == 'Inactive'])
        if inactive_count >= threshold:
             insights.append({
                 "level": "error",
                 "message": f"🚨 **Churn Alert**: {inactive_count} clients are 'Inactive'. Risk threshold ({threshold}) exceeded. Contact CSM immediately.",
                 "category": "Clients"
             })

    # --- Fleet Insight (Common) ---
    maint_ratio = (fleet.get('maintenance', 0) / max(fleet.get('total_vessels', 1), 1)) * 100
    if maint_ratio > 30:
        insights.append({
            "level": "warning",
            "message": f"🛠️ **Fleet Efficiency**: High maintenance ratio ({maint_ratio:.0f}%). Operational capacity is impacted.",
            "category": "Fleet"
        })
    elif fleet.get('operating', 0) > (fleet.get('total_vessels', 1) * 0.8):
        insights.append({
            "level": "success",
            "message": f"✅ **High Utilization**: Over 80% of fleet is active. Consider expanding capacity if trend continues.",
            "category": "Fleet"
        })
        
    return insights
