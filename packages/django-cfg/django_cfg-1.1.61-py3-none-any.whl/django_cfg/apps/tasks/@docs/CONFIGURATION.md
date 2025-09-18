# ⚙️ Django-CFG Tasks Configuration Guide

## 🎯 Overview

Complete configuration reference for Django-CFG task system. Covers all settings, environment variables, and deployment configurations.

**TAGS**: `configuration, settings, deployment, dramatiq, redis`

---

## 🏗️ Configuration Models %%PRIORITY:HIGH%%

### TaskConfig (Main Configuration)

```python
from django_cfg.models.tasks import TaskConfig, DramatiqConfig

config = TaskConfig(
    enabled=True,                    # Enable task system
    backend="dramatiq",              # Task backend (only dramatiq supported)
    dramatiq=DramatiqConfig(...),    # Dramatiq-specific settings
    auto_discover_tasks=True,        # Auto-discover task modules
    task_modules=["tasks"]           # Module names to search for tasks
)
```

**Field Details**:
- `enabled`: Master switch for entire task system
- `backend`: Currently only `TaskBackend.DRAMATIQ` supported
- `dramatiq`: Nested Dramatiq configuration (see below)
- `auto_discover_tasks`: Automatically find task modules in Django apps
- `task_modules`: List of module names to search (e.g., "tasks", "background")

---

### DramatiqConfig (Dramatiq Settings)

```python
from django_cfg.models.tasks import DramatiqConfig

dramatiq_config = DramatiqConfig(
    # === Redis Configuration ===
    redis_db=2,                      # Redis database number %%PRIORITY:HIGH%%
    redis_key_prefix="dramatiq",     # Key prefix for Redis keys
    redis_socket_timeout=5,          # Connection timeout (seconds)
    redis_socket_connect_timeout=5,  # Connect timeout (seconds)
    redis_socket_keepalive=True,     # Enable TCP keepalive
    redis_socket_keepalive_options={},
    redis_health_check_interval=30,  # Health check interval (seconds)
    
    # === Worker Configuration ===
    processes=2,                     # Number of worker processes
    threads=4,                       # Threads per process
    
    # === Queue Configuration ===
    queues=[                         # Available queues
        "default", "high", "low",
        "vehicles", "tax", "parsing", "knowledge"
    ],
    
    # === Middleware Stack ===
    middleware=[                     # Middleware in order %%PRIORITY:HIGH%%
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit", 
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "dramatiq.middleware.Shutdown",
    ],
    
    # === Timeouts & Limits ===
    max_age=3600000,                # Max message age (ms)
    max_retries=3,                  # Default retry count
    min_backoff=15000,              # Min retry backoff (ms)
    max_backoff=300000,             # Max retry backoff (ms)
    
    # === Worker Settings ===
    worker=WorkerConfig(
        threads=4,                   # Threads per worker
        shutdown_timeout=30,         # Graceful shutdown timeout
        log_level="INFO"            # Worker log level
    ),
    
    # === Monitoring ===
    prometheus_enabled=False,        # Disable Prometheus by default
    prometheus_http_host="127.0.0.1",
    prometheus_http_port=9191,
    
    # === Admin Interface ===
    admin_enabled=True              # Enable Django admin integration
)
```

---

## 🔧 Environment-Specific Configurations

### Development Configuration

```python
# config/dev.yaml
tasks:
  enabled: true
  dramatiq:
    redis_db: 2
    processes: 1          # Single process for development
    threads: 2           # Fewer threads
    queues:
      - default
      - knowledge        # Only essential queues
    prometheus_enabled: false
```

### Production Configuration

```python
# config/prod.yaml
tasks:
  enabled: true
  dramatiq:
    redis_db: 2
    processes: 4          # More processes for production
    threads: 8           # More threads
    queues:              # All queues
      - default
      - high
      - low
      - vehicles
      - tax
      - parsing
      - knowledge
    prometheus_enabled: true
    prometheus_http_port: 9191
    max_retries: 5       # More retries in production
```

### Testing Configuration

```python
# config/test.yaml
tasks:
  enabled: false         # Disable in tests
  # OR for integration tests:
  enabled: true
  dramatiq:
    redis_db: 15         # Use different DB for tests
    processes: 1
    threads: 1
```

---

## 🐳 Docker Configuration

### Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  django:
    build: .
    environment:
      - DJANGO_SETTINGS_MODULE=api.settings
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  dramatiq-workers:
    build: .
    command: python manage.py rundramatiq --processes 2 --threads 4
    environment:
      - DJANGO_SETTINGS_MODULE=api.settings
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - django
    restart: unless-stopped

volumes:
  redis_data:
```

### Dockerfile for Workers

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Health check for workers
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=2)
r.ping()
" || exit 1

CMD ["python", "manage.py", "rundramatiq", "--processes", "2", "--threads", "4"]
```

---

## 🔄 Process Management

### Systemd Service

