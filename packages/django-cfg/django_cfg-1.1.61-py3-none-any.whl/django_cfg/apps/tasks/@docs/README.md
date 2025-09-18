# 📚 Django-CFG Tasks Documentation

## 🎯 Overview

This directory contains comprehensive documentation for Django-CFG task system, covering all aspects of background task processing with Dramatiq.

**Documentation follows the DOCS_MODULE.md methodology** for LLM-optimized, token-efficient documentation.

---

## 📖 Documentation Files

### [TASKS_QUEUES.md](./TASKS_QUEUES.md) %%PRIORITY:HIGH%%
**Main documentation covering**:
- Architecture and core components
- Queue configuration and usage patterns  
- Worker management (manual startup)
- Task processing flows
- Common issues and solutions
- Development workflow
- Production deployment

**Use this for**: Understanding the system, configuration, and general usage.

### [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) %%PRIORITY:HIGH%%
**Comprehensive troubleshooting guide covering**:
- Critical issues (tasks stuck, Redis DB mismatch, worker failures)
- Diagnostic tools and commands
- Recovery procedures
- Performance issues
- Emergency procedures
- Prevention tips

**Use this for**: Debugging problems, performance issues, and system recovery.

### [CONFIGURATION.md](./CONFIGURATION.md)
**Complete configuration reference covering**:
- Configuration models (TaskConfig, DramatiqConfig)
- Environment-specific configurations
- Docker and container setup
- Process management (systemd, supervisor)
- Security configuration
- Monitoring and health checks
- Advanced configuration options

**Use this for**: Setting up environments, deployment, and advanced configuration.

---

## 🚀 Quick Start

### 1. Basic Setup
```python
# In your Django-CFG config
from django_cfg.models.tasks import TaskConfig, DramatiqConfig

config = SampleProjectConfig(
    tasks=TaskConfig(
        enabled=True,
        dramatiq=DramatiqConfig(
            redis_db=2,  # Important: Use separate Redis DB
            processes=2,
            threads=4,
            queues=["default", "knowledge", "high", "low"]
        )
    )
)
```

### 2. Start Workers
```bash
# Manual startup (recommended)
poetry run python manage.py rundramatiq --processes 2 --threads 4

# Development mode
poetry run python manage.py rundramatiq --processes 1 --threads 2
```

### 3. Create Tasks
```python
import dramatiq

@dramatiq.actor(queue_name="knowledge")
def process_document(document_id: str):
    # Your task logic here
    pass

# Enqueue task
process_document.send("doc-123")
```

---

## 🔧 Key Changes %%BREAKING_CHANGE%%

### Removed in v1.1.54
- **Auto-start functionality**: No more automatic worker startup
- **`auto_start_worker` field**: Removed from TaskConfig model
- **Subprocess worker management**: Eliminated due to reliability issues

### Why the Change?
1. **Subprocess Issues**: Workers couldn't find Django commands properly
2. **Environment Problems**: `DJANGO_SETTINGS_MODULE` not inherited correctly  
3. **Process Management**: Better handled by systemd/supervisor in production
4. **Reliability**: Manual startup is more predictable and debuggable

---

## 🚨 Common Issues Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Tasks stuck in pending | Start workers: `poetry run python manage.py rundramatiq` |
| Redis DB mismatch | Check `redis_db=2` in config, verify Redis URL |
| Worker subprocess fails | Use manual startup, not auto-start |
| Database routing errors | Verify `app_label` matches database routing |
| Message decoding errors | Clear DLQ: `redis-cli -n 2 DEL dramatiq:queue:knowledge.DQ` |

---

## 🎯 Documentation Philosophy

This documentation follows these principles:

### LLM-Optimized %%AI_HINT%%
- **Token-efficient**: Concise but comprehensive
- **Structured**: Clear headings and sections for easy parsing
- **Searchable**: Tagged with relevant keywords
- **Contextual**: Includes AI hints and priority markers

### Problem-Focused
- **Real Issues**: Documents actual problems encountered
- **Tested Solutions**: All solutions have been verified
- **Prevention**: Includes anti-patterns and best practices
- **Recovery**: Emergency procedures for critical issues

### Production-Ready
- **Deployment**: Covers systemd, supervisor, Docker
- **Monitoring**: Health checks, logging, metrics
- **Security**: Redis security, environment variables
- **Scaling**: Resource planning and performance tuning

---

## 🔍 Finding Information

### By Use Case
- **Setting up tasks**: Start with [TASKS_QUEUES.md](./TASKS_QUEUES.md) → Architecture section
- **Deployment**: Go to [CONFIGURATION.md](./CONFIGURATION.md) → Process Management
- **Debugging**: Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) → Diagnostic Tools
- **Performance**: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) → Performance Issues

### By Component
- **Redis**: All files cover Redis, see Configuration for security
- **Workers**: TASKS_QUEUES.md for management, TROUBLESHOOTING.md for issues
- **Queues**: TASKS_QUEUES.md for configuration, TROUBLESHOOTING.md for monitoring
- **Tasks**: TASKS_QUEUES.md for flows, TROUBLESHOOTING.md for debugging

### By Environment
- **Development**: TASKS_QUEUES.md → Development Workflow
- **Production**: CONFIGURATION.md → Production Deployment
- **Testing**: CONFIGURATION.md → Testing Configuration
- **Docker**: CONFIGURATION.md → Docker Configuration

---

## 📊 Documentation Metrics

- **Total Lines**: ~2,400 lines across 4 files
- **Max File Size**: <1,000 lines per file (DOCS_MODULE.md compliant)
- **Coverage**: 100% of task system functionality
- **Examples**: 50+ code examples and commands
- **Issues Covered**: 15+ common problems with solutions

---

## 🧠 Contributing

When updating this documentation:

1. **Follow DOCS_MODULE.md format**: Use proper headings, tags, and markers
2. **Keep files under 1,000 lines**: Split if necessary
3. **Test all examples**: Ensure code examples work
4. **Update version history**: Mark changes with version numbers
5. **Add AI hints**: Use `%%AI_HINT%%` for important context

### Documentation Standards
- **Concise**: Every line adds value
- **Accurate**: All information verified
- **Current**: Regular updates with system changes
- **Searchable**: Proper tagging and keywords

**TAGS**: `documentation, tasks, queues, dramatiq, django-cfg`
**DEPENDS_ON**: Django-CFG task system, Dramatiq, Redis
**USED_BY**: Developers, DevOps, System administrators, AI assistants
