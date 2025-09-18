"""
Base Module for Django CFG

Provides base functionality for all auto-configuring modules.
"""

from typing import Any, Optional
from abc import ABC


class BaseModule(ABC):
    """
    Base class for all django_cfg modules.
    
    Provides common functionality and configuration access.
    """
    
    def __init__(self):
        """Initialize the base module."""
        self._config = None
    
    def get_config(self) -> Optional[Any]:
        """
        Get the current Django configuration instance.
        
        Returns:
            The current DjangoConfig instance or None
        """
        if self._config is None:
            try:
                # Try to get config from the current context first
                from django_cfg.core.config import get_current_config
                self._config = get_current_config()
                
                # If that fails, try to import directly from Django settings
                if self._config is None:
                    try:
                        from django.conf import settings
                        if hasattr(settings, 'DJANGO_SETTINGS_MODULE'):
                            # Import the config module directly
                            import importlib
                            settings_module_name = settings.DJANGO_SETTINGS_MODULE
                            if settings_module_name:
                                # Get the config module (usually api.config)
                                config_module_name = settings_module_name.replace('.settings', '.config')
                                config_module = importlib.import_module(config_module_name)
                                if hasattr(config_module, 'config'):
                                    self._config = config_module.config
                    except Exception:
                        pass
                        
            except (ImportError, AttributeError):
                # Fallback - config might not be available yet
                pass
        
        return self._config
    
    def set_config(self, config: Any) -> None:
        """
        Set the configuration instance.
        
        Args:
            config: The DjangoConfig instance
        """
        self._config = config
    
    def _get_config_key(self, key: str, default: Any) -> bool:
        """
        Get a key from the configuration instance.
        
        Args:
            key: The key to get
            default: The default value to return if the key is not found
        """
        try:
            # Try to get config if not already set
            if self._config is None:
                self._config = self.get_config()
            
            # If config is available, get the key
            if self._config is not None:
                result = getattr(self._config, key, default)
                return bool(result)
            
            # Fallback to default if no config available
            return bool(default)
            
        except Exception:
            # Return default on any error
            return bool(default)

    def is_support_enabled(self) -> bool:
        """
        Check if django-cfg Support is enabled.
        
        Returns:
            True if Support is enabled, False otherwise
        """
        return self._get_config_key('enable_support', True)
    
    def is_accounts_enabled(self) -> bool:
        """
        Check if django-cfg Accounts is enabled.
        
        Returns:
            True if Accounts is enabled, False otherwise
        """
        return self._get_config_key('enable_accounts', False)
    
    def is_newsletter_enabled(self) -> bool:
        """
        Check if django-cfg Newsletter is enabled.
        
        Returns:
            True if Newsletter is enabled, False otherwise
        """
        return self._get_config_key('enable_newsletter', False)
    
    def is_leads_enabled(self) -> bool:
        """
        Check if django-cfg Leads is enabled.
        
        Returns:
            True if Leads is enabled, False otherwise
        """
        return self._get_config_key('enable_leads', False)
    
    def is_tasks_enabled(self) -> bool:
        """
        Check if django-cfg Tasks (Dramatiq) is enabled.
        
        Returns:
            True if Tasks is enabled, False otherwise
        """
        try:
            config = self.get_config()
            if config is not None and hasattr(config, 'tasks'):
                tasks_config = getattr(config, 'tasks', None)
                if tasks_config is not None:
                    return getattr(tasks_config, 'enabled', False)
            return False
        except Exception:
            return False


# Export the base class
__all__ = [
    "BaseModule",
]
