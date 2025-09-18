# 🚀 Django-CFG: The Configuration Revolution

[![Python Version](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django Version](https://img.shields.io/pypi/djversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![License](https://img.shields.io/pypi/l/django-cfg.svg)](https://github.com/markolofsen/django-cfg/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)

> **Create a production-ready Django project in 30 seconds, not 30 hours.**

Skip the setup hell. Django-CFG creates a complete, modern Django project with everything you need: beautiful admin, API docs, user management, newsletter system, support tickets, and more.

## 🎯 Create Your Project Right Now

### Requirements
- **Python 3.12+** - [Download here](https://www.python.org/downloads/) or use `brew install python@3.12`

### Quick Start
```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Django-CFG
pip install django-cfg

# Create a complete project instantly
django-cfg create-project "My Awesome Project"

# Enter the project and run
cd my-awesome-project
python manage.py runserver
```

**🎉 That's it!** Your app is now running:
- **🚀 Main app:** http://127.0.0.1:8000/
- **🎯 Admin panel:** http://127.0.0.1:8000/admin/
- **📚 API docs:** http://127.0.0.1:8000/api/docs/

**That's it!** 🎉 You now have a **production-ready Django project** with:
- ✅ **Beautiful admin interface** with Unfold + Tailwind CSS  
- ✅ **Complete API documentation** with Swagger/ReDoc
- ✅ **Multi-channel user management** with email & SMS OTP authentication
- ✅ **SMS & WhatsApp integration** with Twilio out of the box
- ✅ **Support ticket system** with chat interface
- ✅ **Newsletter campaigns** with email tracking
- ✅ **Lead management** system with CRM integration
- ✅ **Multi-database routing** and connection pooling
- ✅ **Background task processing** with production-ready Dramatiq integration
- ✅ **Webhook testing** with built-in ngrok integration
- ✅ **Type-safe configuration** with full IDE support


### 📦 Alternative Installation Methods

#### Using Poetry (recommended for development)
```bash
# Create new project directory
mkdir my-project && cd my-project

# Initialize Poetry project
poetry init --no-interaction

# Add Django-CFG
poetry add django-cfg

# Create project
poetry run django-cfg create-project "My Project"
```

#### Using pipenv
```bash
# Create virtual environment and install
pipenv install django-cfg

# Create project
pipenv run django-cfg create-project "My Project"
```

#### Using conda
```bash
# Create conda environment with Python 3.12+
conda create -n myproject python=3.12
conda activate myproject

# Install Django-CFG
conda install -c conda-forge django-cfg
# OR: pip install django-cfg

# Create project
django-cfg create-project "My Project"
```

### ⚠️ Troubleshooting

#### Python Version Error
If you see an error like "django-cfg requires Python 3.12 or higher", upgrade your Python:

```bash
# macOS (using Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# Using pyenv (recommended)
pyenv install 3.12.0
pyenv global 3.12.0

# Windows
# Download from https://www.python.org/downloads/
```

#### Virtual Environment Issues
```bash
# If python3.12 command not found, check available versions:
ls /usr/bin/python*
ls /usr/local/bin/python*

# Try alternative commands:
python3.12 -m venv .venv        # Preferred
/usr/local/bin/python3.12 -m venv .venv  # Full path

# Or use virtualenv:
pip install virtualenv
virtualenv -p python3.12 .venv
```

---

## 🔥 Why Django-CFG Changes Everything

### The Problem with Traditional Django
- **500+ line settings files** that nobody wants to touch
- **Zero type safety** - typos break production
- **Manual everything** - databases, caching, admin, APIs
- **Environment hell** - different configs everywhere
- **Ugly admin interface** stuck in 2010
- **No API documentation** without hours of setup

### The Django-CFG Solution
- **Type-safe configuration** with Pydantic validation
- **100% type-safe** with full IDE support
- **Smart automation** that knows what you need
- **Environment detection** that just works
- **Beautiful modern admin** with Tailwind CSS
- **Auto-generated API docs** and client libraries

---

## 🎨 Customize Your Project

After creating your project with `django-cfg create-project`, you can customize it further:

### 1. **Environment Configuration**
```yaml
# config/config.dev.yaml
secret_key: "your-development-secret-key"
debug: true
database:
  url: "postgresql://user:pass@localhost:5432/mydb"
redis_url: "redis://localhost:6379/0"
```

### 2. **Type-Safe Configuration**
```python
# config.py - Automatically generated and customizable
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "MyAwesomeApp"  # Auto-set from CLI
    secret_key: str = env.secret_key
    debug: bool = env.debug
    project_apps: list[str] = ["accounts", "blog", "shop"]
    
    # Enable/disable built-in modules
    enable_support: bool = True      # Support ticket system
    enable_accounts: bool = True     # Advanced user management
    enable_newsletter: bool = True   # Email marketing
    enable_leads: bool = True        # Lead capture & CRM

config = MyConfig()
```

### 3. **Advanced Features**
```python
from django_cfg import DatabaseConnection, UnfoldConfig, RevolutionConfig

class ProductionConfig(DjangoConfig):
    # Multi-database setup
    databases: dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(engine="postgresql", ...),
        "analytics": DatabaseConnection(routing_apps=["analytics"]),
    }
    
    # Beautiful admin customization
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="My Admin",
        theme="auto",  # auto/light/dark
        dashboard_callback="myapp.dashboard.main_callback",
    )
    
    # Multi-zone API architecture
    revolution: RevolutionConfig = RevolutionConfig(
        zones={
            "public": ZoneConfig(apps=["blog"], public=True),
            "admin": ZoneConfig(apps=["management"], auth_required=True),
        }
    )
```

### 4. **CLI Commands & Project Info**
```bash
# Get information about available templates and CLI
django-cfg info

# Show help for all commands
django-cfg --help

# Create project with specific directory name
django-cfg create-project "My Project" --directory my-custom-dir
```

---

## 🏆 Feature Comparison

| Feature | Traditional Django | Django-CFG |
|---------|-------------------|-------------|
| **📝 Configuration** | 500+ lines of settings hell | **Type-safe & organized** |
| **🔒 Type Safety** | Pray and hope | **100% validated** |
| **🎨 Admin Interface** | Ugly 2010 design | **Modern Unfold + Tailwind** |
| **📊 Dashboard** | Basic admin index | **Real-time metrics & widgets** |
| **🗄️ Multi-Database** | Manual routing nightmare | **Smart auto-routing** |
| **⚡ Commands** | Terminal only | **Beautiful web interface** |
| **📚 API Docs** | Hours of manual setup | **Auto-generated OpenAPI** |
| **📦 Client Generation** | Write clients manually | **Auto TS/Python clients** |
| **🎫 Support System** | Build from scratch | **Built-in tickets & chat** |
| **👤 User Management** | Basic User model | **OTP auth & profiles** |
| **📧 Notifications** | Manual SMTP/webhooks | **Email & Telegram & LLM** |
| **🚀 Deployment** | Cross fingers | **Production-ready defaults** |
| **🌐 Webhook Testing** | Manual ngrok setup | **Built-in ngrok integration** |
| **🔄 Background Tasks** | Manual Celery/RQ setup | **Built-in Dramatiq integration** |
| **💡 IDE Support** | Basic syntax highlighting | **Full IntelliSense paradise** |
| **🐛 Config Errors** | Runtime surprises | **Compile-time validation** |
| **😊 Developer Joy** | Constant frustration | **Pure coding bliss** |

---

## 🎯 Core Features

### 🔒 **Type-Safe Configuration**
Full Pydantic validation with IDE autocomplete and compile-time error checking.

### 🎨 **Beautiful Admin Interface**
Modern Django Unfold admin with Tailwind CSS, dark mode, and custom dashboards.

### 📊 **Real-Time Dashboard**
Live metrics, system health, and custom widgets that update automatically.

### 🗄️ **Smart Multi-Database**
Automatic database routing based on app labels with connection pooling.

### ⚡ **Web Command Interface**
Run Django management commands from a beautiful web interface with real-time logs.

### 📚 **Auto API Documentation**
OpenAPI/Swagger docs generated automatically with zone-based architecture.

### 📦 **Client Generation**
TypeScript and Python API clients generated per zone automatically.

### 🎫 **Built-in Support System**
Complete ticket management with modern chat interface, email notifications, and admin integration.

### 👤 **Advanced User Management**
Built-in accounts system with OTP authentication, user profiles, activity tracking, and registration sources.

### 📧 **Built-in Modules**
Email, Telegram, SMS (Twilio), LLM integration, Support ticket system, Newsletter campaigns, Lead management, and advanced User management ready out of the box.

### 🌍 **Environment Detection**
Automatic dev/staging/production detection with appropriate defaults.

### 🌐 **Built-in Ngrok Integration**
Instant webhook testing with zero-config ngrok tunnels for development.

### 🔄 **Background Task Processing** %%PRIORITY:HIGH%%

Django-CFG includes a complete Dramatiq integration for reliable background job processing with automatic Redis configuration, worker management, and task monitoring.

#### Features
- **🚀 Zero Configuration** - Automatic Redis broker setup and queue management
- **⚡ Smart Worker Management** - Built-in `rundramatiq` command with Django settings integration
- **🔧 Type-Safe Task Definition** - Full IDE support for task creation and scheduling
- **📊 Task Monitoring** - Built-in commands for queue status and task management
- **🐳 Docker Ready** - Pre-configured Docker containers for production deployment
- **🛡️ Production Tested** - Battle-tested configuration used in production environments

#### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    
    # Dramatiq configuration (automatic)
    redis_url: str = "redis://localhost:6379/2"  # Separate DB for tasks
    
    # Optional: Custom task settings
    dramatiq: DramatiqConfig = DramatiqConfig(
        processes=2,           # Worker processes
        threads=4,            # Threads per process
        redis_db=2,           # Redis database for tasks
        queues=["default", "high", "low"]  # Available queues
    )

config = MyConfig()
```

#### Task Definition
```python
import dramatiq
from django_cfg.modules.django_tasks import get_broker

# Tasks are automatically discovered from your apps
@dramatiq.actor(queue_name="high", max_retries=3)
def process_document(document_id: str) -> dict:
    """Process document asynchronously with full Django context."""
    from myapp.models import Document
    
    document = Document.objects.get(id=document_id)
    # Your processing logic here
    document.status = "processed"
    document.save()
    
    return {"status": "completed", "document_id": document_id}

# Queue the task
process_document.send(document_id="123")
```

#### Management Commands
```bash
# Start Dramatiq workers with Django settings
python manage.py rundramatiq --processes 4 --threads 8

# Monitor task queues and status
python manage.py task_status --queue high

# Clear specific queues
python manage.py task_clear --queue default

# Test task processing pipeline
python manage.py test_tasks
```

#### Docker Integration
```yaml
# docker-compose.yml (automatically generated)
services:
  app-dramatiq:
    build: .
    command: ["python", "manage.py", "rundramatiq"]
    environment:
      - DRAMATIQ_PROCESSES=2
      - DRAMATIQ_THREADS=4
      - DRAMATIQ_QUEUES=default,high,low
    depends_on:
      - redis
      - postgres
```

#### Production Features
- **🔄 Automatic Restart** - Workers restart on code changes in development
- **📈 Scaling** - Easy horizontal scaling with multiple worker containers
- **🛡️ Error Handling** - Built-in retry logic and dead letter queues
- **📊 Monitoring** - Integration with Django admin for task monitoring
- **⚡ Performance** - Optimized Redis configuration for high throughput

#### Real-World Example
```python
# Document processing pipeline
@dramatiq.actor(queue_name="knowledge", max_retries=2)
def process_document_async(document_id: str) -> dict:
    """Complete document processing with chunking and embeddings."""
    try:
        document = Document.objects.get(id=document_id)
        
        # Step 1: Chunk document
        chunks = create_document_chunks(document)
        
        # Step 2: Generate embeddings
        for chunk in chunks:
            generate_embeddings.send(chunk.id)
        
        # Step 3: Optimize database
        optimize_document_embeddings.send(document_id)
        
        return {"status": "completed", "chunks_created": len(chunks)}
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return {"status": "failed", "error": str(e)}

# Triggered automatically via Django signals
@receiver(post_save, sender=Document)
def queue_document_processing(sender, instance, created, **kwargs):
    if created:
        process_document_async.send(str(instance.id))
```

**Perfect for:**
- 📄 **Document Processing** - PDF parsing, text extraction, embeddings
- 📧 **Email Campaigns** - Bulk email sending with delivery tracking
- 🔄 **Data Synchronization** - API integrations and data imports
- 📊 **Report Generation** - Heavy computational tasks
- 🧹 **Cleanup Tasks** - Database maintenance and optimization

---

## 🛠️ Management Commands (CLI Tools)

Django-CFG includes powerful management commands for development and operations:

### 🗄️ Database & Migration Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`migrator`** | Interactive database migration tool with multi-DB support | `python manage.py migrator --auto` |
| **`migrate_all`** | Simple migration command for all databases (production-ready) | `python manage.py migrate_all --dry-run` |

**Migration Command Details:**
- **`migrator`** - Full-featured migration tool with interactive menu, database status, and diagnostics
  - `python manage.py migrator` - Interactive menu with all options
  - `python manage.py migrator --auto` - Automatic migration of all databases
  - `python manage.py migrator --database vehicles` - Migrate specific database only
  - `python manage.py migrator --app vehicles_data` - Migrate specific app across all databases
- **`migrate_all`** - Simplified migration tool optimized for production and CI/CD
  - `python manage.py migrate_all` - Migrate all databases automatically
  - `python manage.py migrate_all --dry-run` - Show what would be migrated without executing
  - `python manage.py migrate_all --skip-makemigrations` - Skip makemigrations step

### 🔧 Configuration & Validation Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`check_settings`** | Validate configuration and settings | `python manage.py check_settings` |
| **`show_config`** | Display current configuration | `python manage.py show_config --format yaml` |
| **`validate_config`** | Deep validation of all settings | `python manage.py validate_config --strict` |
| **`tree`** | Display Django project structure | `python manage.py tree --depth 3 --include-docs` |

### 🚀 API & Development Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`create_token`** | Generate API tokens and keys | `python manage.py create_token --user admin` |
| **`generate`** | Generate API clients and documentation | `python manage.py generate --zone client` |
| **`show_urls`** | Display all URL patterns | `python manage.py show_urls --zone client` |
| **`script`** | Run custom scripts with Django context | `python manage.py script my_script.py` |
| **`runserver_ngrok`** | Run development server with ngrok tunnel | `python manage.py runserver_ngrok --domain custom` |

### 👤 User & Authentication Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`superuser`** | Create superuser with smart defaults | `python manage.py superuser --email admin@example.com` |

### 📧 Communication & Integration Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`test_email`** | Test email configuration | `python manage.py test_email --to test@example.com` |
| **`test_telegram`** | Test Telegram bot integration | `python manage.py test_telegram --chat_id 123` |
| **`test_twilio`** | Test Twilio SMS and WhatsApp integration | `python manage.py test_twilio` |
| **`translate_content`** | Translate JSON with LLM and smart caching | `python manage.py translate_content --target-lang es` |

### 🎫 Built-in Module Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`support_stats`** | Display support ticket statistics | `python manage.py support_stats --format json` |
| **`test_newsletter`** | Test newsletter sending functionality | `python manage.py test_newsletter --email test@example.com` |
| **`newsletter_stats`** | Display newsletter campaign statistics | `python manage.py newsletter_stats --format json` |
| **`leads_stats`** | Display lead conversion statistics | `python manage.py leads_stats --format json` |

### 🔄 Background Task Commands
| Command | Description | Example |
|---------|-------------|---------|
| **`rundramatiq`** | Run Dramatiq background task workers | `python manage.py rundramatiq --processes 4` |
| **`task_status`** | Show Dramatiq task status and queues | `python manage.py task_status --queue high` |
| **`task_clear`** | Clear Dramatiq queues | `python manage.py task_clear --queue default` |
| **`test_tasks`** | Test Dramatiq task processing pipeline | `python manage.py test_tasks --document-id 123` |

---

## 🌍 Environment Detection

Django-CFG automatically detects your environment and applies appropriate settings:

| Environment | Detection Method | Cache Backend | Email Backend | Database SSL | Debug Mode |
|-------------|------------------|---------------|---------------|--------------|------------|
| **Development** | `DEBUG=True` or local domains | Memory/Redis | Console | Optional | `True` |
| **Testing** | `pytest` or `test` in command | Dummy Cache | In-Memory | Disabled | `False` |
| **Staging** | `STAGING=True` or staging domains | Redis | SMTP | Required | `False` |
| **Production** | `PRODUCTION=True` or prod domains | Redis | SMTP | Required | `False` |

---

## 📝 Logging System

Comprehensive logging with environment-aware configuration:

```python
# Automatic log configuration based on environment
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

**Features:**
- Environment-specific log levels
- Automatic file rotation
- Structured logging with JSON support
- Integration with monitoring systems
- Custom formatters for different outputs

---

## 📚 API Documentation

Django-CFG provides ready-made Redoc/Swagger solutions for each API zone:

### Zone-Based API Architecture
```python
revolution: RevolutionConfig = RevolutionConfig(
    zones={
        "client": ZoneConfig(
            apps=["accounts", "billing"],
            title="Client API",
            public=True,
        ),
        "admin": ZoneConfig(
            apps=["management", "reports"],
            title="Admin API", 
            auth_required=True,
        ),
    }
)
```

### Automatic Documentation URLs
- **`/api/client/docs/`** - Interactive Swagger UI for client zone
- **`/api/client/redoc/`** - Beautiful ReDoc documentation
- **`/api/admin/docs/`** - Admin zone Swagger UI
- **`/api/admin/redoc/`** - Admin zone ReDoc

### Client Generation
```bash
# Generate TypeScript client for client zone
python manage.py generate --zone client --format typescript

# Generate Python client for admin zone  
python manage.py generate --zone admin --format python
```

---

## 🎫 Built-in Support System

Django-CFG includes a complete support ticket system with modern chat interface:

### Features
- **🎯 Ticket Management** - Create, assign, and track support tickets
- **💬 Chat Interface** - Beautiful Tailwind CSS chat UI for conversations  
- **📧 Email Integration** - Automatic notifications for ticket updates
- **👥 User Management** - Support for both staff and customer interactions
- **📊 Dashboard Integration** - Real-time metrics in Unfold admin
- **🔗 API Ready** - RESTful API endpoints for all support operations

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_support: bool = True  # That's it!

config = MyConfig()
```

### Automatic Integration
- ✅ **Admin Interface** - Support section in sidebar with tickets & messages
- ✅ **Dashboard Cards** - Live ticket statistics and quick actions  
- ✅ **API Endpoints** - `/api/support/` zone with full CRUD operations
- ✅ **Email Templates** - Beautiful HTML emails with your branding
- ✅ **Chat Interface** - Modern `/support/chat/{ticket_uuid}/` pages

### Disable Support (Optional)
```python
enable_support: bool = False  # Removes from admin, API, and dashboard
```

---

## 📧 Built-in Newsletter System

Django-CFG includes a complete newsletter and email marketing system with tracking and analytics:

### Features
- **📬 Newsletter Management** - Create, schedule, and manage email newsletters
- **👥 Subscription Management** - User subscriptions with double opt-in and unsubscribe
- **📊 Email Tracking** - Open rates, click tracking, and engagement analytics
- **🎯 Campaign System** - Organize newsletters into campaigns with templates
- **📈 Bulk Email** - Send to thousands of subscribers with delivery tracking
- **🔗 API Ready** - RESTful API endpoints for all newsletter operations
- **📱 Email Templates** - Beautiful responsive HTML templates with tracking pixels

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_newsletter: bool = True  # That's it!

config = MyConfig()
```

### Automatic Integration
- ✅ **Admin Interface** - Newsletter section with campaigns, subscriptions & email logs
- ✅ **Dashboard Cards** - Live newsletter statistics and recent campaigns
- ✅ **API Endpoints** - `/api/newsletter/` zone with full CRUD operations
- ✅ **Email Templates** - Responsive HTML emails with your branding and tracking
- ✅ **Tracking System** - Automatic open/click tracking with UUID-based security
- ✅ **Subscription Forms** - Ready-to-use subscription and unsubscribe endpoints

### Email Tracking Features
```python
from django_cfg.apps.newsletter.services.email_service import NewsletterEmailService

# Send newsletter with tracking
service = NewsletterEmailService()
result = service.send_newsletter_email(
    newsletter=newsletter,
    subject="Monthly Update",
    email_title="Our Latest News",
    main_text="Check out what's new this month!",
    button_text="Read More",
    button_url="https://example.com/news",
    send_to_all=True  # Send to all subscribers
)
```

### Disable Newsletter (Optional)
```python
enable_newsletter: bool = False  # Removes from admin, API, and dashboard
```

---

## 🎯 Built-in Lead Management System

Django-CFG includes a comprehensive lead collection and CRM system for capturing and managing potential customers:

### Features
- **📝 Lead Capture** - Collect leads from contact forms, landing pages, and API
- **🏷️ Lead Sources** - Track where leads came from (web, mobile, ads, referrals)
- **📊 Lead Scoring** - Automatic scoring based on engagement and profile data
- **🔄 Status Management** - Lead lifecycle from new to converted or closed
- **📧 Email Integration** - Automatic notifications for new leads and status changes
- **📱 API Ready** - RESTful API endpoints for all lead operations
- **🎯 CRM Integration** - Ready for integration with external CRM systems

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_leads: bool = True  # That's it!

config = MyConfig()
```

### Automatic Integration
- ✅ **Admin Interface** - Leads section with lead management and source tracking
- ✅ **Dashboard Cards** - Live lead statistics and conversion metrics
- ✅ **API Endpoints** - `/api/leads/` zone with full CRUD operations
- ✅ **Contact Forms** - Ready-to-use lead capture forms and endpoints
- ✅ **Email Notifications** - Automatic alerts for new leads and status changes
- ✅ **Source Tracking** - Automatic detection of lead sources and campaigns

### Lead Capture Example
```python
from django_cfg.apps.leads.models import Lead, LeadSource

# Create lead from contact form
lead = Lead.objects.create(
    name="John Doe",
    email="john@example.com",
    phone="+1234567890",
    message="Interested in your services",
    source=LeadSource.objects.get(name="Website Contact Form"),
    status=Lead.LeadStatus.NEW
)
```

### Disable Leads (Optional)
```python
enable_leads: bool = False  # Removes from admin, API, and dashboard
```

---

## 👤 Built-in User Management System

Django-CFG includes a comprehensive user management system with OTP authentication, profiles, and activity tracking:

### Features
- **🔐 Multi-Channel OTP Authentication** - Secure one-time password authentication via email and SMS
- **📱 Phone Number Support** - Complete phone verification with Twilio SMS integration
- **👥 Custom User Model** - Extended user model with profiles and metadata
- **📊 Activity Tracking** - Complete audit trail of user actions and logins
- **🔗 Registration Sources** - Track where users came from (web, mobile, API, etc.)
- **📧 Email Integration** - Beautiful welcome emails and OTP notifications
- **💬 SMS Integration** - Twilio-powered SMS delivery for phone verification
- **🛡️ Security Features** - Failed attempt tracking, account lockouts, and audit logs
- **📱 API Ready** - RESTful API endpoints for all user operations

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_accounts: bool = True  # That's it!
    # auth_user_model is automatically set to django_cfg_accounts.CustomUser

config = MyConfig()
```

### Automatic Integration
- ✅ **Custom User Model** - Automatically sets `AUTH_USER_MODEL` to `django_cfg_accounts.CustomUser`
- ✅ **Admin Interface** - "Users & Access" section with users, groups, and registration sources
- ✅ **Dashboard Integration** - User statistics and recent activity widgets
- ✅ **API Endpoints** - `/api/accounts/` zone with authentication, profiles, and OTP
- ✅ **Email Templates** - Welcome emails and OTP verification with your branding
- ✅ **Migration Safety** - Smart migration ordering to avoid conflicts

### Multi-Channel OTP Authentication Flow
```python
from django_cfg.apps.accounts.services.otp_service import OTPService

# Email OTP (traditional)
success, error = OTPService.request_email_otp("user@example.com")
user = OTPService.verify_email_otp("user@example.com", "123456")

# Phone OTP (SMS via Twilio)
success, error = OTPService.request_phone_otp("+1234567890")
user = OTPService.verify_phone_otp("+1234567890", "123456")

# Auto-detect channel (unified API)
success, error = OTPService.request_otp("user@example.com")  # Email
success, error = OTPService.request_otp("+1234567890")       # Phone
```

### Twilio SMS Configuration
```yaml
# config.dev.yaml
twilio:
  account_sid: "your-twilio-account-sid"
  auth_token: "your-twilio-auth-token"
  sms_from: "+1234567890"  # Your Twilio phone number
  whatsapp_from: "+14155238886"  # WhatsApp sandbox (optional)
```

### Custom User Model Features
- **Extended Profile** - Additional fields for user metadata including phone numbers
- **Phone Verification** - Built-in phone verification with SMS OTP
- **Activity Tracking** - Automatic logging of user actions and authentication events
- **Registration Sources** - Track user acquisition channels (email vs phone signup)
- **Security Audit** - Failed login attempts and security events

### Disable Accounts (Optional)
```python
enable_accounts: bool = False  # Uses Django's default User model
```

---

## 🤖 Built-in LLM Integration

Django-CFG includes a powerful LLM module for AI-powered features like translation, content generation, and smart automation:

### Features
- **🌍 Smart Translation** - JSON translation with intelligent caching by language pairs
- **💬 LLM Client** - OpenAI/OpenRouter integration with dynamic pricing and cost tracking
- **⚡ Smart Caching** - Text-level caching that sends only uncached content to LLM
- **🔧 Direct Injection** - No configuration needed, just inject `LLMClient` where needed
- **📊 Cost Tracking** - Real-time cost calculation with dynamic model pricing
- **🛡️ Production Ready** - Built-in error handling, retries, and fallbacks

### Quick Usage
```python
from django_cfg.modules.django_llm import LLMClient, DjangoTranslator

# Direct LLM usage
client = LLMClient(provider="openrouter", api_key="your-key")
response = client.chat_completion([{"role": "user", "content": "Hello!"}])

# Smart JSON translation with caching
translator = DjangoTranslator(client=client)
translated = translator.translate_json(
    data={"greeting": "Hello", "message": "Welcome to our app"},
    target_language="es"
)
# Result: {"greeting": "Hola", "message": "Bienvenido a nuestra aplicación"}
```

### Management Command
```bash
# Translate JSON content with smart caching
python manage.py translate_content --target-lang es --json '{"title": "Hello World"}'
```

### Key Benefits
- **Zero Configuration** - Works out of the box with environment variables
- **Smart Caching** - Dramatically reduces LLM costs with intelligent text-level caching
- **Language Detection** - Automatic source language detection for better translations
- **Cost Optimization** - Only sends uncached texts to LLM, reuses cached translations

---

## 🌐 Built-in Ngrok Integration

Django-CFG includes seamless ngrok integration for instant webhook testing and external API development:

### Features
- **🚀 Zero Configuration** - Works out of the box with automatic tunnel creation
- **🔐 Secure Tunnels** - HTTPS tunnels with automatic ALLOWED_HOSTS management
- **⚡ Auto URL Updates** - Automatically updates `api_url` when tunnel is active
- **🎯 Webhook Ready** - Perfect for testing webhooks, APIs, and external integrations
- **🛠️ Development Focused** - Only enabled in DEBUG mode for safety
- **📱 Custom Domains** - Support for custom ngrok domains and subdomains

### Quick Setup
```python
from django_cfg import DjangoConfig
from django_cfg.models.ngrok import NgrokConfig, NgrokAuthConfig, NgrokTunnelConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    debug: bool = True
    
    # Ngrok configuration (optional)
    ngrok: Optional[NgrokConfig] = NgrokConfig(
        enabled=True,
        auth=NgrokAuthConfig(
            authtoken="your-ngrok-authtoken",  # Get from ngrok.com
        ),
        tunnel=NgrokTunnelConfig(
            schemes=["https"],  # HTTPS for webhooks
            compression=True,
        ),
        auto_start=True,  # Start with runserver_ngrok
        update_api_url=True,  # Update api_url automatically
        webhook_path="/webhooks/",  # Default webhook path
    )

config = MyConfig()
```

### Usage
```bash
# Run development server with ngrok tunnel
python manage.py runserver_ngrok

# With custom domain
python manage.py runserver_ngrok --domain myapp

# With custom port
python manage.py runserver_ngrok 0.0.0.0:8080

# Disable ngrok for this session
python manage.py runserver_ngrok --no-ngrok
```

### Automatic Features
- ✅ **HTTPS Tunnel** - Secure tunnel with automatic SSL
- ✅ **ALLOWED_HOSTS** - Automatically adds ngrok domain to Django settings
- ✅ **API URL Updates** - Updates `api_url` config to tunnel URL
- ✅ **Webhook URLs** - Easy webhook URL generation with `get_webhook_url()`
- ✅ **Development Safety** - Only works in DEBUG mode
- ✅ **Error Handling** - Graceful fallback if ngrok is unavailable

### Webhook Testing Example
```python
from django_cfg.modules.django_ngrok import get_ngrok_service

# Get webhook URL for external services
ngrok_service = get_ngrok_service()
webhook_url = ngrok_service.get_webhook_url("stripe/webhook/")
# Result: https://abc123.ngrok-free.app/webhooks/stripe/webhook/

# Use this URL in external service configuration (Stripe, GitHub, etc.)
```

### Environment Configuration
```yaml
# config.dev.yaml
ngrok:
  authtoken: "your-ngrok-authtoken-here"
```

**Perfect for:**
- 🎯 **Webhook Development** - Test Stripe, GitHub, Slack webhooks locally
- 🔗 **API Integration** - Share your local API with external services
- 📱 **Mobile Testing** - Test your API from mobile devices
- 🤝 **Client Demos** - Show your work to clients instantly

---

## 🏗️ Real-World Example

Here's a complete production configuration:

```python
from django_cfg import DjangoConfig, DatabaseConnection, UnfoldConfig, RevolutionConfig

class ProductionConfig(DjangoConfig):
    """🚀 Production-ready configuration"""
    
    # === Project Settings ===
    project_name: str = "CarAPIS"
    project_version: str = "2.0.0"
    secret_key: str = env.secret_key
    debug: bool = False
    
    # === Multi-Database Setup ===
    databases: dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="carapis_main",
            user=env.db_user,
            password=env.db_password,
            host=env.db_host,
            port=5432,
            sslmode="require",
        ),
        "analytics": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="carapis_analytics", 
            user=env.db_user,
            password=env.db_password,
            host=env.db_host,
            routing_apps=["analytics", "reports"],
        ),
    }
    
    # === Beautiful Admin ===
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="CarAPIS Admin",
        site_header="CarAPIS Control Center",
        theme="auto",
        dashboard_callback="api.dashboard.main_callback",
    )
    
    # === Built-in Modules ===
    enable_support: bool = True     # Automatic tickets, chat interface, email notifications
    enable_accounts: bool = True    # Advanced user management with OTP authentication
    enable_newsletter: bool = True  # Email marketing, campaigns, tracking & analytics
    enable_leads: bool = True       # Lead capture, CRM integration, source tracking
    
    # === Background Task Processing ===
    redis_url: str = "redis://redis:6379/2"  # Separate DB for Dramatiq tasks
    dramatiq: DramatiqConfig = DramatiqConfig(
        processes=4,              # Production worker processes
        threads=8,               # Threads per process for I/O bound tasks
        redis_db=2,              # Dedicated Redis DB for task queues
        queues=["default", "high", "low", "knowledge", "email"],  # Production queues
        max_retries=3,           # Default retry attempts
        max_age=3600000,         # 1 hour max task age (milliseconds)
    )
    
    # === Multi-Zone API ===
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api/v2",
        zones={
            "public": ZoneConfig(
                apps=["cars", "search"],
                title="Public API",
                description="Car data and search",
                public=True,
            ),
            "partner": ZoneConfig(
                apps=["integrations", "webhooks"],
                title="Partner API",
                auth_required=True,
                rate_limit="1000/hour",
            ),
        }
    )

config = ProductionConfig()
```

---

## 🧪 Testing

Django-CFG includes comprehensive testing utilities:

```python
def test_configuration():
    """Test your configuration is valid"""
    config = MyConfig()
    settings = config.get_all_settings()
    
    # Validate required settings
    assert "SECRET_KEY" in settings
    assert settings["DEBUG"] is False
    assert "myapp" in settings["INSTALLED_APPS"]
    
    # Test database connections
    assert "default" in settings["DATABASES"]
    assert settings["DATABASES"]["default"]["ENGINE"] == "django.db.backends.postgresql"
    
    # Validate API configuration
    assert "SPECTACULAR_SETTINGS" in settings
    assert settings["SPECTACULAR_SETTINGS"]["TITLE"] == "My API"
```

---

## 🔄 Migrating Existing Django Projects

### Option 1: Start Fresh (Recommended)
```bash
# Create new project with Django-CFG
django-cfg create-project "My Migrated Project"

# Copy your apps and models to the new structure
# Migrate your data using Django's dumpdata/loaddata
```

### Option 2: Gradual Migration
```bash
# Install Django-CFG in existing project
pip install django-cfg

# Create configuration class
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "Existing Project"
    secret_key: str = "your-existing-secret"
    project_apps: list[str] = ["your_app1", "your_app2"]

config = MyConfig()
```

```python
# Replace your settings.py content with:
from .config import config
globals().update(config.get_all_settings())
```

### Option 3: Side-by-Side Comparison
```bash
# Create reference project to compare
django-cfg create-project "Reference Project"

# Compare configurations and gradually adopt features
# Perfect for learning Django-CFG patterns
```

**Result:** Transform your legacy Django project into a modern, type-safe, feature-rich application! 🎉

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
git clone https://github.com/markolofsen/django-cfg.git
cd django-cfg
poetry install
poetry run pytest
```

### Development Commands
```bash
# Run tests
poetry run pytest

# Format code
poetry run black .

# Type checking
poetry run mypy .

# Build package
poetry build
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists with deadlines
- **Pydantic** - Data validation using Python type hints
- **Django Unfold** - Beautiful modern admin interface
- **Django Revolution** - API generation and zone management

---

**Made with ❤️ by the ReformsAI Team**

*Django-CFG: Because configuration should be simple, safe, and powerful.*
