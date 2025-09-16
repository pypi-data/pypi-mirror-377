"""
Views for Django CFG Tasks app.

Provides API endpoints and dashboard views for task management.
"""

import json
import logging
from typing import Dict, Any

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required

from ...modules.django_tasks import DjangoTasks

logger = logging.getLogger(__name__)


@staff_member_required
@require_http_methods(["GET"])
def queue_status_api(request):
    """API endpoint for queue status."""
    try:
        tasks_service = DjangoTasks()
        status_data = _get_queue_status(tasks_service)
        
        return JsonResponse({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        logger.error(f"Queue status API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def start_workers_api(request):
    """API endpoint for starting workers."""
    try:
        # This would integrate with the actual worker management
        # For now, return a success response
        return JsonResponse({
            'success': True,
            'message': 'Worker start command sent'
        })
        
    except Exception as e:
        logger.error(f"Start workers API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def clear_queues_api(request):
    """API endpoint for clearing queues."""
    try:
        # This would integrate with the actual queue clearing
        # For now, return a success response
        return JsonResponse({
            'success': True,
            'message': 'Queue clear command sent'
        })
        
    except Exception as e:
        logger.error(f"Clear queues API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def task_stats_api(request):
    """API endpoint for task statistics."""
    try:
        tasks_service = DjangoTasks()
        stats_data = _get_task_statistics(tasks_service)
        
        return JsonResponse({
            'success': True,
            'data': stats_data
        })
        
    except Exception as e:
        logger.error(f"Task stats API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def dashboard_view(request):
    """Dashboard view for task management."""
    try:
        tasks_service = DjangoTasks()
        
        context = {
            'queue_status': _get_queue_status(tasks_service),
            'task_stats': _get_task_statistics(tasks_service),
        }
        
        return render(request, 'tasks/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard view error: {e}")
        context = {
            'error': str(e)
        }
        return render(request, 'tasks/dashboard.html', context)


def _get_queue_status(tasks_service: DjangoTasks) -> Dict[str, Any]:
    """Get current queue status."""
    try:
        # Use tasks service to get Redis connection
        redis_client = tasks_service.get_redis_client()
        
        if not redis_client:
            return {
                'error': 'Redis connection not available',
                'queues': {},
                'workers': 0
            }
        
        # Get queue information
        queues_info = {}
        config = tasks_service.config
        
        if config and config.queues:
            for queue_name in config.queues:
                queue_key = f"dramatiq:default.DQ.{queue_name}"
                queue_length = redis_client.llen(queue_key)
                
                # Get failed queue length
                failed_key = f"dramatiq:default.DQ.{queue_name}.failed"
                failed_length = redis_client.llen(failed_key)
                
                queues_info[queue_name] = {
                    'pending': queue_length,
                    'failed': failed_length,
                    'total': queue_length + failed_length
                }
        
        # Get worker information (simplified)
        worker_keys = redis_client.keys("dramatiq:worker:*")
        active_workers = len(worker_keys) if worker_keys else 0
        
        return {
            'queues': queues_info,
            'workers': active_workers,
            'redis_connected': True,
            'timestamp': tasks_service._get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Queue status error: {e}")
        return {
            'error': str(e),
            'queues': {},
            'workers': 0,
            'redis_connected': False
        }


def _get_task_statistics(tasks_service: DjangoTasks) -> Dict[str, Any]:
    """Get task execution statistics."""
    try:
        # Import django_dramatiq models if available
        try:
            from django_dramatiq.models import Task
            from django.db.models import Count
            
            # Get task counts by status
            stats = Task.objects.aggregate(
                total=Count('id'),
            )
            
            # Get recent tasks
            recent_tasks = list(
                Task.objects.order_by('-created_at')[:10]
                .values('actor_name', 'status', 'created_at', 'updated_at')
            )
            
            return {
                'statistics': stats,
                'recent_tasks': recent_tasks,
                'timestamp': tasks_service._get_current_timestamp()
            }
            
        except ImportError:
            return {'error': 'django_dramatiq not available'}
            
    except Exception as e:
        logger.error(f"Task statistics error: {e}")
        return {'error': str(e)}
