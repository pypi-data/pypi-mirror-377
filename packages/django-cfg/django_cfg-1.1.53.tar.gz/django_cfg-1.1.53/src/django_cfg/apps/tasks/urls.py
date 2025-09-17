"""
URLs for Django CFG Tasks app.

Provides endpoints for task queue management and monitoring.
"""

from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # API endpoints for task management
    path('api/status/', views.queue_status_api, name='queue_status_api'),
    path('api/workers/start/', views.start_workers_api, name='start_workers_api'),
    path('api/queues/clear/', views.clear_queues_api, name='clear_queues_api'),
    path('api/stats/', views.task_stats_api, name='task_stats_api'),
    
    # Dashboard views
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
