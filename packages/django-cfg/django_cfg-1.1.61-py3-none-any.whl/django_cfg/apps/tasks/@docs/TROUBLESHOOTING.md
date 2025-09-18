# 🔧 Django-CFG Tasks Troubleshooting Guide

## 🎯 Overview

Comprehensive troubleshooting guide for Django-CFG task system issues. Based on real production problems and their solutions.

**TAGS**: `troubleshooting, debugging, dramatiq, redis, workers`

---

## 🚨 Critical Issues %%PRIORITY:HIGH%%

### 1. Tasks Stuck in Pending Status

**Symptoms**:
- Tasks appear in queue but never process
- Document processing status remains "pending"
- No worker activity in logs

**Diagnostic Commands**:
```bash
# Check if workers are running
ps aux | grep rundramatiq
pgrep -f rundramatiq

# Check Redis queue length
redis-cli -n 2 LLEN dramatiq:queue:knowledge

# Check Django task status
python manage.py shell -c "
from django_dramatiq.models import Task
print(f'Pending: {Task.objects.filter(status=\"pending\").count()}')
print(f'Failed: {Task.objects.filter(status=\"failed\").count()}')
"
```

**Solutions**:
1. **Start Workers**: `poetry run python manage.py rundramatiq`
2. **Check Redis Connection**: Verify Redis is running on correct port/DB
3. **Verify Queue Names**: Ensure task is sent to correct queue
4. **Check Logs**: Look for worker startup errors

---

### 2. Redis Database Mismatch %%BREAKING_CHANGE%%

**Problem**: Tasks sent to wrong Redis database

**Symptoms**:
- Tasks enqueued successfully but workers don't see them
- Queue appears empty in worker logs
- Redis shows tasks in different DB

**Root Cause**: 
```python
# BROKEN: Concatenating DB numbers
redis_url = f"{base_url}/{redis_db}"  # "redis://localhost:6379/0/2"
```

**Fix Applied in `generation.py`**:
```python
from urllib.parse import urlparse, urlunparse

def fix_redis_url(redis_url: str, redis_db: int) -> str:
    parsed = urlparse(redis_url)
    return urlunparse((
        parsed.scheme,
        parsed.netloc, 
        f"/{redis_db}",  # Replace path with correct DB
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
```

**Verification**:
```bash
# Check which DB tasks are in
redis-cli -n 0 KEYS dramatiq:*  # Should be empty
redis-cli -n 2 KEYS dramatiq:*  # Should show queues
```

---

### 3. Worker Subprocess Failures %%DEPRECATED%%

**Problem**: Auto-start workers fail with "broker required" error

**Error Message**:
```
dramatiq: error: the following arguments are required: broker
```

**Root Cause**: 
- Subprocess couldn't find `rundramatiq` command
- `DJANGO_SETTINGS_MODULE` not inherited
- Poetry environment not available in subprocess

**Solution**: %%BREAKING_CHANGE%% **Removed auto-start functionality**
- Use manual worker management
- Start workers via process manager (systemd, supervisor)
- No more subprocess complexity

---

### 4. Database Routing Issues

**Problem**: `ConnectionDoesNotExist: The connection 'knowledge' doesn't exist`

**Root Cause**: Incorrect `app_label` in database routing

**Fix Applied**:
```python
# BEFORE: Used full app path as key
DATABASE_ROUTING_RULES = {
    "apps.knowbase": ["knowbase"]  # ❌ Wrong
}

# AFTER: Extract app_label correctly  
app_label = app_path.split('.')[-1]  # "apps.knowbase" → "knowbase"
DATABASE_ROUTING_RULES = {
    "knowbase": ["knowbase"]  # ✅ Correct
}
```

---

### 5. Task Decoding Errors

**Problem**: "Error decoding message: Extra data: line 1 column 4 (char 3)"

**Symptoms**:
- Tasks end up in Dead Letter Queue (DLQ)
- Worker logs show message decoding failures
- Tasks appear corrupted

