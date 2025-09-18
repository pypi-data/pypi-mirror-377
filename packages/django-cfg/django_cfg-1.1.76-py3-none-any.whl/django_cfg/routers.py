"""
Database Router for Django Config Toolkit

Simple and reliable database routing.
"""

from django.conf import settings
from django.apps import apps


class DatabaseRouter:
    """
    Simple database router that routes based on app labels.
    
    Uses DATABASE_ROUTING_RULES setting to determine which apps
    should use which databases.
    """
    
    def _get_database_for_app(self, app_label):
        """
        Get database for app_label, trying multiple approaches.
        
        1. Direct app_label lookup
        2. Find full app path and lookup
        """
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        
        # Try direct app_label first
        if app_label in rules:
            return rules[app_label]
        
        # Try to find full app path using Django's app registry
        try:
            app_config = apps.get_app_config(app_label)
            app_module = app_config.module.__name__
            
            # Check if full module path is in rules
            if app_module in rules:
                return rules[app_module]
                
        except LookupError:
            pass
        
        return None

    def db_for_read(self, model, **hints):
        """Route reads to correct database."""
        return self._get_database_for_app(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """Route writes to correct database.""" 
        return self._get_database_for_app(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between databases."""
        app_label1 = obj1._meta.app_label
        app_label2 = obj2._meta.app_label
        
        db1 = self._get_database_for_app(app_label1)
        db2 = self._get_database_for_app(app_label2)
        
        # Allow relations if both are in same database
        if db1 and db2:
            return db1 == db2
        
        # Allow relations between routed apps and default database
        # (e.g., User from default can relate to Document from knowbase)
        if (db1 and not db2) or (db2 and not db1):
            return True
            
        # Allow all other relations (both in default)
        return True

    def allow_migrate(self, db, app_label, **hints):
        """Allow migrations to correct database."""
        target_db = self._get_database_for_app(app_label)

        if target_db:
            # This app IS configured in the rules
            return db == target_db
        else:
            # This app is NOT configured, allow migration to default only
            return db == 'default'
