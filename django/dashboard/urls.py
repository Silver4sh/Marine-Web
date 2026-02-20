from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('environment/', views.environment, name='environment'),
    path('buoy/<str:buoy_id>/', views.buoy_detail, name='buoy_detail'),
    path('survey/', views.survey_list, name='survey_list'),
    path('survey/create/', views.create_survey, name='create_survey'),
    path('clients/', views.clients, name='clients'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('notifications/', views.notifications_partial, name='notifications'),
    path('api/map-data/', views.get_map_data, name='api_map_data'),
    
    # Fallback for default Django auth redirect
    path('accounts/login/', views.login_view, name='fallback_login'),
]
