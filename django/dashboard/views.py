from django.shortcuts import render
from django.db.models import Count
from .models import Vessels, Orders, AuditLogs, Surveis, Sites
import json

def index(request):
    return render(request, 'index.html')

def dashboard(request):
    # Basic stats
    total_vessels = Vessels.objects.count()
    active_vessels = Vessels.objects.filter(status='Active').count()
    
    total_orders = Orders.objects.count()
    active_orders = Orders.objects.exclude(status='Complited').count() # Typo in DB 'Complited'
    
    total_sites = Sites.objects.count()
    
    recent_logs = AuditLogs.objects.order_by('-changed_at')[:5]

    context = {
        'total_vessels': total_vessels,
        'active_vessels': active_vessels,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'total_sites': total_sites,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard.html', context)

def insights(request):
    # Aggregations for charts
    vessel_status = Vessels.objects.values('status').annotate(count=Count('status'))
    order_status = Orders.objects.values('status').annotate(count=Count('status'))
    
    context = {
        'vessel_status': json.dumps(list(vessel_status)),
        'order_status': json.dumps(list(order_status)),
    }
    return render(request, 'insights.html', context)