```ini
# /etc/systemd/system/dramatiq-workers.service
[Unit]
Description=Dramatiq Background Workers
After=network.target redis.service postgresql.service
Requires=redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myproject
Environment=DJANGO_SETTINGS_MODULE=api.settings
Environment=PYTHONPATH=/opt/myproject
ExecStart=/opt/myproject/venv/bin/python manage.py rundramatiq --processes 4 --threads 8
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dramatiq-workers

[Install]
WantedBy=multi-user.target
```

**Management Commands**:
```bash
# Enable and start
sudo systemctl enable dramatiq-workers
sudo systemctl start dramatiq-workers

# Status and logs
sudo systemctl status dramatiq-workers
sudo journalctl -u dramatiq-workers -f

# Restart workers
sudo systemctl restart dramatiq-workers
```

### Supervisor Configuration

```ini
# /etc/supervisor/conf.d/dramatiq-workers.conf
[program:dramatiq-workers]
command=/opt/myproject/venv/bin/python manage.py rundramatiq --processes 4 --threads 8
directory=/opt/myproject
user=www-data
autostart=true
autorestart=true
startsecs=10
startretries=3
redirect_stderr=true
stdout_logfile=/var/log/dramatiq/workers.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=DJANGO_SETTINGS_MODULE="api.settings",PYTHONPATH="/opt/myproject"

# Resource limits
process_name=%(program_name)s_%(process_num)02d
numprocs=1
```

**Management Commands**:
```bash
# Reload configuration
sudo supervisorctl reread
sudo supervisorctl update

# Control workers
sudo supervisorctl start dramatiq-workers
sudo supervisorctl stop dramatiq-workers
sudo supervisorctl restart dramatiq-workers
sudo supervisorctl status dramatiq-workers
```

---

## 🔐 Security Configuration

### Redis Security

```bash
# /etc/redis/redis.conf
bind 127.0.0.1                    # Bind to localhost only
requirepass your_strong_password   # Set password
protected-mode yes                 # Enable protected mode
port 6379                         # Default port (consider changing)

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
```

### Django Settings

```python
# settings/production.py
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://:password@localhost:6379/2",  # With password
        "connection_pool_kwargs": {
            "max_connections": 20,
            "retry_on_timeout": True,
        },
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks", 
        "dramatiq.middleware.Retries",
        "dramatiq.middleware.Shutdown",
    ],
}

# Security headers for Prometheus endpoint
if DRAMATIQ_CONFIG.get('prometheus_enabled'):
    ALLOWED_HOSTS.append('monitoring.internal')
```

---

## 📊 Monitoring Configuration

### Prometheus Integration

```python
# Enable Prometheus in configuration
dramatiq_config = DramatiqConfig(
    prometheus_enabled=True,
    prometheus_http_host="0.0.0.0",  # Allow external access
    prometheus_http_port=9191,
)
```

**Prometheus Scrape Config**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'dramatiq-workers'
    static_configs:
      - targets: ['worker1:9191', 'worker2:9191']
    scrape_interval: 15s
    metrics_path: /metrics
```

### Health Check Endpoint

```python
# Add to Django URLs
from django_cfg.modules.django_tasks import get_task_health

def health_check(request):
    health = get_task_health()
    status = 200 if health['enabled'] and health['redis_connection'] else 503
    return JsonResponse(health, status=status)

# urls.py
urlpatterns = [
    path('health/tasks/', health_check, name='tasks_health'),
]
```

---

## 🔧 Advanced Configuration

### Custom Middleware

```python
# custom_middleware.py
import dramatiq
from dramatiq.middleware import Middleware

class CustomLoggingMiddleware(Middleware):
    def before_process_message(self, broker, message):
        logger.info(f"Processing task: {message.actor_name}")
    
    def after_process_message(self, broker, message, *, result=None, exception=None):
        if exception:
            logger.error(f"Task failed: {message.actor_name} - {exception}")
        else:
            logger.info(f"Task completed: {message.actor_name}")

# Add to middleware list
middleware = [
    "dramatiq.middleware.AgeLimit",
    "myapp.middleware.CustomLoggingMiddleware",  # Custom middleware
    "dramatiq.middleware.TimeLimit",
    "dramatiq.middleware.Callbacks",
    "dramatiq.middleware.Retries",
    "dramatiq.middleware.Shutdown",
]
```

### Queue Routing

```python
# Route different tasks to different queues
@dramatiq.actor(queue_name="high")
def urgent_task():
    pass

@dramatiq.actor(queue_name="knowledge") 
def process_document():
    pass

@dramatiq.actor(queue_name="low")
def cleanup_task():
    pass
```

### Rate Limiting

```python
# Add rate limiting middleware
from dramatiq.rate_limits import ConcurrentRateLimiter
from dramatiq.rate_limits.backends import RedisBackend

# Configure rate limiter
backend = RedisBackend(url="redis://localhost:6379/2")
rate_limiter = ConcurrentRateLimiter(backend, "api-calls", limit=10)

