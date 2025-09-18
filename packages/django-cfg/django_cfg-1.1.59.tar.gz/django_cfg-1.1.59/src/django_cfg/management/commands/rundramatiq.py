"""
Django management command for running Dramatiq workers.

This command provides a Django-integrated way to start Dramatiq workers
with configuration from Django-CFG TaskConfig.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from typing import Any, Optional, List
import logging
import sys
import os

from django_cfg.modules.django_tasks import get_task_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Run Dramatiq workers with Django-CFG configuration.
    
    This command starts Dramatiq workers using the configuration
    defined in Django-CFG TaskConfig, with support for custom
    process counts, queue selection, and worker options.
    """
    
    help = "Run Dramatiq workers for background task processing"
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--processes",
            type=int,
            help="Number of worker processes (overrides config)",
        )
        parser.add_argument(
            "--threads", 
            type=int,
            help="Number of threads per process (overrides config)",
        )
        parser.add_argument(
            "--queues",
            type=str,
            help="Comma-separated list of queues to process (overrides config)",
        )
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="Log level for workers (overrides config)",
        )
        parser.add_argument(
            "--watch",
            type=str,
            help="Watch directory for code changes and auto-reload",
        )
        parser.add_argument(
            "--pid-file",
            type=str,
            help="Write process ID to file",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show configuration without starting workers",
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Get task service
            task_service = get_task_service()
            
            # Check if task system is enabled
            if not task_service.is_enabled():
                raise CommandError(
                    "Task system is not enabled. "
                    "Please configure 'tasks' in your Django-CFG configuration."
                )
            
            # Validate configuration
            if not task_service.validate_configuration():
                raise CommandError(
                    "Task system configuration is invalid. "
                    "Please check your Redis connection and task settings."
                )
            
            # Get effective configuration
            config = task_service.config
            if not config:
                raise CommandError("Task configuration not available")
            
            # Build worker arguments
            worker_args = self._build_worker_args(config, options)
            
            if options["dry_run"]:
                self._show_configuration(config, worker_args)
                return
            
            # Start workers
            self._start_workers(worker_args, options)
            
        except ImportError:
            raise CommandError(
                "Dramatiq dependencies not installed. "
                "Install with: pip install django-cfg[tasks]"
            )
        except Exception as e:
            logger.exception("Failed to start Dramatiq workers")
            raise CommandError(f"Failed to start workers: {e}")
    
    def _build_worker_args(self, config, options) -> List[str]:
        """Build command line arguments for Dramatiq workers."""
        args = ["dramatiq"]
        
        # Process count
        processes = options.get("processes") or config.get_effective_processes()
        args.extend(["--processes", str(processes)])
        
        # Thread count
        threads = options.get("threads") or config.dramatiq.threads
        args.extend(["--threads", str(threads)])
        
        # Queues
        if options.get("queues"):
            queues = [q.strip() for q in options["queues"].split(",")]
        else:
            queues = config.get_effective_queues()
        
        for queue in queues:
            args.extend(["--queues", queue])
        
        # Log level (not supported by standard dramatiq CLI)
        # log_level = options.get("log_level") or config.worker.log_level
        # args.extend(["--log-level", log_level])
        
        # Watch directory
        if options.get("watch"):
            args.extend(["--watch", options["watch"]])
        
        # PID file
        if options.get("pid_file"):
            args.extend(["--pid-file", options["pid_file"]])
        
        # Note: Using Python API instead of CLI, so no broker argument needed
        
        # Add discovered task modules
        discovered_modules = get_task_service().discover_tasks()
        for module in discovered_modules:
            args.append(module)
        
        # If no modules discovered, add default patterns
        if not discovered_modules:
            # Add common task module patterns
            for app in settings.INSTALLED_APPS:
                if not app.startswith("django.") and not app.startswith("django_"):
                    args.append(f"{app}.tasks")
        
        return args
    
    def _show_configuration(self, config, worker_args):
        """Show worker configuration without starting."""
        self.stdout.write(
            self.style.SUCCESS("Dramatiq Worker Configuration:")
        )
        
        self.stdout.write(f"  Processes: {config.get_effective_processes()}")
        self.stdout.write(f"  Threads: {config.dramatiq.threads}")
        self.stdout.write(f"  Queues: {', '.join(config.get_effective_queues())}")
        self.stdout.write(f"  Log Level: {config.worker.log_level}")
        self.stdout.write(f"  Redis DB: {config.dramatiq.redis_db}")
        
        self.stdout.write("\nDiscovered task modules:")
        discovered = get_task_service().discover_tasks()
        if discovered:
            for module in discovered:
                self.stdout.write(f"  - {module}")
        else:
            self.stdout.write("  (none found)")
        
        self.stdout.write(f"\nCommand that would be executed:")
        self.stdout.write(f"  {' '.join(worker_args)}")
    
    def _start_workers(self, worker_args, options):
        """Start Dramatiq workers using Python API instead of CLI."""
        self.stdout.write(
            self.style.SUCCESS("Starting Dramatiq workers...")
        )
        
        # Show startup info
        task_service = get_task_service()
        config = task_service.config
        
        processes = options.get("processes") or config.get_effective_processes()
        threads = options.get("threads") or config.dramatiq.threads
        queues = config.get_effective_queues()
        if options.get("queues"):
            queues = [q.strip() for q in options["queues"].split(",")]
        
        self.stdout.write(f"Processes: {processes}")
        self.stdout.write(f"Threads: {threads}")
        self.stdout.write(f"Queues: {', '.join(queues)}")
        
        # Write PID file if requested
        if options.get("pid_file"):
            with open(options["pid_file"], "w") as f:
                f.write(str(os.getpid()))
            self.stdout.write(f"PID written to: {options['pid_file']}")
        
        try:
            # Import dramatiq and get broker FIRST
            import dramatiq
            from dramatiq.worker import Worker
            from django_cfg.modules.django_tasks import get_dramatiq_broker
            
            # Get the configured broker
            broker = get_dramatiq_broker()
            
            # CRITICAL: Set the broker as the global default BEFORE importing tasks
            dramatiq.set_broker(broker)
            
            # Now discover and import task modules with the correct broker set
            discovered_modules = get_task_service().discover_tasks()
            for module_name in discovered_modules:
                try:
                    __import__(module_name)
                    self.stdout.write(f"Loaded tasks from: {module_name}")
                except ImportError as e:
                    self.stdout.write(f"Warning: Could not import {module_name}: {e}")
            
            # Verify broker is set correctly
            current_broker = dramatiq.get_broker()
            self.stdout.write(f"Using broker: {current_broker}")
            
            # Create and start worker
            worker = Worker(broker, worker_timeout=600000)
            worker.start()
                
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down workers...")
        except Exception as e:
            logger.exception("Worker execution failed")
            raise CommandError(f"Worker execution failed: {e}")
