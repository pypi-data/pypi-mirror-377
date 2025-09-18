"""
Smart Migration Command for Django Config Toolkit
Simple and reliable migration for all databases.
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder
from django.conf import settings
import questionary
from datetime import datetime
from django_cfg.core.config import DEFAULT_APPS


class Command(BaseCommand):
    help = "Smart migration command with interactive menu for multiple databases"

    def add_arguments(self, parser):
        parser.add_argument("--auto", action="store_true", help="Run automatic migration without prompts")
        parser.add_argument("--database", type=str, help="Migrate specific database only")
        parser.add_argument("--app", type=str, help="Migrate specific app only")

    def handle(self, *args, **options):
        if options["auto"]:
            self.run_automatic_migration()
        elif options["database"]:
            self.migrate_database(options["database"])
        elif options["app"]:
            self.migrate_app(options["app"])
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with options"""
        self.stdout.write(self.style.SUCCESS("\n🚀 Smart Migration Tool - Django Config Toolkit\n"))

        databases = self.get_all_database_names()

        choices = [
            questionary.Choice("🔄 Run Full Migration (All Databases)", value="full"),
            questionary.Choice("📝 Create Migrations Only", value="makemigrations"),
            questionary.Choice("🔍 Show Database Status", value="status"),
            questionary.Choice("⚙️  Show Django Config Info", value="config"),
            questionary.Choice("❌ Exit", value="exit"),
        ]

        # Add individual database options
        for db_name in databases:
            display_name = f"📊 Migrate {db_name.title()} Database Only"
            choices.insert(-1, questionary.Choice(display_name, value=f"migrate_{db_name}"))

        choice = questionary.select("Select an option:", choices=choices).ask()

        if choice == "full":
            self.run_full_migration()
        elif choice == "makemigrations":
            self.create_migrations()
        elif choice == "status":
            self.show_database_status()
        elif choice == "config":
            self.show_config_info()
        elif choice == "exit":
            self.stdout.write("Goodbye! 👋")
            return
        elif choice.startswith("migrate_"):
            db_name = choice.replace("migrate_", "")
            self.migrate_database(db_name)

    def run_full_migration(self):
        """Run migration for all databases"""
        self.stdout.write(self.style.SUCCESS("🔄 Starting full migration..."))

        # First migrate default database
        self.stdout.write("📊 Migrating default database...")
        self.migrate_database("default")

        # Then migrate other databases (excluding default)
        databases = self.get_all_database_names()
        for db_name in databases:
            if db_name != "default":
                self.stdout.write(f"🔄 Migrating {db_name}...")
                self.migrate_database(db_name)

        self.stdout.write(self.style.SUCCESS("✅ Full migration completed!"))

    def run_automatic_migration(self):
        """Run automatic migration for all databases"""
        self.stdout.write(self.style.SUCCESS("🚀 Running automatic migration..."))

        # Create migrations
        self.create_migrations()

        # Run full migration
        self.run_full_migration()
        
        # Always migrate constance (required for django-cfg)
        self.migrate_constance_if_needed()

    def create_migrations(self):
        """Create migrations for all apps"""
        self.stdout.write(self.style.SUCCESS("📝 Creating migrations..."))

        try:
            # First try global makemigrations
            call_command("makemigrations", verbosity=1)
            
            # Then try for each app that has models but no migrations
            all_apps = self.get_all_installed_apps()
            for app in all_apps:
                if self.app_has_models(app) and not self.app_has_migrations(app):
                    try:
                        self.stdout.write(f"  📝 Creating migrations for {app}...")
                        call_command("makemigrations", app, verbosity=1)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠️  Could not create migrations for {app}: {e}"))
            
            self.stdout.write(self.style.SUCCESS("✅ Migrations created"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Warning creating migrations: {e}"))

    def migrate_database(self, db_name):
        """Migrate specific database"""
        try:
            self.stdout.write(f"🔄 Migrating {db_name}...")

            # Get apps for this database
            apps = self.get_apps_for_database(db_name)

            # Debug info
            self.stdout.write(f"  📋 Apps for {db_name}: {apps}")

            if not apps:
                self.stdout.write(self.style.WARNING(f"  ⚠️  No apps configured for {db_name}"))
                return

            # make migrations for all apps
            self.create_migrations()

            # Migrate each app
            for app in apps:
                try:
                    # Convert full module path to app_label if needed
                    app_label = self.get_app_label_from_path(app)
                    
                    # Skip apps without migrations
                    if not self.app_has_migrations(app_label):
                        # self.stdout.write(f"  ⚠️  Skipping {app_label} - no migrations")
                        continue

                    self.stdout.write(f"  📦 Migrating {app_label}...")
                    call_command("migrate", app_label, database=db_name, verbosity=1)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Warning migrating {app}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"✅ {db_name} migration completed!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error migrating {db_name}: {e}"))

    def migrate_constance_if_needed(self):
        """Always migrate constance app if it's installed"""
        try:
            # Check if constance is in INSTALLED_APPS
            if 'constance' in settings.INSTALLED_APPS:
                self.stdout.write(self.style.SUCCESS("🔧 Migrating constance (django-cfg requirement)..."))
                
                # Try to migrate constance on default database
                try:
                    call_command("migrate", "constance", database="default", verbosity=1)
                    self.stdout.write(self.style.SUCCESS("✅ Constance migration completed!"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️  Constance migration warning: {e}"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  Constance not found in INSTALLED_APPS"))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Could not migrate constance: {e}"))

    def migrate_app(self, app_name):
        """Migrate specific app across all databases"""
        self.stdout.write(f"🔄 Migrating app {app_name}...")

        databases = self.get_all_database_names()
        for db_name in databases:
            apps = self.get_apps_for_database(db_name)
            if app_name in apps:
                # Convert full module path to app_label if needed
                app_label = self.get_app_label_from_path(app_name)
                self.stdout.write(f"  📊 Migrating {app_label} on {db_name}...")
                try:
                    call_command("migrate", app_label, database=db_name, verbosity=1)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Warning: {e}"))

    def show_database_status(self):
        """Show status of all databases and their apps"""
        self.stdout.write(self.style.SUCCESS("\n📊 Database Status Report\n"))

        # Get database info from Django settings
        db_info = self.get_database_info()
        databases = self.get_all_database_names()

        for db_name in databases:
            self.stdout.write(f"\n🗄️  Database: {db_name}")

            # Show database info from Django settings
            if db_name in db_info:
                info = db_info[db_name]
                self.stdout.write(f'  🔧 Engine: {info["engine"]}')
                self.stdout.write(f'  🔗 Name: {info["name"]}')

            # Test connection
            try:
                with connections[db_name].cursor() as cursor:
                    cursor.execute("SELECT 1")
                self.stdout.write(f"  ✅ Connection: OK")
            except Exception as e:
                self.stdout.write(f"  ❌ Connection: FAILED - {e}")

            # Show apps
            apps = self.get_apps_for_database(db_name)
            if apps:
                self.stdout.write(f'  📦 Apps: {", ".join(apps)}')
            else:
                self.stdout.write(f"  📦 Apps: None configured")

    def show_config_info(self):
        """Show Django configuration information"""
        self.stdout.write(self.style.SUCCESS("\n⚙️  Django Configuration Information\n"))

        try:
            # Environment info
            self.stdout.write(f'🌍 Environment: {getattr(settings, "ENVIRONMENT", "unknown")}')
            self.stdout.write(f"🔧 Debug: {settings.DEBUG}")

            # Database info
            databases = settings.DATABASES
            self.stdout.write(f"🗄️ Databases: {len(databases)}")

            for db_name, db_config in databases.items():
                engine = db_config.get("ENGINE", "unknown")
                name = db_config.get("NAME", "unknown")
                self.stdout.write(f"  📊 {db_name}: {engine} -> {name}")

            # Multiple databases
            if len(databases) > 1:
                self.stdout.write(f"📊 Multiple Databases: Yes")

                # Show routing rules
                routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
                if routing_rules:
                    self.stdout.write(f"  🔀 Routing Rules:")
                    for app, db in routing_rules.items():
                        self.stdout.write(f"    - {app} → {db}")
                else:
                    self.stdout.write(f"  🔀 Routing Rules: None configured")
            else:
                self.stdout.write(f"📊 Multiple Databases: No")

            # Other settings
            self.stdout.write(f'🔑 Secret Key: {"*" * 20}...')
            self.stdout.write(f"🌐 Allowed Hosts: {settings.ALLOWED_HOSTS}")
            self.stdout.write(f"📦 Installed Apps: {len(settings.INSTALLED_APPS)}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error getting Django config info: {e}"))

    def get_apps_for_database(self, db_name: str):
        """Get apps for specific database using Django-CFG configuration"""
        try:
            # Try to get Django-CFG config
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            
            if config and hasattr(config, 'databases'):
                if db_name in config.databases:
                    db_config = config.databases[db_name]
                    if hasattr(db_config, 'apps') and db_config.apps:
                        return db_config.apps
                        
                # For default database, get all apps not in other databases
                if db_name == "default":
                    all_apps = self.get_all_installed_apps()
                    apps_in_other_dbs = set()
                    
                    # Collect apps from all non-default databases
                    for other_db_name, other_db_config in config.databases.items():
                        if other_db_name != "default" and hasattr(other_db_config, 'apps'):
                            # Convert full paths to app_labels for comparison
                            for app_path in other_db_config.apps:
                                app_label = self.get_app_label_from_path(app_path)
                                apps_in_other_dbs.add(app_label)
                    
                    return [app for app in all_apps if app not in apps_in_other_dbs]
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Could not get Django-CFG config: {e}"))
        
        # Fallback to old routing rules method
        routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
        if db_name == "default":
            all_apps = self.get_all_installed_apps()
            apps_in_other_dbs = set(routing_rules.keys())
            return [app for app in all_apps if app not in apps_in_other_dbs]
        else:
            return [app for app, db in routing_rules.items() if db == db_name]

    def get_all_installed_apps(self):
        """Get all installed Django apps by checking for apps.py files."""
        apps_list = []

        # Get all Django app configs
        for app_config in apps.get_app_configs():
            app_label = app_config.label
            app_path = Path(app_config.path)

            # Check if apps.py exists in the app directory
            apps_py_path = app_path / "apps.py"
            if apps_py_path.exists():
                if app_label not in DEFAULT_APPS:
                    apps_list.append(app_label)
                continue

            # Fallback: check if it's a standard Django app (has models.py or admin.py)
            if (app_path / "models.py").exists() or (app_path / "admin.py").exists():
                apps_list.append(app_label)

        return apps_list

    def get_apps_in_other_databases(self) -> set:
        """Get all apps that are configured for non-default databases."""
        try:
            # Try to get Django-CFG config
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            
            if config and hasattr(config, 'databases'):
                apps_in_other_dbs = set()
                
                # Collect apps from all non-default databases
                for db_name, db_config in config.databases.items():
                    if db_name != "default" and hasattr(db_config, 'apps'):
                        apps_in_other_dbs.update(db_config.apps)
                
                return apps_in_other_dbs
                
        except Exception:
            pass
        
        # Fallback to old routing rules method
        routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
        return set(routing_rules.keys())

    def get_all_database_names(self):
        """Get all database names."""
        return list(connections.databases.keys())

    def get_database_info(self):
        """Get database information from Django settings"""
        try:
            db_info = {}

            # Get database info from Django settings
            for db_name, db_config in settings.DATABASES.items():
                db_info[db_name] = {"name": db_config.get("NAME", "unknown"), "engine": db_config.get("ENGINE", "unknown"), "host": db_config.get("HOST", ""), "port": db_config.get("PORT", ""), "apps": []}  # Will be populated by routing logic

            return db_info

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Error getting database info: {e}"))
            return {}

    def app_has_migrations(self, app_label: str) -> bool:
        """Simple check if an app has migrations."""
        try:
            # Get the app config
            app_config = apps.get_app_config(app_label)
            if not app_config:
                return False

            # Check if migrations directory exists and has files
            migrations_dir = Path(app_config.path) / "migrations"
            if not migrations_dir.exists():
                return False

            # Check if there are any migration files (excluding __init__.py)
            migration_files = [f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"]

            # Also check if there are any applied migrations in the database
            # Check all databases for this app's migrations
            for db_name in connections.databases.keys():
                try:
                    recorder = MigrationRecorder(connections[db_name])
                    applied_migrations = recorder.migration_qs.filter(app=app_label)
                    if applied_migrations.exists():
                        return True
                except Exception:
                    continue

            # If no applied migrations found, check if there are migration files
            return len(migration_files) > 0

        except Exception:
            # Silently return False for apps that don't exist or have issues
            return False

    def app_has_models(self, app_label: str) -> bool:
        """Check if an app has models defined."""
        try:
            # Get the app config
            app_config = apps.get_app_config(app_label)
            if not app_config:
                return False

            # Check if models.py exists and has content
            models_file = Path(app_config.path) / "models.py"
            if models_file.exists():
                # Read the file and check if it has model definitions
                content = models_file.read_text()
                # Simple check for model definitions
                if "class " in content and "models.Model" in content:
                    return True

            # Also check if the app has any registered models
            models = app_config.get_models()
            return len(models) > 0

        except Exception:
            # Silently return False for apps that don't exist or have issues
            return False

    def get_app_label_from_path(self, app_path: str) -> str:
        """
        Convert full module path to Django app_label.
        
        Args:
            app_path: Full module path (e.g., 'apps.vehicles_data') or app_label (e.g., 'vehicles_data')
            
        Returns:
            Django app_label that can be used with migrate command
            
        Examples:
            'apps.vehicles_data' -> 'vehicles_data'
            'vehicles_data' -> 'vehicles_data'
            'myproject.apps.blog' -> 'blog'
        """
        try:
            # Try to get app config by full path first
            try:
                app_config = apps.get_app_config(app_path)
                return app_config.label
            except LookupError:
                pass
            
            # Fallback: extract last part of the path as potential app_label
            potential_label = app_path.split('.')[-1]
            try:
                app_config = apps.get_app_config(potential_label)
                return app_config.label
            except LookupError:
                pass
                
            # If all fails, return original path
            return app_path
            
        except Exception:
            # Fallback to original path
            return app_path
