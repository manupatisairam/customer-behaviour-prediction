from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_panel_dashboard'),
    path('users/', views.manage_users_view, name='manage_users'),
    path('logs/', views.system_logs_view, name='system_logs'),
    path('logs/export/', views.export_logs_csv, name='export_logs'),
    path('logs/clear/', views.clear_logs, name='clear_logs'),
    path('reports/', views.reports_view, name='admin_reports'),
    path('monitor/', views.system_monitor_view, name='system_monitor'),
    path('api/stats/', views.admin_api_stats, name='api_stats'),
    path('generate-report/<str:report_type>/', views.generate_report_view, name='generate_report'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('export-center/', views.export_center_view, name='export_center'),
]
