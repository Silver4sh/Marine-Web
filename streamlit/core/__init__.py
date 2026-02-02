from .config import (
    ROLE_OPERATIONS, ROLE_MARCOM, ROLE_ADMIN, ROLE_FINANCE,
    load_css, inject_custom_css
)

from .utils import (
    load_html, render_metric_card, get_status_color, 
    create_google_arrow_icon, create_circle_icon, apply_chart_style,
    render_vessel_card, render_vessel_list_column, render_vessel_detail_section
)

from .database import (
    get_connection, run_query, get_fleet_status, get_vessel_position, 
    get_path_vessel, get_data_water, get_financial_metrics, get_revenue_analysis, 
    get_order_stats, get_clients_summary, get_logs, get_vessel_list, 
    get_revenue_by_service, get_fleet_daily_activity, get_vessel_utilization_stats, 
    get_revenue_cycle_metrics, get_environmental_anomalies, get_logistics_performance, 
    get_system_settings, update_system_setting, get_all_users, create_new_user, 
    update_user_status, update_user_role, delete_user, update_last_login_optimized, 
    update_password,get_client_stats
)

from .analysis import (
    get_notification_id, generate_insights, calculate_advanced_forecast
)

from .visualizations import (
    add_history_path_to_map, render_map_content, page_heatmap
)
