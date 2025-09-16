# Ngrok Environment Variables Support

Django-CFG now supports automatic retrieval of ngrok URLs from environment variables that are set by the `runserver_ngrok` command.

## 🚀 How it works

1. **The `runserver_ngrok` command** automatically sets environment variables when starting the ngrok tunnel
2. **The `django_ngrok` module** can retrieve URLs from both the active manager and environment variables
3. **The `DjangoConfig` class** provides a convenient `get_ngrok_url()` method to get the current URL

## 📋 Environment Variables

When running `python manage.py runserver_ngrok`, the following variables are automatically set:

```bash
NGROK_URL=https://abc123.ngrok.io           # Main tunnel URL
DJANGO_NGROK_URL=https://abc123.ngrok.io    # Duplicate variable
NGROK_HOST=abc123.ngrok.io                  # Host only
NGROK_SCHEME=https                          # Scheme (http/https)
NGROK_API_URL=https://abc123.ngrok.io       # API URL (usually the same)
```

## 🛠 Methods for retrieving URLs

### In the `django_ngrok` module

```python
from django_cfg.modules.django_ngrok import (
    get_tunnel_url_from_env,        # Get URL from env variables
    get_ngrok_host_from_env,        # Get host from env variables  
    is_ngrok_available_from_env,    # Check availability in env
    get_effective_tunnel_url        # Get URL (manager or env)
)

# Usage examples
tunnel_url = get_tunnel_url_from_env()  # https://abc123.ngrok.io
ngrok_host = get_ngrok_host_from_env()  # abc123.ngrok.io
is_available = is_ngrok_available_from_env()  # True/False
effective_url = get_effective_tunnel_url()  # Priority: manager -> env
```

### In the `DjangoConfig` class

```python
from django_cfg.core.config import DjangoConfig

config = DjangoConfig(...)

# Get ngrok URL with optional path
base_url = config.get_ngrok_url()                    # https://abc123.ngrok.io
webhook_url = config.get_ngrok_url("/api/webhooks/") # https://abc123.ngrok.io/api/webhooks/
admin_url = config.get_ngrok_url("/admin/")          # https://abc123.ngrok.io/admin/

# Returns None if ngrok is not available
if config.get_ngrok_url():
    print("Ngrok is active!")
```

## 📝 Usage Examples

### 1. In webhook handler

```python
def create_payment_webhook(request):
    config = get_current_config()
    
    # Get current callback URL
    callback_url = config.get_ngrok_url("/api/payments/webhooks/nowpayments/")
    
    if callback_url:
        # Use ngrok URL
        payment_data = {
            "callback_url": callback_url,
            "amount": 100.0,
            "currency": "USD"
        }
    else:
        # Fallback to regular URL
        payment_data = {
            "callback_url": config.get_site_url("/api/payments/webhooks/nowpayments/"),
            "amount": 100.0,
            "currency": "USD"
        }
    
    return create_payment(payment_data)
```

### 2. In payment service

```python
from django_cfg.modules.django_ngrok import get_webhook_url

class PaymentService:
    def create_nowpayments_invoice(self, amount, currency):
        # Automatically gets ngrok URL or fallback
        webhook_url = get_webhook_url("/api/payments/webhooks/nowpayments/")
        
        return {
            "amount": amount,
            "currency": currency,
            "callback_url": webhook_url,
            "success_url": get_webhook_url("/payment/success/"),
            "cancel_url": get_webhook_url("/payment/cancel/")
        }
```

### 3. In Django settings

```python
# settings.py
from django_cfg.modules.django_ngrok import get_tunnel_url_from_env

# Get ngrok URL for ALLOWED_HOSTS
NGROK_URL = get_tunnel_url_from_env()
if NGROK_URL:
    from urllib.parse import urlparse
    ALLOWED_HOSTS.append(urlparse(NGROK_URL).netloc)
```

## 🔄 URL Retrieval Priority

URL retrieval methods work in the following priority order:

1. **Active ngrok manager** - if tunnel is running programmatically
2. **Environment variables** - if set by the `runserver_ngrok` command
3. **Fallback to config.api_url** - for methods with fallback support

## ⚡ Quick Start

1. **Configure ngrok in your settings:**

```python
from django_cfg.core.config import DjangoConfig
from django_cfg.models.ngrok import NgrokConfig

class MyConfig(DjangoConfig):
    project_name = "My Project"
    secret_key = "your-secret-key"
    
    ngrok = NgrokConfig(
        enabled=True,
        auto_start=True,
        update_api_url=True
    )
```

2. **Start server with ngrok:**

```bash
python manage.py runserver_ngrok
```

3. **Use in your code:**

```python
# Get current ngrok URL
config = get_current_config()
webhook_url = config.get_ngrok_url("/api/webhooks/")

# Or directly from module
from django_cfg.modules.django_ngrok import get_effective_tunnel_url
tunnel_url = get_effective_tunnel_url()
```

## 🎯 Benefits

- ✅ **Automatic detection** - URL is retrieved automatically from environment variables
- ✅ **Fallback mechanism** - if ngrok is unavailable, regular URLs are used
- ✅ **Ease of use** - single method to get current URL
- ✅ **Flexibility** - works with both active manager and environment variables
- ✅ **Safety** - graceful fallback on errors

## 🔧 Debugging

To check environment variables:

```python
import os

env_vars = ['NGROK_URL', 'DJANGO_NGROK_URL', 'NGROK_HOST', 'NGROK_SCHEME']
for var in env_vars:
    print(f"{var}: {os.environ.get(var, 'Not set')}")
```

To check ngrok availability:

```python
from django_cfg.modules.django_ngrok import is_ngrok_available_from_env

if is_ngrok_available_from_env():
    print("✅ Ngrok is available from environment variables")
else:
    print("❌ Ngrok is not available, run runserver_ngrok")
```
