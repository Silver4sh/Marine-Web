from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Vessels, Orders, AuditLogs, Surveis, Sites, Buoys
import json
import pandas as pd
from django.http import JsonResponse, HttpResponse
from .utils import (
    get_financial_metrics, get_revenue_analysis, get_order_stats,
    get_client_stats, calculate_advanced_forecast, calculate_correlation,
    get_revenue_cycle_metrics, get_data_water, get_buoy_fleet, get_buoy_history,
    get_operational_anomalies, get_environmental_compliance_dashboard,
    get_vessel_utilization_stats, get_logistics_performance, get_all_surveys,
    create_survey_report, get_clients_summary, get_system_logs, get_notification_items
)
from .ai_analyst import MarineAIAnalyst

# ... (Auth & Dashboard Views remain same as before, see Step 569/562 for reference) ...
# I will output the FULL file to be safe, reusing previous content 

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'dashboard/login.html', {'error': 'Invalid credentials'})
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    return redirect('dashboard')

@login_required
def dashboard(request):
    total_vessels = Vessels.objects.count()
    active_vessels = Vessels.objects.filter(status='Active').count()
    total_orders = Orders.objects.count()
    active_orders = Orders.objects.exclude(status='Complited').count() 
    total_sites = Sites.objects.count()
    recent_logs = AuditLogs.objects.order_by('-changed_at')[:5]

    # Advanced Analytics
    
    anomalies = get_operational_anomalies()
    anomalies_list = anomalies.to_dict(orient='records') if not anomalies.empty else []
    
    compliance = get_environmental_compliance_dashboard()
    compliance_json = compliance.to_json(orient='records', date_format='iso') if not compliance.empty else "[]"

    context = {
        'total_vessels': total_vessels,
        'active_vessels': active_vessels,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'total_sites': total_sites,
        'recent_logs': recent_logs,
        'anomalies': anomalies_list,
        'compliance_data': compliance_json,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def insights(request):
    return redirect('analytics')

@login_required
def get_map_data(request):
    sites = Sites.objects.all().values('code_site', 'name', 'latitude', 'longitude', 'status', 'type')
    buoys = Buoys.objects.all().values('code_buoy', 'latitude', 'longitude', 'status')
    return JsonResponse({
        'sites': list(sites), 
        'buoys': list(buoys)
    })

@login_required
def analytics(request):
    fin = get_financial_metrics()
    orders = get_order_stats()
    clients = get_client_stats()
    rev_df = get_revenue_analysis()
    forecast_json = "[]"
    
    if not rev_df.empty:
        rev_df['type'] = 'Aktual'
        rev_df['month_str'] = rev_df['month'].astype(str)
        forecast_df = calculate_advanced_forecast(rev_df, months=6)
        if not forecast_df.empty:
             forecast_df['month_str'] = forecast_df['month'].astype(str)
             combined = pd.concat([rev_df, forecast_df])
             forecast_json = combined.to_json(orient='records', date_format='iso')

    cycle_df = get_revenue_cycle_metrics()
    corr_matrix_json = "[]"
    corr_insights = []
    
    if not cycle_df.empty:
        corr_data = cycle_df[['avg_days_to_cash', 'realized_revenue', 'total_orders', 'paid_count']].rename(columns={'avg_days_to_cash': 'Hari Bayar', 'realized_revenue': 'Pendapatan', 'total_orders': 'Total Order', 'paid_count': 'Lunas'})
        corr_matrix = calculate_correlation(corr_data)
        if not corr_matrix.empty:
            corr_matrix_json = corr_matrix.to_json(orient='split')
            corr_insights = MarineAIAnalyst.analyze_correlations(corr_matrix)['insights']

    ai_fin = MarineAIAnalyst.analyze_financials(fin)
    
    # Advanced Analytics
    
    # Utilization
    util_df = get_vessel_utilization_stats()
    util_json = util_df.to_json(orient='records') if not util_df.empty else "[]"
    
    # Logistics
    log_df = get_logistics_performance()
    log_list = log_df.head(5).to_dict(orient='records') if not log_df.empty else []

    context = {
        'fin': fin, 'orders': orders, 'clients': clients,
        'forecast_data': forecast_json, 'corr_matrix': corr_matrix_json,
        'corr_insights': corr_insights, 'ai_insights': ai_fin['insights'],
        'utilization_data': util_json,
        'logistics_data': log_list
    }
    return render(request, 'dashboard/analytics.html', context)

@login_required
def environment(request):
    # 1. Fetch Heatmap Data
    water_df = get_data_water()
    heatmap_json = "[]"
    ai_insights = []
    
    if not water_df.empty:
        # Convert timestamps for JSON
        water_df['latest_timestamp'] = water_df['latest_timestamp'].astype(str)
        heatmap_json = water_df.to_json(orient='records')
        
        # AI Analysis
        ai_env = MarineAIAnalyst.analyze_environment(water_df[water_df['salinitas'] > 40] if 'salinitas' in water_df.columns else pd.DataFrame())
        ai_insights = ai_env['insights']

    # 2. Fetch Buoys
    buoy_df = get_buoy_fleet()
    buoy_list = []
    total, active, maint = 0, 0, 0
    
    if not buoy_df.empty:
        total = len(buoy_df)
        active = len(buoy_df[buoy_df['status'] == 'Active'])
        maint = total - active
        buoy_list = buoy_df.to_dict(orient='records')

    context = {
        'heatmap_data': heatmap_json,
        'ai_insights': ai_insights,
        'buoy_list': buoy_list,
        'total_buoys': total,
        'active_buoys': active,
        'maint_buoys': maint,
        # Metrics
        'avg_salinity': water_df['salinitas'].mean() if not water_df.empty else 0,
        'avg_turbidity': water_df['turbidity'].mean() if not water_df.empty else 0,
        'avg_oxygen': water_df['oxygen'].mean() if not water_df.empty else 0,
        'alert_count': len(ai_insights)
    }
    return render(request, 'dashboard/environment.html', context)

@login_required
def buoy_detail(request, buoy_id):
    # Fetch history
    hist_df = get_buoy_history(buoy_id)
    
    if not hist_df.empty:
        hist_df['created_at'] = hist_df['created_at'].astype(str)
        hist_data = hist_df.to_dict(orient='records')
        hist_json = hist_df.to_json(orient='records')
        return render(request, 'dashboard/partials/buoy_detail_modal.html', {
            'hist_data': hist_data, 
            'hist_json': hist_json,
            'buoy_id': buoy_id
        })
    else:
        return HttpResponse("<div class='p-4 text-center'>Tidak ada data historis.</div>")

@login_required
def survey_list(request):
    from .utils import get_all_surveys
    # Need to fetch sites and vessels for the modal dropdowns
    sites = Sites.objects.filter(status='Active').values('code_site', 'name')
    vessels = Vessels.objects.filter(status='Active').values('code_vessel', 'name')
    
    surveys = get_all_surveys()
    surveys_list = surveys.to_dict(orient='records') if not surveys.empty else []
    
    context = {
        'surveys': surveys_list,
        'sites': sites,
        'vessels': vessels
    }
    return render(request, 'dashboard/survey.html', context)

@login_required
def create_survey(request):
    from .utils import create_survey_report
    if request.method == 'POST':
        data = {
            "project_name": request.POST.get('project_name'),
            "code_report": request.POST.get('code_report'),
            "id_site": request.POST.get('id_site'),
            "id_vessel": request.POST.get('id_vessel'),
            "id_user": request.user.id, # Using Logged in Django User ID
            "date_survey": request.POST.get('date_survey'),
            "comment": request.POST.get('comment')
        }
        
        success, msg = create_survey_report(data)
        if success:
            # Could add a flash message here
            return redirect('survey_list')
        else:
            # Handle error
            return HttpResponse(f"Error: {msg}")
            
    return redirect('survey_list')

@login_required
def clients(request):
    from .utils import get_clients_summary
    from .ai_analyst import MarineAIAnalyst
    import numpy as np

    df = get_clients_summary()
    
    # Enrich Data (Growth Matrix Logic)
    if not df.empty:
        df['ltv'] = df['ltv'].astype(float)
        # Churn Risk Logic
        conditions = [
            (df['total_orders'] >= 4),
            (df['total_orders'] >= 2),
            (df['total_orders'] < 2)
        ]
        choices = ['Rendah', 'Menengah', 'Tinggi']
        df['churn_risk'] = np.select(conditions, choices, default='Menengah')
    else:
        df['churn_risk'] = []

    # AI Analysis
    ai_analysis = MarineAIAnalyst.analyze_clients(df)
    
    # Metrics
    total_clients = len(df)
    high_value_sum = df[df['ltv'] > 3000000000]['ltv'].sum() / 1000000000 if not df.empty else 0
    at_risk = len(df[df['churn_risk'] == 'Tinggi']) if not df.empty else 0
    avg_projects = df['total_orders'].mean() if not df.empty else 0

    context = {
        'clients': df.to_dict(orient='records'),
        'clients_json': df.to_json(orient='records'),
        'total_clients': total_clients,
        'high_value_sum': high_value_sum,
        'at_risk_count': at_risk,
        'avg_projects': avg_projects,
        'ai_insights': ai_analysis['insights']
    }
    return render(request, 'dashboard/clients.html', context)

@login_required
def admin_panel(request):
    from django.contrib.auth.models import User
    from .utils import get_system_logs
    
    users = User.objects.all().order_by('-date_joined')
    logs = get_system_logs(limit=50).to_dict(orient='records')
    
    context = {
        'users': users,
        'logs': logs
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
def notifications_partial(request):
    from .utils import get_notification_items
    items = get_notification_items()
    return render(request, 'dashboard/partials/notifications.html', {'notifications': items})
