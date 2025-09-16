"""
Example of using ngrok URL from environment variables in django-cfg.

This example shows how to get the current ngrok URL from environment variables
that are automatically set by the runserver_ngrok command.
"""

from django_cfg.core.config import DjangoConfig
from django_cfg.models.ngrok import NgrokConfig
from django_cfg.modules.django_ngrok import (
    get_tunnel_url_from_env,
    get_ngrok_host_from_env,
    is_ngrok_available_from_env,
    get_effective_tunnel_url
)


class MyProjectConfig(DjangoConfig):
    """Project configuration with ngrok support."""
    
    project_name: str = "My Project with Ngrok"
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    
    # Enable ngrok
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True,
        auto_start=True,
        update_api_url=True
    )


def demonstrate_ngrok_env_usage():
    """Demonstration of using ngrok URL from environment variables."""
    
    config = MyProjectConfig()
    
    print("=== Ngrok Environment Variables Demo ===")
    
    # 1. Check ngrok availability from environment variables
    if is_ngrok_available_from_env():
        print("✅ Ngrok URL is available from environment variables")
        
        # 2. Get base URL
        tunnel_url = get_tunnel_url_from_env()
        print(f"🌐 Tunnel URL: {tunnel_url}")
        
        # 3. Get host
        ngrok_host = get_ngrok_host_from_env()
        print(f"🏠 Ngrok Host: {ngrok_host}")
        
        # 4. Get effective URL (from manager or env)
        effective_url = get_effective_tunnel_url()
        print(f"🎯 Effective URL: {effective_url}")
        
        # 5. Use config method to get URL with path
        webhook_url = config.get_ngrok_url("/api/webhooks/nowpayments/")
        print(f"🔗 Webhook URL: {webhook_url}")
        
        # 6. Examples of different URLs
        api_url = config.get_ngrok_url("/api/")
        admin_url = config.get_ngrok_url("/admin/")
        health_url = config.get_ngrok_url("/health/")
        
        print(f"📡 API URL: {api_url}")
        print(f"⚙️  Admin URL: {admin_url}")
        print(f"💚 Health URL: {health_url}")
        
    else:
        print("❌ Ngrok URL is not available from environment variables")
        print("💡 Start server with: python manage.py runserver_ngrok")
    
    print("\n=== Environment Variables ===")
    import os
    env_vars = ['NGROK_URL', 'DJANGO_NGROK_URL', 'NGROK_HOST', 'NGROK_SCHEME', 'NGROK_API_URL']
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")


def webhook_handler_example():
    """Example usage in webhook handler."""
    
    config = MyProjectConfig()
    
    # Get current ngrok URL for webhook
    current_ngrok_url = config.get_ngrok_url()
    
    if current_ngrok_url:
        # Create callback URL
        callback_url = config.get_ngrok_url("/api/payments/webhooks/callback/")
        
        # Use in API request to external service
        webhook_data = {
            "callback_url": callback_url,
            "success_url": config.get_ngrok_url("/payment/success/"),
            "cancel_url": config.get_ngrok_url("/payment/cancel/"),
        }
        
        print("📦 Webhook Data:")
        for key, value in webhook_data.items():
            print(f"  {key}: {value}")
        
        return webhook_data
    else:
        print("⚠️  Ngrok URL is not available, using fallback URLs")
        return {
            "callback_url": config.get_site_url("/api/payments/webhooks/callback/"),
            "success_url": config.get_site_url("/payment/success/"),
            "cancel_url": config.get_site_url("/payment/cancel/"),
        }


def payment_service_example():
    """Example usage in payment service."""
    
    from django_cfg.modules.django_ngrok import get_webhook_url
    
    # Get webhook URL with automatic fallback
    webhook_url = get_webhook_url("/api/payments/webhooks/nowpayments/")
    
    print(f"💳 Payment Service Webhook URL: {webhook_url}")
    
    # Example payment data
    payment_data = {
        "amount": 100.0,
        "currency": "USD",
        "callback_url": webhook_url,
        "description": "Test payment"
    }
    
    return payment_data


if __name__ == "__main__":
    print("🚀 Django-CFG Ngrok Environment Variables Example")
    print("=" * 50)
    
    # Main demonstration
    demonstrate_ngrok_env_usage()
    
    print("\n" + "=" * 50)
    
    # Webhook handler example
    print("🔗 Webhook Handler Example:")
    webhook_handler_example()
    
    print("\n" + "=" * 50)
    
    # Payment service example
    print("💳 Payment Service Example:")
    payment_service_example()
    
    print("\n✨ Done! Now you can use ngrok URL from environment variables.")
