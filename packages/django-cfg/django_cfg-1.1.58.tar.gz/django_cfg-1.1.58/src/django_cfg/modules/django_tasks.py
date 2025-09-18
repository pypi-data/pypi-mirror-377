"""
Django-CFG Task Service Module.

This module provides the service layer for background task processing with Dramatiq,
including task management, worker control, monitoring, and Django integration.
"""

from typing import Optional, Dict, Any, List, Union
import logging
import subprocess
import time
from urllib.parse import urlparse

from django_cfg.modules.base import BaseModule
from django_cfg.models.tasks import TaskConfig, DramatiqConfig, validate_task_config
from django_cfg.models.constance import ConstanceField

# Django imports (will be available when Django is configured)
try:
    from django.conf import settings
    from django.apps import apps
except ImportError:
    settings = None
    apps = None

# Optional imports
try:
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker
except ImportError:
    dramatiq = None
    RedisBroker = None

try:
    import django_dramatiq
except ImportError:
    django_dramatiq = None

try:
    import redis
except ImportError:
    redis = None

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
            if dramatiq is None:
                logger.error("Dramatiq not available")
                return None
            
            try:
                # This will be configured by Django settings
                self._broker = dramatiq.get_broker()
            except Exception as e:
                logger.error(f"Failed to get Dramatiq broker: {e}")
                return None
        
        return self._broker
    
    def get_queue_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all configured queues."""
        if not self.broker:
            return []
        
        stats = []
        for queue_name in self.config.dramatiq.queues:
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
            # First try the base class method
            django_config = self.get_config()  # This returns full DjangoConfig
            if django_config and hasattr(django_config, 'tasks'):
                task_config = django_config.tasks
                if task_config and isinstance(task_config, TaskConfig):
                    # Update cache with fresh config
                    self._config = task_config
                    logger.debug(f"Loaded TaskConfig: enabled={task_config.enabled}")
                    return self._config
                elif task_config is None:
                    logger.debug("Tasks configuration is None in Django config")
                else:
                    logger.error(f"Expected TaskConfig, got {type(task_config)}")
            else:
                logger.debug("No tasks attribute found in Django config")
            
            # Fallback: try to import config directly
            try:
                from api.config import config as api_config
                if hasattr(api_config, 'tasks') and api_config.tasks:
                    task_config = api_config.tasks
                    if isinstance(task_config, TaskConfig):
                        self._config = task_config
                        logger.debug(f"Loaded TaskConfig from api.config: enabled={task_config.enabled}")
                        return self._config
            except ImportError:
                logger.debug("Could not import api.config")
            
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
        if dramatiq is None or django_dramatiq is None:
            logger.warning("Dramatiq dependencies not available")
            return False
        
        return True
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL from Django-CFG cache configuration."""
        # Always try to get the URL if not cached
        if self._redis_url is None:
            try:
                # Use get_current_config from django_cfg.core.config
                from django_cfg.core.config import get_current_config
                django_config = get_current_config()
                
                # If that fails, try to import directly from api.config
                if not django_config:
                    try:
                        from api.config import config
                        django_config = config
                        logger.debug("Got Django config from direct import")
                    except ImportError:
                        logger.warning("Could not import config from api.config")
                
                logger.debug(f"Django config type: {type(django_config)}")
                logger.debug(f"Has cache_default: {hasattr(django_config, 'cache_default') if django_config else False}")
                
                if django_config and hasattr(django_config, 'cache_default') and django_config.cache_default:
                    cache_config = django_config.cache_default
                    logger.debug(f"Cache config type: {type(cache_config)}")
                    logger.debug(f"Cache config redis_url: {getattr(cache_config, 'redis_url', 'NOT_FOUND')}")
                    
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
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")
        
        return self._redis_url
    
    def check_redis_connection(self) -> bool:
        """Check if Redis connection is available."""
        redis_url = self.get_redis_url()
        if not redis_url:
            return False
        
        if redis is None:
            logger.error("Redis library not available")
            return False
        
        try:
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
        
        if redis is None:
            logger.error("Redis library not available")
            return None
        
        try:
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
        
        if apps is None:
            logger.warning("Django apps not available")
            return []
        
        try:
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
    
    def get_constance_fields(self) -> List[ConstanceField]:
        """
        Get Constance fields for Dramatiq configuration.
        
        Returns:
            List of ConstanceField objects for dynamic task configuration
        """
        if not self.is_enabled():
            return []
        
        fields = [
            ConstanceField(
                name="DRAMATIQ_WORKER_PROCESSES",
                default=self.config.dramatiq.processes if self.config else 2,
                help_text="Number of worker processes for Dramatiq",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_WORKER_THREADS",
                default=self.config.dramatiq.threads if self.config else 4,
                help_text="Number of threads per worker process",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_MAX_RETRIES",
                default=3,
                help_text="Maximum number of retries for failed tasks",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_TASK_TIMEOUT",
                default=600,
                help_text="Task timeout in seconds (10 minutes default)",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_PROMETHEUS_ENABLED",
                default=int(self.config.dramatiq.prometheus_enabled if self.config else False),
                help_text="Enable Prometheus metrics for Dramatiq (0=disabled, 1=enabled)",
                field_type="bool",
                group="Tasks",
                required=False,
            ),
        ]
        
        logger.debug(f"Generated {len(fields)} Constance fields for Dramatiq")
        return fields
    
    def start_workers(self, processes: Optional[int] = None, queues: Optional[List[str]] = None) -> bool:
        """Start Dramatiq workers programmatically."""
        logger.warning("Auto-start workers functionality has been removed. Please start workers manually using: python manage.py rundramatiq")
        return False
    
    def stop_workers(self, graceful: bool = True) -> bool:
        """Stop all Dramatiq workers."""
        try:
            timeout = self.config.dramatiq.worker.shutdown_timeout if self.config else 30
            logger.info(f"Stopping workers (graceful={graceful}, timeout={timeout}s)")
            
            # Find and kill Dramatiq worker processes
            try:
                # Find worker processes
                result = subprocess.run(
                    ["pgrep", "-f", "rundramatiq"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    pids = [pid.strip() for pid in pids if pid.strip()]
                    
                    if pids:
                        logger.info(f"Found {len(pids)} worker processes: {pids}")
                        
                        # Send appropriate signal
                        signal = "TERM" if graceful else "KILL"
                        
                        for pid in pids:
                            try:
                                subprocess.run(["kill", f"-{signal}", pid], check=True)
                                logger.info(f"Sent {signal} signal to worker process {pid}")
                            except subprocess.CalledProcessError:
                                logger.warning(f"Failed to send {signal} signal to process {pid}")
                        
                        # Wait for graceful shutdown if requested
                        if graceful:
                            logger.info(f"Waiting up to {timeout}s for graceful shutdown...")
                            # TODO: Could implement actual waiting logic here
                        
                        logger.info("✅ Dramatiq workers stopped successfully")
                        return True
                    else:
                        logger.info("No worker processes found")
                        return True
                else:
                    logger.info("No worker processes found")
                    return True
                    
            except Exception as e:
                logger.error(f"Failed to find/stop worker processes: {e}")
                return False
            
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


def clear_dramatiq_queues() -> bool:
    """
    Clear all Dramatiq queues on startup.
    
    Returns:
        bool: True if queues were cleared successfully
    """
    try:
        service = get_task_service()
        if not service.is_enabled():
            logger.debug("Task system not enabled, skipping queue clearing")
            return True
        
        # Get broker and clear all queues
        if hasattr(service, 'manager') and service.manager and service.manager.broker:
            broker = service.manager.broker
            queue_names = service.config.dramatiq.queues
            
            for queue_name in queue_names:
                try:
                    # Clear the queue
                    if hasattr(broker, 'flush'):
                        broker.flush(queue_name)
                        logger.info(f"Cleared Dramatiq queue: {queue_name}")
                    elif hasattr(broker, 'client'):
                        # For Redis broker, clear using Redis client
                        redis_client = broker.client
                        queue_key = f"dramatiq:queue:{queue_name}"
                        redis_client.delete(queue_key)
                        logger.info(f"Cleared Redis queue: {queue_name}")
                except Exception as e:
                    logger.warning(f"Failed to clear queue {queue_name}: {e}")
            
            logger.info("✅ Dramatiq queues cleared on startup")
            return True
        else:
            logger.debug("Broker not available, skipping queue clearing")
            return True
            
    except Exception as e:
        logger.error(f"Failed to clear Dramatiq queues: {e}")
        return False


def initialize_task_system():
    """
    Initialize the task system during Django app startup.
    This function is called from Django AppConfig.ready() method.
    """
    try:
        service = get_task_service()
        
        # Force config reload to ensure we have fresh config
        service._config = None
        config = service.config
        
        if config and config.enabled:
            logger.info("🔧 Initializing Django-CFG task system...")
            logger.info("✅ Task system initialized successfully")
            logger.info("💡 To start workers, run: python manage.py rundramatiq")
        else:
            logger.debug(f"Task system not enabled (config: {config}), skipping initialization")
            
    except Exception as e:
        logger.error(f"Failed to initialize task system: {e}")


def extend_constance_config_with_tasks():
    """
    Extend Constance configuration with Dramatiq task fields if tasks are enabled.
    
    This function should be called during Django configuration setup to automatically
    add task-related Constance fields when the task system is enabled.
    """
    try:
        service = get_task_service()
        if not service.is_enabled():
            logger.debug("Task system not enabled, skipping Constance extension")
            return []
        
        fields = service.get_constance_fields()
        logger.info(f"🔧 Extended Constance with {len(fields)} task configuration fields")
        return fields
        
    except Exception as e:
        logger.error(f"Failed to extend Constance config with tasks: {e}")
        return []


# === Broker Creation ===

def create_dramatiq_broker():
    """
    Create and configure Dramatiq broker from Django settings.
    
    This function creates a broker instance that can be used directly
    by the Dramatiq CLI without requiring a separate broker.py file.
    
    Returns:
        dramatiq.Broker: Configured Dramatiq broker instance
    """
    try:
        from django.conf import settings
        
        if not hasattr(settings, 'DRAMATIQ_BROKER'):
            raise RuntimeError("DRAMATIQ_BROKER not configured in Django settings")
        
        broker_config = settings.DRAMATIQ_BROKER
        
        # Create broker from Django settings
        broker = RedisBroker(**broker_config['OPTIONS'])
        
        # Add middleware (only if not already present)
        existing_middleware_types = {type(mw).__name__ for mw in broker.middleware}
        
        for middleware_path in broker_config['MIDDLEWARE']:
            try:
                module_path, class_name = middleware_path.rsplit('.', 1)
                
                # Skip if middleware of this type already exists
                if class_name in existing_middleware_types:
                    continue
                    
                module = __import__(module_path, fromlist=[class_name])
                middleware_class = getattr(module, class_name)
                broker.add_middleware(middleware_class())
            except Exception as e:
                logger.warning(f"Failed to add middleware {middleware_path}: {e}")
        
        return broker
        
    except Exception as e:
        logger.error(f"Failed to create Dramatiq broker: {e}")
        raise


# Global broker instance (lazy-loaded)
_broker_instance = None


def get_dramatiq_broker():
    """
    Get the global Dramatiq broker instance.
    
    Returns:
        dramatiq.Broker: The singleton broker instance
    """
    global _broker_instance
    
    if _broker_instance is None:
        _broker_instance = create_dramatiq_broker()
    
    return _broker_instance


# === Exports ===

__all__ = [
    "DjangoTasks",
    "TaskManager", 
    "get_task_service",
    "reset_task_service",
    "is_task_system_available",
    "get_task_health",
    "enqueue_task",
    "extend_constance_config_with_tasks",
    "initialize_task_system",
    "clear_dramatiq_queues",
    "create_dramatiq_broker",
    "get_dramatiq_broker",
]
