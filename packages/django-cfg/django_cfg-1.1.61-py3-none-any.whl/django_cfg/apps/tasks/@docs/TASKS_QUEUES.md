# 🚀 Django-CFG Tasks & Queues Documentation

## 🎯 Overview

Django-CFG provides production-ready background task processing using **Dramatiq** with Redis as message broker. This system handles document processing, maintenance tasks, and other asynchronous operations.

**Key Features**:
- Multiple Redis databases for isolation
- Automatic task discovery
- Production-ready middleware stack
- Comprehensive monitoring and health checks
- Manual worker management (no auto-start)

**TAGS**: `dramatiq, redis, queues, background-tasks, async`

---

## 🧱 Architecture %%PRIORITY:HIGH%%

### Core Components

- **TaskConfig**: Pydantic model for task system configuration
- **DramatiqConfig**: Dramatiq-specific settings (Redis, workers, middleware)
- **DjangoTasks**: Main service class for task management
- **TaskManager**: Worker control and queue monitoring

### Redis Database Layout

```
DB 0: Django cache (default)
DB 1: Sessions, general cache
DB 2: Dramatiq queues %%PRIORITY:HIGH%%
```

**%%AI_HINT: Always use DB=2 for Dramatiq to avoid conflicts%%**

---

## 📦 Queue Configuration

### Default Queues

```python
queues = [
    "default",      # General tasks
    "high",         # Priority tasks
    "low",          # Background tasks
    "vehicles",     # Vehicle data processing
    "tax",          # Tax calculations
    "parsing",      # Data parsing tasks
    "knowledge"     # Document processing %%PRIORITY:HIGH%%
]
```

### Queue Usage Patterns

- **knowledge**: Document chunking, embedding generation
- **high**: User-facing operations, real-time processing
- **default**: Standard background tasks
- **low**: Cleanup, maintenance, non-urgent tasks

---

## 🔧 Worker Management %%PRIORITY:HIGH%%

### Manual Worker Startup (Recommended)

```bash
# Start workers manually
cd /path/to/django/project
poetry run python manage.py rundramatiq --processes 2 --threads 4

# With specific queues
poetry run python manage.py rundramatiq --queues knowledge --queues high

# Development mode (single process)
poetry run python manage.py rundramatiq --processes 1 --threads 2
```

### Why No Auto-Start? %%BREAKING_CHANGE%%

**REMOVED_IN: v1.1.54** - Auto-start functionality removed due to:

1. **Subprocess Issues**: Django subprocess couldn't find `rundramatiq` command
2. **Environment Problems**: `DJANGO_SETTINGS_MODULE` not properly inherited
3. **Process Management**: Difficult to control worker lifecycle
4. **Production Concerns**: Workers should be managed by process managers (systemd, supervisor)

**%%AI_HINT: Always start workers manually or via process manager%%**

---

## 🏗️ Configuration Models

### TaskConfig (Pydantic 2)

```python
class TaskConfig(BaseModel):
    enabled: bool = True
    backend: TaskBackend = TaskBackend.DRAMATIQ
    dramatiq: DramatiqConfig = Field(default_factory=DramatiqConfig)
    auto_discover_tasks: bool = True
    task_modules: List[str] = ["tasks"]
    
    # REMOVED: auto_start_worker field
```

### DramatiqConfig

```python
class DramatiqConfig(BaseModel):
    # Redis settings
    redis_db: int = 2  # %%PRIORITY:HIGH%%
    redis_key_prefix: str = "dramatiq"
    
    # Worker settings
    processes: int = 2
    threads: int = 4
    
    # Queue configuration
    queues: List[str] = [
        "default", "high", "low", 
        "vehicles", "tax", "parsing", "knowledge"
    ]
    
    # Middleware stack
    middleware: List[str] = [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit", 
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "dramatiq.middleware.Shutdown",
        # Prometheus disabled by default
    ]
```

---

## 🔁 Task Processing Flows

### Document Processing Flow

1. **Document Created** → `post_save` signal triggered
2. **Signal Handler** → `_start_document_processing()` called
3. **Task Enqueued** → `process_document_async.send(document_id)`
4. **Worker Picks Up** → Task from `knowledge` queue
5. **Processing** → Document chunking, embedding generation
6. **Completion** → Status updated, chunks saved

**Modules Involved**:
- `apps.knowbase.signals`
- `apps.knowbase.tasks.document_processing`
- `apps.knowbase.services.document_service`
- `apps.knowbase.services.chunking_service`

### Task Lifecycle States

```
pending → running → completed
       ↘         ↗
         failed → retrying → completed/dead_letter
```

---

## 🚨 Common Issues & Solutions %%PRIORITY:HIGH%%

### Issue: Tasks Stuck in Pending

**Symptoms**: Tasks enqueued but never processed
**Causes**:
1. No workers running
2. Wrong Redis database
3. Queue name mismatch
4. Worker crashed

**Solutions**:
```bash
# Check if workers are running
ps aux | grep rundramatiq

# Check Redis connection
redis-cli -n 2 LLEN dramatiq:queue:knowledge

# Start workers
poetry run python manage.py rundramatiq
```

### Issue: Redis DB Mismatch %%BREAKING_CHANGE%%

**Problem**: Tasks sent to DB=0, worker listens on DB=2