@dramatiq.actor
def api_call_task():
    with rate_limiter.acquire():
        # Make API call
        pass
```

---

## 🧪 Testing Configuration

### Test Settings

```python
# settings/test.py
import tempfile

# Use in-memory Redis for tests
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.stub.StubBroker",
    "OPTIONS": {},
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
    ],
}

# Or use separate Redis DB
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker", 
    "OPTIONS": {
        "url": "redis://localhost:6379/15",  # Test DB
    },
}
```

### Test Utilities

```python
# test_utils.py
import dramatiq
from dramatiq.brokers.stub import StubBroker

def setup_test_broker():
    """Set up test broker for unit tests."""
    broker = StubBroker()
    dramatiq.set_broker(broker)
    return broker

def clear_test_queues():
    """Clear all test queues."""
    broker = dramatiq.get_broker()
    if hasattr(broker, 'flush_all'):
        broker.flush_all()
```

---

## 📝 Configuration Validation

### Validation Rules

```python
# Built-in validation in TaskConfig
@field_validator("enabled")
@classmethod
def validate_enabled_with_environment(cls, v: bool) -> bool:
    """Validate task system can be enabled in current environment."""
    if v:
        try:
            import dramatiq
            import redis
        except ImportError as e:
            raise ValueError(f"Missing required dependency: {e}")
    return v

@field_validator("dramatiq")
@classmethod  
def validate_dramatiq_config(cls, v: DramatiqConfig) -> DramatiqConfig:
    """Validate Dramatiq configuration."""
    if v.processes < 1:
        raise ValueError("processes must be >= 1")
    if v.threads < 1:
        raise ValueError("threads must be >= 1") 
    if v.redis_db < 0 or v.redis_db > 15:
        raise ValueError("redis_db must be 0-15")
    return v
```

### Configuration Check Command

```python
# management/commands/check_tasks.py
from django.core.management.base import BaseCommand
from django_cfg.modules.django_tasks import get_task_service

class Command(BaseCommand):
    help = 'Check task system configuration'
    
    def handle(self, *args, **options):
        service = get_task_service()
        
        if not service.is_enabled():
            self.stdout.write(
                self.style.WARNING('Task system is disabled')
            )
            return
        
        # Check configuration
        if service.validate_configuration():
            self.stdout.write(
                self.style.SUCCESS('✅ Task system configuration is valid')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Task system configuration is invalid')
            )
        
        # Check Redis connection
        if service.check_redis_connection():
            self.stdout.write(
                self.style.SUCCESS('✅ Redis connection is working')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Redis connection failed')
            )
        
        # Show discovered tasks
        discovered = service.discover_tasks()
        self.stdout.write(f"Discovered task modules: {discovered}")
```

**Usage**: `python manage.py check_tasks`

---

## 🚨 Common Configuration Mistakes %%PRIORITY:HIGH%%

### ❌ Wrong Redis Database

```python
# DON'T: Use same DB as cache
CACHES = {'default': {'LOCATION': 'redis://localhost:6379/2'}}
DRAMATIQ_REDIS_DB = 2  # Conflict!

# DO: Use separate databases
CACHES = {'default': {'LOCATION': 'redis://localhost:6379/0'}}
DRAMATIQ_REDIS_DB = 2  # Separate DB
```

### ❌ Incorrect Middleware Order

```python
# DON'T: Wrong order
middleware = [
    "dramatiq.middleware.Retries",      # Should be later
    "dramatiq.middleware.AgeLimit",     # Should be first
]

# DO: Correct order
middleware = [
    "dramatiq.middleware.AgeLimit",     # Age limit first
    "dramatiq.middleware.TimeLimit",    # Time limit second  
    "dramatiq.middleware.Callbacks",    # Callbacks third
    "dramatiq.middleware.Retries",      # Retries fourth
    "dramatiq.middleware.Shutdown",     # Shutdown last
]
```

### ❌ Missing Environment Variables

```python
# DON'T: Hardcode settings
DRAMATIQ_BROKER = {
    "OPTIONS": {"url": "redis://localhost:6379/2"}
}

# DO: Use environment variables
import os
DRAMATIQ_BROKER = {
    "OPTIONS": {
        "url": os.getenv('REDIS_URL', 'redis://localhost:6379/2')
    }
}
```

---

## 🧠 Best Practices

### Configuration Management

1. **Environment-Specific**: Use different configs for dev/staging/prod
2. **Validation**: Always validate configuration on startup
3. **Secrets**: Use environment variables for sensitive data
4. **Documentation**: Document all configuration options
5. **Defaults**: Provide sensible defaults for all settings

### Resource Planning

1. **Memory**: Plan for ~50MB per worker process
2. **CPU**: 1 process per CPU core is good starting point
3. **Redis**: Monitor memory usage, enable persistence
4. **Network**: Consider Redis connection limits
5. **Disk**: Plan for log storage and Redis persistence

**DEPENDS_ON**: Django-CFG, Dramatiq, Redis
**USED_BY**: Development, DevOps, System administrators