**Common Causes**:
1. **Message Format Issues**: Incorrect serialization
2. **Version Mismatch**: Different Dramatiq versions
3. **Encoding Problems**: Unicode/binary issues
4. **Corrupted Messages**: Redis data corruption

**Debugging**:
```bash
# Check DLQ contents
redis-cli -n 2 LRANGE dramatiq:queue:knowledge.DQ 0 -1

# Clear DLQ (development only)
redis-cli -n 2 DEL dramatiq:queue:knowledge.DQ
```

---

## 🔍 Diagnostic Tools

### Redis Queue Inspection

```bash
# Connect to Dramatiq Redis DB
redis-cli -n 2

# List all Dramatiq keys
KEYS dramatiq:*

# Check queue lengths
LLEN dramatiq:queue:default
LLEN dramatiq:queue:knowledge
LLEN dramatiq:queue:high

# View queue contents (first 5 items)
LRANGE dramatiq:queue:knowledge 0 4

# Check dead letter queues
LLEN dramatiq:queue:knowledge.DQ
LRANGE dramatiq:queue:knowledge.DQ 0 -1
```

### Worker Process Monitoring

```bash
# Find running workers
ps aux | grep rundramatiq
pgrep -f rundramatiq

# Monitor worker resource usage
top -p $(pgrep -f rundramatiq)

# Check worker logs
tail -f /tmp/dramatiq_worker.log
```

### Django Task Status

```python
# In Django shell
from django_dramatiq.models import Task

# Task counts by status
for status in ['pending', 'running', 'completed', 'failed']:
    count = Task.objects.filter(status=status).count()
    print(f"{status}: {count}")

# Recent failed tasks
failed_tasks = Task.objects.filter(
    status='failed'
).order_by('-created_at')[:10]

for task in failed_tasks:
    print(f"{task.actor_name}: {task.traceback}")
```

---

## 🛠️ Recovery Procedures

### Clear Stuck Tasks (Development)

```bash
# Clear all queues (DESTRUCTIVE)
redis-cli -n 2 FLUSHDB

# Clear specific queue
redis-cli -n 2 DEL dramatiq:queue:knowledge

# Reset Django task status
python manage.py shell -c "
from django_dramatiq.models import Task
Task.objects.filter(status='pending').update(status='failed')
"
```

### Restart Workers Safely

```bash
# Graceful shutdown (wait for current tasks)
pkill -TERM -f rundramatiq

# Force shutdown (immediate)
pkill -KILL -f rundramatiq

# Start fresh workers
poetry run python manage.py rundramatiq --processes 2 --threads 4
```

### Retry Failed Tasks

```python
# In Django shell
from django_dramatiq.models import Task
from apps.knowbase.tasks.document_processing import process_document_async

# Retry specific failed tasks
failed_tasks = Task.objects.filter(
    status='failed',
    actor_name='process_document_async'
)

for task in failed_tasks:
    # Re-enqueue the task
    process_document_async.send(task.kwargs['document_id'])
    print(f"Retried task for document: {task.kwargs['document_id']}")
```

---

## 📊 Performance Issues

### High Memory Usage

**Symptoms**:
- Workers consuming excessive RAM
- System becomes unresponsive
- OOM killer terminates workers

**Solutions**:
1. **Reduce Worker Count**: Lower `--processes` parameter
2. **Limit Task Size**: Break large tasks into smaller chunks
3. **Add Memory Limits**: Use systemd or supervisor limits
4. **Monitor Memory**: Add memory usage logging

### Slow Task Processing

**Symptoms**:
- Tasks take longer than expected
- Queue backlog grows
- Users experience delays

**Debugging**:
```python
# Add timing to tasks
import time
import logging

@dramatiq.actor
def my_task():
    start_time = time.time()
    try:
        # Task logic here
        pass
    finally:
        duration = time.time() - start_time
        logging.info(f"Task completed in {duration:.2f}s")
```

**Solutions**:
1. **Profile Tasks**: Identify bottlenecks
2. **Add More Workers**: Scale horizontally
3. **Optimize Database Queries**: Use select_related, prefetch_related
4. **Cache Results**: Avoid redundant processing