**Fixed in generation.py**:
```python
# Before (broken)
redis_url = f"{base_url}/{redis_db}"  # redis://localhost:6379/0/2

# After (fixed)
from urllib.parse import urlparse, urlunparse
parsed = urlparse(redis_url)
fixed_url = urlunparse((
    parsed.scheme, parsed.netloc, f"/{redis_db}",
    parsed.params, parsed.query, parsed.fragment
))
```

### Issue: Worker Subprocess Failures

**Problem**: `dramatiq: error: the following arguments are required: broker`

**Root Cause**: Subprocess couldn't execute `rundramatiq` command properly

**Solution**: Removed auto-start, use manual worker management

### Issue: Database Routing Problems

**Problem**: `ConnectionDoesNotExist: The connection 'knowledge' doesn't exist`

**Solution**: Fixed `app_label` extraction in `generation.py`:
```python
# Extract app_label from full path
app_label = app_path.split('.')[-1]  # "apps.knowbase" → "knowbase"
```

---

## 🛠️ Development Workflow

### Local Development

1. **Start Redis**: `redis-server`
2. **Start Django**: `poetry run python manage.py runserver`
3. **Start Workers**: `poetry run python manage.py rundramatiq --processes 1`
4. **Monitor Queues**: Use Django admin or Redis CLI

### Testing Tasks

```python
# Synchronous testing
from apps.knowbase.tasks.document_processing import process_document_async
result = process_document_async('document-id')

# Asynchronous testing
process_document_async.send('document-id')
```

### Queue Monitoring

```bash
# Check queue lengths
redis-cli -n 2 LLEN dramatiq:queue:knowledge
redis-cli -n 2 LLEN dramatiq:queue:default

# View failed tasks
redis-cli -n 2 LLEN dramatiq:queue:knowledge.DQ

# Clear queues (development only)
redis-cli -n 2 FLUSHDB
```

---

## 🔍 Debugging Guide

### Worker Logs

```bash
# View worker output
poetry run python manage.py rundramatiq --processes 1 --threads 1

# With verbose logging
DJANGO_LOG_LEVEL=DEBUG poetry run python manage.py rundramatiq
```

### Task Status Checking

```python
# Check task in Django shell
from django_dramatiq.models import Task
tasks = Task.objects.filter(status='pending')
print(f"Pending tasks: {tasks.count()}")
```

### Redis Debugging

```bash
# Connect to Dramatiq Redis DB
redis-cli -n 2

# List all keys
KEYS dramatiq:*

# Check specific queue
LLEN dramatiq:queue:knowledge
LRANGE dramatiq:queue:knowledge 0 -1
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoint

The task system provides health status via `get_task_health()`:

```python
{
    "enabled": True,
    "redis_connection": True,
    "configuration_valid": True,
    "workers": [...],
    "queues": [...],
    "discovered_modules": [...]
}
```

### Key Metrics

- Queue lengths
- Task processing rates
- Worker status
- Failed task counts
- Redis connection health

---

## 🚀 Production Deployment

### Process Manager Setup

**Systemd Service** (`/etc/systemd/system/dramatiq-workers.service`):
```ini
[Unit]
Description=Dramatiq Workers
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment=DJANGO_SETTINGS_MODULE=api.settings
ExecStart=/path/to/venv/bin/python manage.py rundramatiq --processes 4 --threads 8
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Supervisor Configuration

```ini
[program:dramatiq-workers]
command=/path/to/venv/bin/python manage.py rundramatiq --processes 4
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
environment=DJANGO_SETTINGS_MODULE="api.settings"
stdout_logfile=/var/log/dramatiq/workers.log
stderr_logfile=/var/log/dramatiq/workers.error.log
```

---

## ⚠️ Anti-patterns %%PRIORITY:HIGH%%

### ❌ Don't Do This

```python
# Don't use auto-start (removed)
TaskConfig(auto_start_worker=True)  # %%DEPRECATED%%

# Don't mix Redis databases
DRAMATIQ_BROKER = {"OPTIONS": {"url": "redis://localhost:6379/0"}}  # Wrong DB

# Don't ignore queue clearing in development
clear_dramatiq_queues()  # Can delete important tasks

# Don't use subprocess for worker management
subprocess.Popen(["python", "manage.py", "rundramatiq"])  # Unreliable
```

### ✅ Best Practices

```python
# Use manual worker management
# Start workers via process manager or manually

# Use correct Redis database
redis_db: int = 2

# Handle task failures gracefully
@dramatiq.actor(max_retries=3, min_backoff=1000)
def my_task():
    try:
        # Task logic
        pass
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise
```

---

## 📝 Version History

- **v1.1.53**: Added auto-start functionality
- **v1.1.54**: %%BREAKING_CHANGE%% Removed auto-start due to subprocess issues
- **v1.1.54**: Fixed Redis URL generation for correct database routing
- **v1.1.54**: Fixed database routing with proper `app_label` extraction

---

## 🧠 Notes

- **RAG-Optimized**: This documentation is structured for LLM retrieval
- **Token-Efficient**: Concise but comprehensive coverage
- **Production-Ready**: Based on real-world deployment experience
- **Problem-Focused**: Documents actual issues encountered and solutions

**DEPENDS_ON**: `dramatiq`, `redis`, `django-dramatiq`, `pydantic`
**USED_BY**: Document processing, maintenance tasks, background operations
