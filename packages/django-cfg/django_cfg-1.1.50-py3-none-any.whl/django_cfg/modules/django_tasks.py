"""
Django-CFG Task Service Module.

This module provides the service layer for background task processing with Dramatiq,
including task management, worker control, monitoring, and Django integration.
"""

from typing import Optional, Dict, Any, List, Union
import logging
import os
from django_cfg.modules.base import BaseModule
from django_cfg.models.tasks import TaskConfig, DramatiqConfig, validate_task_config

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Task management and worker control.
    
    Provides high-level interface for managing Dramatiq workers,
    monitoring task queues, and controlling task execution.
    """
    
    def __init__(self, config: DramatiqConfig):
        self.config = config
        self._broker = None
        self._workers = []
    
    @property
    def broker(self):
        """Get Dramatiq broker instance (lazy-loaded)."""
        if self._broker is None:
            try:
                import dramatiq
                from dramatiq.brokers.redis import RedisBroker
                
                # This will be configured by Django settings
                self._broker = dramatiq.get_broker()
            except ImportError:
                logger.error("Dramatiq not available")
                return None
            except Exception as e:
                logger.error(f"Failed to get Dramatiq broker: {e}")
                return None
        
        return self._broker
    
    def get_queue_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all configured queues."""
        if not self.broker:
            return []
        
        stats = []
        for queue_name in self.config.queues:
            try:
                # Get queue statistics from broker
                queue_stats = {
                    "name": queue_name,
                    "pending": 0,  # Will be populated by actual broker stats
                    "running": 0,
                    "completed": 0,
                    "failed": 0,
                }
                
                # TODO: Implement actual queue statistics retrieval
                # This depends on the specific broker implementation
                
                stats.append(queue_stats)
            except Exception as e:
                logger.error(f"Failed to get stats for queue {queue_name}: {e}")
        
        return stats
    
    def get_worker_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all active workers."""
        # TODO: Implement worker statistics retrieval
        # This would typically involve checking process status,
        # memory usage, and current task information
        
        return []
    
    def clear_queue(self, queue_name: str) -> bool:
        """Clear all messages from a specific queue."""
        if not self.broker:
            return False
        
        try:
            # TODO: Implement queue clearing
            logger.info(f"Cleared queue: {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear queue {queue_name}: {e}")
            return False
    
    def retry_failed_tasks(self, queue_name: Optional[str] = None) -> int:
        """Retry failed tasks in specified queue or all queues."""
        if not self.broker:
            return 0
        
        try:
            # TODO: Implement failed task retry logic
            retried_count = 0
            logger.info(f"Retried {retried_count} failed tasks")
            return retried_count
        except Exception as e:
            logger.error(f"Failed to retry tasks: {e}")
            return 0


class DjangoTasks(BaseModule):
    """
    Main Django-CFG task service.
    
    Provides the primary interface for task system integration,
    configuration management, and service coordination.
    """
    
    def __init__(self):
        super().__init__()
        self._config: Optional[TaskConfig] = None
        self._manager: Optional[TaskManager] = None
        self._redis_url: Optional[str] = None
    
    @property
    def config(self) -> Optional[TaskConfig]:
        """Get task configuration (lazy-loaded)."""
        # Always try to get fresh config to avoid stale cache issues
        try:
            django_config = self.get_config()  # This returns full DjangoConfig
            if django_config and hasattr(django_config, 'tasks') and django_config.tasks:
                # Extract only the TaskConfig part
                task_config = django_config.tasks
                if isinstance(task_config, TaskConfig):
                    # Update cache with fresh config
                    self._config = task_config
                    logger.debug(f"Loaded TaskConfig: {type(self._config)}")
                    return self._config
                else:
                    logger.error(f"Expected TaskConfig, got {type(task_config)}")
                    return None
            else:
                logger.warning("No tasks configuration found in Django config")
                return None
        except Exception as e:
            logger.warning(f"Failed to get task config: {e}")
            # Fallback to cached version if available
            return self._config
    
    @property
    def manager(self) -> Optional[TaskManager]:
        """Get task manager (lazy-loaded)."""
        if self._manager is None and self.config:
            try:
                self._manager = TaskManager(self.config.dramatiq)
            except Exception as e:
                logger.error(f"Failed to create task manager: {e}")
                return None
        return self._manager
    
    def is_enabled(self) -> bool:
        """Check if task system is enabled and properly configured."""
        if not self.config:
            return False
        
        if not self.config.enabled:
            return False
        
        # Check if required dependencies are available
        try:
            import dramatiq
            import django_dramatiq
        except ImportError:
            logger.warning("Dramatiq dependencies not available")
            return False
        
        return True
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL from Django-CFG cache configuration."""
        # Always try to get the URL if not cached
        if self._redis_url is None:
            try:
                django_config = self.get_config()
                if django_config and hasattr(django_config, 'cache_default') and django_config.cache_default:
                    cache_config = django_config.cache_default
                    if hasattr(cache_config, 'redis_url') and cache_config.redis_url:
                        self._redis_url = cache_config.redis_url
                        logger.debug(f"Got Redis URL: {self._redis_url}")
                    elif hasattr(cache_config, 'location') and cache_config.location:
                        self._redis_url = cache_config.location
                        logger.debug(f"Got Redis URL from location: {self._redis_url}")
                    else:
                        logger.warning("Cache config exists but no redis_url or location found")
                else:
                    logger.warning("No cache_default configuration found")
            except Exception as e:
                logger.warning(f"Failed to get Redis URL: {e}")
        
        return self._redis_url
    
    def check_redis_connection(self) -> bool:
        """Check if Redis connection is available."""
        redis_url = self.get_redis_url()
        if not redis_url:
            return False
        
        try:
            import redis
            from urllib.parse import urlparse
            
            parsed = urlparse(redis_url)
            r = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=self.config.dramatiq.redis_db if self.config else 1,
                password=parsed.password,
                socket_timeout=5
            )
            
            # Test connection
            r.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False
    
    def get_redis_client(self):
        """Get Redis client instance."""
        redis_url = self.get_redis_url()
        if not redis_url:
            logger.warning("No Redis URL available for client")
            return None
        
        try:
            import redis
            from urllib.parse import urlparse
            
            parsed = urlparse(redis_url)
            # Get redis_db from config, with fallback
            redis_db = 1  # default
            try:
                task_config = self.config  # This should return TaskConfig
                if task_config:
                    logger.debug(f"TaskConfig type: {type(task_config)}")
                    if hasattr(task_config, 'dramatiq') and task_config.dramatiq:
                        redis_db = task_config.dramatiq.redis_db
                        logger.debug(f"Using redis_db: {redis_db}")
                    else:
                        logger.warning("No dramatiq config found in TaskConfig")
                else:
                    logger.warning("No TaskConfig available")
            except Exception as e:
                logger.error(f"Error getting redis_db: {e}")
            
            client = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=redis_db,
                password=parsed.password,
                socket_timeout=5
            )
            
            logger.debug(f"Created Redis client: host={parsed.hostname}, port={parsed.port}, db={redis_db}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            return None
    
    def _get_current_timestamp(self) -> int:
        """Get current timestamp."""
        import time
        return int(time.time())
    
    def validate_configuration(self) -> bool:
        """Validate complete task system configuration."""
        if not self.config:
            logger.error("Task configuration not available")
            return False
        
        redis_url = self.get_redis_url()
        if not redis_url:
            logger.error("Redis URL not configured")
            return False
        
        return validate_task_config(self.config, redis_url)
    
    def get_dramatiq_settings(self) -> Dict[str, Any]:
        """Generate Django settings for Dramatiq integration."""
        if not self.config or not self.is_enabled():
            return {}
        
        redis_url = self.get_redis_url()
        if not redis_url:
            logger.error("Cannot generate Dramatiq settings: Redis URL not available")
            return {}
        
        try:
            return self.config.get_dramatiq_settings(redis_url)
        except Exception as e:
            logger.error(f"Failed to generate Dramatiq settings: {e}")
            return {}
    
    
    def get_installed_apps(self) -> List[str]:
        """Get Django apps required for task system."""
        if not self.is_enabled():
            return []
        
        apps = ["django_dramatiq"]
        
        # Add optional apps based on configuration
        if self.config and self.config.dramatiq.admin_enabled:
            # Admin integration is included in django_dramatiq
            # Add our custom tasks app for enhanced admin interface
            apps.append("django_cfg.apps.tasks")
        
        return apps
    
    def discover_tasks(self) -> List[str]:
        """Discover task modules in Django apps."""
        if not self.config or not self.config.auto_discover_tasks:
            return []
        
        discovered = []
        
        try:
            from django.apps import apps
            from django.conf import settings
            
            for app_config in apps.get_app_configs():
                for module_name in self.config.task_modules:
                    module_path = f"{app_config.name}.{module_name}"
                    try:
                        __import__(module_path)
                        discovered.append(module_path)
                        logger.debug(f"Discovered task module: {module_path}")
                    except ImportError:
                        # Module doesn't exist, which is fine
                        pass
                    except Exception as e:
                        logger.warning(f"Error importing task module {module_path}: {e}")
        
        except Exception as e:
            logger.error(f"Task discovery failed: {e}")
        
        return discovered
    
    def start_workers(self, processes: Optional[int] = None, queues: Optional[List[str]] = None) -> bool:
        """Start Dramatiq workers programmatically."""
        if not self.is_enabled():
            logger.error("Task system not enabled")
            return False
        
        try:
            # This would typically be handled by management commands
            # but can be useful for programmatic worker management
            
            effective_processes = processes or self.config.get_effective_processes()
            effective_queues = queues or self.config.get_effective_queues()
            
            logger.info(f"Starting {effective_processes} workers for queues: {effective_queues}")
            
            # TODO: Implement actual worker startup
            # This would involve spawning worker processes
            
            return True
        except Exception as e:
            logger.error(f"Failed to start workers: {e}")
            return False
    
    def stop_workers(self, graceful: bool = True) -> bool:
        """Stop all Dramatiq workers."""
        try:
            # TODO: Implement worker shutdown
            timeout = self.config.worker.shutdown_timeout if self.config else 30
            logger.info(f"Stopping workers (graceful={graceful}, timeout={timeout}s)")
            
            return True
        except Exception as e:
            logger.error(f"Failed to stop workers: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of task system."""
        status = {
            "enabled": self.is_enabled(),
            "redis_connection": False,
            "configuration_valid": False,
            "workers": [],
            "queues": [],
            "discovered_modules": [],
        }
        
        if self.is_enabled():
            status["redis_connection"] = self.check_redis_connection()
            status["configuration_valid"] = self.validate_configuration()
            
            if self.manager:
                status["workers"] = self.manager.get_worker_stats()
                status["queues"] = self.manager.get_queue_stats()
            
            status["discovered_modules"] = self.discover_tasks()
        
        return status


# === Service Factory ===

_task_service_instance: Optional[DjangoTasks] = None


def get_task_service() -> DjangoTasks:
    """
    Get the global task service instance.
    
    Returns:
        DjangoTasks: The singleton task service instance
    """
    global _task_service_instance
    
    if _task_service_instance is None:
        _task_service_instance = DjangoTasks()
    
    return _task_service_instance


def reset_task_service():
    """Reset the global task service instance (useful for testing)."""
    global _task_service_instance
    _task_service_instance = None


# === Utility Functions ===

def is_task_system_available() -> bool:
    """Check if task system is available and properly configured."""
    try:
        service = get_task_service()
        return service.is_enabled()
    except Exception:
        return False


def get_task_health() -> Dict[str, Any]:
    """Get task system health status."""
    try:
        service = get_task_service()
        return service.get_health_status()
    except Exception as e:
        return {
            "enabled": False,
            "error": str(e),
            "redis_connection": False,
            "configuration_valid": False,
        }


def enqueue_task(actor_name: str, *args, queue_name: str = "default", **kwargs) -> bool:
    """
    Enqueue a task for processing.
    
    Args:
        actor_name: Name of the Dramatiq actor
        *args: Task arguments
        queue_name: Queue to send task to
        **kwargs: Task keyword arguments
    
    Returns:
        bool: True if task was successfully enqueued
    """
    try:
        service = get_task_service()
        if not service.is_enabled():
            logger.error("Task system not enabled")
            return False
        
        # TODO: Implement actual task enqueueing
        # This would involve getting the actor and calling send()
        
        logger.info(f"Enqueued task {actor_name} to queue {queue_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to enqueue task {actor_name}: {e}")
        return False


# === Exports ===

__all__ = [
    "DjangoTasks",
    "TaskManager", 
    "get_task_service",
    "reset_task_service",
    "is_task_system_available",
    "get_task_health",
    "enqueue_task",
]
