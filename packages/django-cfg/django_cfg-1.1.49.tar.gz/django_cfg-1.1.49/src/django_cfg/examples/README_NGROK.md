# 🌐 Ngrok Integration Quick Start

Simple ngrok integration for django-cfg following KISS principle.

## 🚀 Installation

```bash
# Install django-cfg with ngrok support
pip install django-cfg[ngrok]

# Or install ngrok separately
pip install django-cfg ngrok
```

## ⚡ Quick Setup

### 1. Basic Configuration

```python
# config.py
from django_cfg import DjangoConfig, NgrokConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    secret_key: str = "your-secret-key"
    debug: bool = True
    
    # Enable ngrok
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True
    )

config = MyConfig()
```

### 2. Environment Setup

```bash
# .env (optional - for advanced features)
NGROK_AUTHTOKEN=your-ngrok-authtoken
```

### 3. Run Server with Ngrok

```bash
# Start Django server with ngrok tunnel
python manage.py runserver_ngrok

# Output:
# Starting development server at http://127.0.0.1:8000/
# ngrok forwarding to http://127.0.0.1:8000 from ingress url: https://abc123.ngrok-free.app
```

## 🔧 Advanced Configuration

```python
from django_cfg import DjangoConfig, NgrokConfig, NgrokAuthConfig, NgrokTunnelConfig

class AdvancedConfig(DjangoConfig):
    project_name: str = "Advanced Project"
    
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True,
        auto_start=True,
        webhook_path="/api/webhooks/",
        
        auth=NgrokAuthConfig(
            authtoken_from_env=True
        ),
        
        tunnel=NgrokTunnelConfig(
            domain="myapp.ngrok.io",  # Custom domain (paid plan)
            schemes=["https"],        # HTTPS only
            basic_auth=["admin:secret123"],
            compression=True
        )
    )
```

## 💳 Webhook Usage Example

```python
# services/payments.py
from django_cfg import get_webhook_url

class PaymentService:
    def create_payment(self, amount: float):
        # Get webhook URL (ngrok tunnel or fallback to site_url)
        webhook_url = get_webhook_url("/api/payments/webhook/")
        
        return {
            "amount": amount,
            "callback_url": webhook_url,
            # ... other payment data
        }

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def payment_webhook(request):
    """Handle payment webhook."""
    if request.method == "POST":
        # Process webhook data
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Method not allowed"}, status=405)
```

## 🛠️ Management Commands

```bash
# Run server with ngrok
python manage.py runserver_ngrok

# Run with custom domain
python manage.py runserver_ngrok --domain myapp.ngrok.io

# Run without ngrok (even if configured)
python manage.py runserver_ngrok --no-ngrok

# Regular runserver (no ngrok)
python manage.py runserver
```

## 🔍 Programmatic Usage

```python
from django_cfg import start_tunnel, get_tunnel_url, get_webhook_url, stop_tunnel

# Start tunnel manually
tunnel_url = start_tunnel(8000)
print(f"Tunnel: {tunnel_url}")

# Get current tunnel URL
current_url = get_tunnel_url()

# Get webhook URL (with tunnel or fallback)
webhook_url = get_webhook_url("/api/test/")

# Stop tunnel
stop_tunnel()
```

## 🔒 Security Notes

- **Development Only**: Ngrok only works when `DEBUG=True`
- **Auth Token**: Store in `NGROK_AUTHTOKEN` environment variable
- **Auto Cleanup**: Tunnels are automatically cleaned up on server shutdown
- **ALLOWED_HOSTS**: Automatically updated with ngrok domain

## 🐛 Troubleshooting

### Ngrok not starting
```bash
# Check if ngrok is installed
pip install ngrok

# Check auth token
echo $NGROK_AUTHTOKEN

# Check configuration
python -c "from config import config; print(config.ngrok)"
```

### Tunnel not accessible
- Verify `ALLOWED_HOSTS` includes ngrok domain
- Check firewall settings
- Ensure ngrok auth token is valid

### Webhook not receiving data
- Test tunnel URL directly in browser
- Check webhook endpoint is accessible locally
- Verify external service can reach ngrok URL

## 📚 More Examples

See `ngrok_example.py` for complete configuration examples.

## 🎯 Key Benefits

- **Zero Config**: Works out of the box
- **Type Safe**: Full Pydantic validation
- **Graceful Fallback**: Falls back to site_url if ngrok unavailable
- **KISS Principle**: Simple, focused implementation
- **Production Safe**: Only works in DEBUG mode