---

## 🔧 Configuration Issues

### Middleware Problems

**Problem**: Tasks fail due to middleware configuration

**Common Issues**:
```python
# ❌ Wrong middleware order
middleware = [
    "dramatiq.middleware.Retries",      # Should be later
    "dramatiq.middleware.AgeLimit",     # Should be first
]

# ✅ Correct order
middleware = [
    "dramatiq.middleware.AgeLimit",     # Age limit first
    "dramatiq.middleware.TimeLimit",    # Time limit second
    "dramatiq.middleware.Callbacks",    # Callbacks third
    "dramatiq.middleware.Retries",      # Retries fourth
    "dramatiq.middleware.Shutdown",     # Shutdown last
]
```

### Queue Configuration

**Problem**: Tasks sent to non-existent queues

**Debugging**:
```python
# Check configured queues
from django_cfg.modules.django_tasks import get_task_service
service = get_task_service()
print("Configured queues:", service.config.dramatiq.queues)

# Check if queue exists in Redis
import redis
r = redis.Redis(host='localhost', port=6379, db=2)
queues = [key.decode() for key in r.keys('dramatiq:queue:*')]
print("Redis queues:", queues)
```

---

## 🚨 Emergency Procedures

### System Overload

**Symptoms**:
- Redis memory usage at 100%
- Workers consuming all CPU
- System unresponsive

**Immediate Actions**:
```bash
# 1. Stop all workers immediately
pkill -KILL -f rundramatiq

# 2. Check Redis memory usage
redis-cli INFO memory

# 3. Clear queues if necessary (DESTRUCTIVE)
redis-cli -n 2 FLUSHDB

# 4. Restart with minimal workers
poetry run python manage.py rundramatiq --processes 1 --threads 1
```

### Data Corruption

**Symptoms**:
- Tasks fail with serialization errors
- Redis shows corrupted data
- Unexpected task behavior

**Recovery**:
```bash
# 1. Stop all workers
pkill -f rundramatiq

# 2. Backup Redis data
redis-cli -n 2 BGSAVE

# 3. Clear corrupted queues
redis-cli -n 2 DEL dramatiq:queue:knowledge

# 4. Reset task status in Django
python manage.py shell -c "
from django_dramatiq.models import Task
Task.objects.all().delete()
"

# 5. Restart system
poetry run python manage.py rundramatiq
```

---

## 📝 Logging & Monitoring

### Enhanced Logging

```python
# Add to Django settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'dramatiq_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/dramatiq/tasks.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'dramatiq': {
            'handlers': ['dramatiq_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django_cfg.modules.django_tasks': {
            'handlers': ['dramatiq_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Health Check Script

```python
#!/usr/bin/env python
"""Health check script for Dramatiq workers."""

import redis
import subprocess
import sys

def check_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=2)
        r.ping()
        return True
    except:
        return False

def check_workers():
    try:
        result = subprocess.run(['pgrep', '-f', 'rundramatiq'], 
                              capture_output=True)
        return result.returncode == 0
    except:
        return False

def main():
    redis_ok = check_redis()
    workers_ok = check_workers()
    
    print(f"Redis: {'OK' if redis_ok else 'FAIL'}")
    print(f"Workers: {'OK' if workers_ok else 'FAIL'}")
    
    if not (redis_ok and workers_ok):
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## 🧠 Prevention Tips

### Development Best Practices

1. **Always Test Locally**: Run workers during development
2. **Monitor Queue Lengths**: Set up alerts for queue buildup
3. **Use Timeouts**: Set reasonable task timeouts
4. **Handle Failures**: Implement proper error handling
5. **Log Everything**: Add comprehensive logging

### Production Checklist

- [ ] Workers managed by process manager
- [ ] Redis persistence enabled
- [ ] Monitoring and alerting configured
- [ ] Log rotation set up
- [ ] Backup procedures in place
- [ ] Health checks implemented
- [ ] Resource limits configured

**DEPENDS_ON**: Redis, Dramatiq, Django-CFG task system
**USED_BY**: Development teams, DevOps, Production support
