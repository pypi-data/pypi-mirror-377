"""
Simple example of ngrok integration with django-cfg.

This example shows how to configure and use ngrok tunnels
for webhook testing in development.
"""

from django_cfg import DjangoConfig, NgrokConfig, NgrokAuthConfig, NgrokTunnelConfig


# Basic ngrok configuration
class BasicConfig(DjangoConfig):
    """Basic configuration with ngrok enabled."""
    
    project_name: str = "My Project"
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    
    # Enable ngrok with minimal configuration
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True
    )


# Advanced ngrok configuration
class AdvancedConfig(DjangoConfig):
    """Advanced configuration with custom ngrok settings."""
    
    project_name: str = "Advanced Project"
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    
    # Advanced ngrok configuration
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True,
        auto_start=True,
        webhook_path="/api/webhooks/",
        
        auth=NgrokAuthConfig(
            authtoken_from_env=True  # Uses NGROK_AUTHTOKEN env var
        ),
        
        tunnel=NgrokTunnelConfig(
            domain="myapp.ngrok.io",  # Custom domain (requires paid plan)
            schemes=["https"],        # HTTPS only
            basic_auth=["admin:secret123"],
            compression=True
        )
    )


# Usage example
if __name__ == "__main__":
    # Create config
    config = BasicConfig()
    
    # Get Django settings
    settings = config.get_all_settings()
    
    print("Django settings generated with ngrok support!")
    print(f"Ngrok enabled: {config.ngrok.enabled}")
    
    # Example of using ngrok service
    from django_cfg import get_webhook_url, start_tunnel
    
    # Start tunnel (would normally be done by runserver_ngrok command)
    tunnel_url = start_tunnel(8000)
    if tunnel_url:
        print(f"Tunnel started: {tunnel_url}")
        
        # Get webhook URL
        webhook_url = get_webhook_url("/api/payments/webhook/")
        print(f"Webhook URL: {webhook_url}")
    else:
        print("Failed to start tunnel (ngrok not installed or configured)")
