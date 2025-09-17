"""
Test Twilio Command

Complete testing suite for Twilio functionality including:
- WhatsApp OTP testing
- SMS OTP testing  
- Email OTP testing (SendGrid)
- Template generation and testing
- Configuration validation
"""

import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Rich imports for beautiful output
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.align import Align
from rich.status import Status

# Django CFG imports
from django_cfg.core.config import get_current_config
from django_cfg.modules.django_twilio import (
    send_whatsapp_otp,
    send_sms_otp, 
    send_otp_email,
    send_sms,
    send_whatsapp
)


class Command(BaseCommand):
    """Command to test and setup Twilio functionality."""
    help = "Test Twilio messaging, OTP, and email functionality with template generation"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.config = None

    def add_arguments(self, parser):
        # Test modes
        parser.add_argument(
            "--mode",
            type=str,
            choices=["setup", "test-otp", "test-sms", "test-whatsapp", "test-email", "generate-templates", "show-guide", "all"],
            default="all",
            help="Test mode to run"
        )
        
        # Contact info
        parser.add_argument(
            "--phone",
            type=str,
            help="Phone number for testing (uses test_phone from config if not specified)",
            default=None
        )
        parser.add_argument(
            "--email",
            type=str,
            help="Email address for testing (uses admin_emails from config if not specified)",
            default=None
        )
        
        # Template generation
        parser.add_argument(
            "--generate",
            action="store_true",
            help="Generate email templates and test data"
        )
        
        # Interactive mode
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Run in interactive mode"
        )

    def handle(self, *args, **options):
        mode = options["mode"]
        phone = options["phone"]
        email = options["email"]
        interactive = options["interactive"]
        generate = options["generate"]

        # Show beautiful header
        self.show_header()

        # Load config
        self.load_config()

        # Get email from config if not provided
        if not email:
            email = self.get_admin_email()
            
        # Get phone from config if not provided
        if not phone:
            phone = self.get_test_phone()

        if interactive:
            mode = self.interactive_mode()

        # Execute selected mode
        if mode == "setup" or mode == "all":
            self.setup_mode()
        
        if mode == "generate-templates" or mode == "all":
            self.generate_templates()
            
        if mode == "show-guide":
            self.show_guide()
            
        if mode == "test-otp" or mode == "all":
            self.test_otp(phone, email)
            
        if mode == "test-sms" or mode == "all":
            self.test_sms(phone)
            
        if mode == "test-whatsapp" or mode == "all":
            self.test_whatsapp(phone)
            
        if mode == "test-email" or mode == "all":
            self.test_email(email)

        # Show completion message
        self.show_completion()

    def show_header(self):
        """Show beautiful header with Rich."""
        title = Text("Django CFG Twilio Test Suite", style="bold cyan")
        subtitle = Text("Complete testing for WhatsApp, SMS & Email OTP", style="dim")
        
        header_content = Align.center(
            Text.assemble(
                title, "\n",
                subtitle
            )
        )
        
        self.console.print()
        self.console.print(Panel(
            header_content,
            title="🚀 Test Suite",
            border_style="bright_blue",
            padding=(1, 2)
        ))

    def load_config(self):
        """Load Django CFG configuration."""
        try:
            self.config = get_current_config()
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load config: {e}[/red]")
            self.config = None

    def get_admin_email(self):
        """Get admin email from config with Rich formatting."""
        if self.config and self.config.admin_emails:
            email = self.config.admin_emails[0]
            self.console.print(f"[green]📧 Using admin email from config:[/green] [cyan]{email}[/cyan]")
            return email
        else:
            email = "admin@example.com"
            self.console.print(f"[yellow]⚠️  No admin emails in config, using default:[/yellow] [dim]{email}[/dim]")
            return email
    
    def get_test_phone(self):
        """Get test phone from config with Rich formatting."""
        if self.config and self.config.twilio and self.config.twilio.test_phone:
            phone = self.config.twilio.test_phone
            self.console.print(f"[green]📱 Using test phone from config:[/green] [cyan]{phone}[/cyan]")
            return phone
        else:
            phone = "+1234567890"
            self.console.print(f"[yellow]⚠️  No test_phone in config, using default:[/yellow] [dim]{phone}[/dim]")
            return phone

    def show_completion(self):
        """Show completion message with Rich."""
        self.console.print()
        completion_panel = Panel(
            Align.center(Text("All tests completed successfully! 🎉", style="bold green")),
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(completion_panel)

    def interactive_mode(self):
        """Interactive mode for selecting test options with Rich."""
        # Create options table
        table = Table(title="🔧 Interactive Test Mode", show_header=True, header_style="bold cyan")
        table.add_column("Option", style="cyan", width=6)
        table.add_column("Description", style="white")
        table.add_column("Features", style="dim")
        
        options = [
            ("1", "Setup & Configuration Check", "Validate Twilio & SendGrid config"),
            ("2", "Generate Email Templates", "Create rendered HTML templates"),
            ("3", "Test OTP (Multi-channel)", "WhatsApp + SMS + Email OTP"),
            ("4", "Test SMS only", "Direct SMS messaging"),
            ("5", "Test WhatsApp only", "Direct WhatsApp messaging"),
            ("6", "Test Email only", "Django email system"),
            ("7", "Show Setup Guide", "Display installation guide"),
            ("8", "Run all tests", "Complete test suite")
        ]
        
        for option, description, features in options:
            table.add_row(option, description, features)
        
        self.console.print()
        self.console.print(table)
        
        choice = Prompt.ask(
            "\n[cyan]Choose an option[/cyan]",
            choices=["1", "2", "3", "4", "5", "6", "7", "8"],
            default="8"
        )
        
        modes = {
            "1": "setup",
            "2": "generate-templates", 
            "3": "test-otp",
            "4": "test-sms",
            "5": "test-whatsapp",
            "6": "test-email",
            "7": "show-guide",
            "8": "all"
        }
        
        selected_mode = modes.get(choice, "all")
        self.console.print(f"[green]✓ Selected:[/green] {options[int(choice)-1][1]}")
        return selected_mode

    def setup_mode(self):
        """Check and display Twilio configuration with Rich table."""
        self.console.print()
        
        if not self.config:
            self.console.print("[red]❌ Django CFG config not found[/red]")
            return
            
        # Create configuration table
        config_table = Table(title="🔧 Configuration Status", show_header=True, header_style="bold cyan")
        config_table.add_column("Component", style="white", width=20)
        config_table.add_column("Status", width=8)
        config_table.add_column("Details", style="dim")
        
        # Check admin emails
        if self.config.admin_emails:
            config_table.add_row(
                "Admin Emails", 
                "[green]✅[/green]", 
                f"{len(self.config.admin_emails)} configured: {', '.join(self.config.admin_emails[:2])}"
            )
        else:
            config_table.add_row("Admin Emails", "[yellow]⚠️[/yellow]", "Not configured")
        
        # Check Twilio config
        if hasattr(self.config, 'twilio') and self.config.twilio:
            config_table.add_row(
                "Twilio Account", 
                "[green]✅[/green]", 
                f"SID: {self.config.twilio.account_sid[:8]}..."
            )
            
            if self.config.twilio.verify:
                config_table.add_row(
                    "Verify API", 
                    "[green]✅[/green]", 
                    f"Service: {self.config.twilio.verify.service_sid}, Channel: {self.config.twilio.verify.default_channel}"
                )
            else:
                config_table.add_row("Verify API", "[yellow]⚠️[/yellow]", "Not configured")
                
            if self.config.twilio.sendgrid:
                config_table.add_row(
                    "SendGrid", 
                    "[green]✅[/green]", 
                    f"From: {self.config.twilio.sendgrid.from_email}"
                )
            else:
                config_table.add_row("SendGrid", "[yellow]⚠️[/yellow]", "Not configured")
        else:
            config_table.add_row("Twilio Account", "[red]❌[/red]", "Missing configuration")
            
        # Check email config
        if hasattr(self.config, 'email') and self.config.email:
            config_table.add_row(
                "Email Backend", 
                "[green]✅[/green]", 
                f"Host: {self.config.email.host}:{self.config.email.port}"
            )
        else:
            config_table.add_row("Email Backend", "[yellow]⚠️[/yellow]", "Not configured")
            
        self.console.print(config_table)
        
        # Show webhook URLs
        self.show_webhook_urls()

    def show_webhook_urls(self):
        """Display webhook URLs for Twilio configuration using reverse."""
        self.console.print()
        
        # Create webhook table
        webhook_table = Table(title="🔔 Webhook URLs for Twilio", show_header=True, header_style="bold yellow")
        webhook_table.add_column("Webhook Type", style="white", width=20)
        webhook_table.add_column("Local URL", style="cyan", width=45)
        webhook_table.add_column("Ngrok URL", style="magenta", width=45)
        
        # Get base URLs
        base_url = self.config.api_url if self.config else "http://localhost:8000"
        ngrok_url = self.config.get_ngrok_url() if self.config else None
        
        # Get webhook URLs using reverse
        try:
            from django.urls import reverse
            
            # Define webhook endpoints with their URL names
            webhooks = [
                ("Message Status", "cfg_accounts:webhook-message-status"),
                ("Verification Status", "cfg_accounts:webhook-verification-status"),
            ]
            
            for webhook_type, url_name in webhooks:
                try:
                    # Get the reversed URL path
                    url_path = reverse(url_name)
                    
                    # Build full URLs
                    local_full = f"{base_url.rstrip('/')}{url_path}"
                    ngrok_full = f"{ngrok_url.rstrip('/')}{url_path}" if ngrok_url else "[dim]Not available[/dim]"
                    
                    webhook_table.add_row(webhook_type, local_full, ngrok_full)
                    
                except Exception as e:
                    # Fallback if reverse fails
                    self.console.print(f"[yellow]⚠️  Could not reverse URL for {webhook_type}: {e}[/yellow]")
                    fallback_path = f"/apix/accounts/webhook/{webhook_type.lower().replace(' ', '-')}/"
                    local_full = f"{base_url.rstrip('/')}{fallback_path}"
                    ngrok_full = f"{ngrok_url.rstrip('/')}{fallback_path}" if ngrok_url else "[dim]Not available[/dim]"
                    webhook_table.add_row(webhook_type, local_full, ngrok_full)
            
        except ImportError:
            # Fallback if Django is not available
            webhooks = [
                ("Message Status", "/apix/accounts/webhook/message-status/"),
                ("Verification Status", "/apix/accounts/webhook/verification-status/"),
            ]
            
            for webhook_type, endpoint in webhooks:
                local_full = f"{base_url.rstrip('/')}{endpoint}"
                ngrok_full = f"{ngrok_url.rstrip('/')}{endpoint}" if ngrok_url else "[dim]Not available[/dim]"
                webhook_table.add_row(webhook_type, local_full, ngrok_full)
        
        self.console.print(webhook_table)
        
        # Show instructions
        instructions = [
            "[cyan]💡 Instructions:[/cyan]",
            "1. Use ngrok URLs for webhook configuration in Twilio Console",
            "2. Copy the ngrok URL and paste it in your Twilio service settings",
            "3. Test webhooks using the URLs above",
            "",
            "[yellow]⚠️  Note:[/yellow] Ngrok URLs change on restart - update Twilio config accordingly"
        ]
        
        for instruction in instructions:
            self.console.print(f"   {instruction}")

    def generate_templates(self):
        """Show email template preview with test data."""
        self.console.print()
        
        try:
            # Get template paths
            template_dir = Path(__file__).parent.parent.parent / "modules" / "django_twilio" / "templates"
            accounts_template_path = Path(__file__).parent.parent.parent / "apps" / "accounts" / "templates" / "emails" / "otp_email.html"
            sendgrid_template_path = template_dir / "sendgrid_otp_email.html"
            sendgrid_json_path = template_dir / "sendgrid_test_data.json"
            
            # Load SendGrid test data
            if sendgrid_json_path.exists():
                with open(sendgrid_json_path, 'r') as f:
                    test_data = json.load(f)
                self.console.print(f"[green]✅ SendGrid test data loaded:[/green] [dim]{sendgrid_json_path}[/dim]")
            else:
                self.console.print(f"[red]❌ SendGrid test data not found:[/red] [dim]{sendgrid_json_path}[/dim]")
                return
            
            # Check if templates exist
            if accounts_template_path.exists():
                self.console.print(f"[green]✅ Django OTP template found:[/green] [dim]{accounts_template_path}[/dim]")
            else:
                self.console.print(f"[red]❌ Django template not found:[/red] [dim]{accounts_template_path}[/dim]")
            
            if sendgrid_template_path.exists():
                self.console.print(f"[green]✅ SendGrid OTP template found:[/green] [dim]{sendgrid_template_path}[/dim]")
            else:
                self.console.print(f"[red]❌ SendGrid template not found:[/red] [dim]{sendgrid_template_path}[/dim]")
            
            # Create summary table
            summary_table = Table(title="📧 Email Template Preview", show_header=True, header_style="bold cyan")
            summary_table.add_column("Component", style="white")
            summary_table.add_column("Value", style="cyan")
            
            # Show test data in table format
            summary_table.add_row("Site Name", str(test_data.get('site_name', 'N/A')))
            summary_table.add_row("User Name", str(test_data.get('user', {}).get('get_full_name', 'N/A')))
            summary_table.add_row("OTP Code", str(test_data.get('otp_code', 'N/A')))
            summary_table.add_row("OTP Link", str(test_data.get('otp_link', 'N/A')))
            summary_table.add_row("Expires (min)", str(test_data.get('expires_minutes', 'N/A')))
            
            self.console.print(summary_table)
            
            # Show usage instructions
            instructions = [
                "[cyan]💡 Template Usage:[/cyan]",
                "1. Django template: src/django_cfg/apps/accounts/templates/emails/otp_email.html (uses Django syntax)",
                "2. SendGrid template: src/django_cfg/modules/django_twilio/templates/sendgrid_otp_email.html (uses Handlebars syntax)",
                "3. SendGrid test data: sendgrid_test_data.json (structure for SendGrid Dynamic Templates)",
                "",
                "[yellow]⚠️  SendGrid Setup:[/yellow]",
                "- Upload sendgrid_otp_email.html to SendGrid Dynamic Templates",
                "- Use sendgrid_test_data.json for testing in SendGrid interface",
                "- Variables use {{variable}} syntax (Handlebars) instead of {{ variable }} (Django)",
                "- Conditions use {{#if variable}} instead of {% if variable %}"
            ]
            
            for instruction in instructions:
                self.console.print(f"   {instruction}")
                
        except Exception as e:
            self.console.print(f"[red]❌ Template preview failed: {e}[/red]")

    def show_guide(self):
        """Show setup guide from guide.md with Rich Markdown."""
        self.console.print()
        
        try:
            # Get guide path
            guide_path = Path(__file__).parent.parent.parent / "modules" / "django_twilio" / "templates" / "guide.md"
            
            if guide_path.exists():
                with open(guide_path, 'r') as f:
                    guide_content = f.read()
                
                # Show first part of the guide (first 50 lines for overview)
                lines = guide_content.split('\n')
                preview_content = '\n'.join(lines[:50])
                
                # Create markdown panel
                markdown_panel = Panel(
                    Markdown(preview_content),
                    title="📚 Django CFG Twilio Setup Guide",
                    border_style="cyan",
                    padding=(1, 2)
                )
                
                self.console.print(markdown_panel)
                
                # Show file info
                info_table = Table(show_header=False, box=None)
                info_table.add_column("Info", style="cyan")
                info_table.add_column("Value", style="white")
                
                info_table.add_row("📄 Full guide:", str(guide_path))
                info_table.add_row("📊 Total lines:", str(len(lines)))
                info_table.add_row("💡 Tip:", "Open in your editor for complete setup instructions")
                
                self.console.print()
                self.console.print(info_table)
                
            else:
                self.console.print(f"[red]❌ Guide not found at:[/red] [dim]{guide_path}[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load guide: {e}[/red]")


    def test_otp(self, phone, email):
        """Test OTP functionality with Rich interface."""
        self.console.print()
        
        # Create results table
        results_table = Table(title="🔐 OTP Testing Results", show_header=True, header_style="bold cyan")
        results_table.add_column("Channel", style="white", width=12)
        results_table.add_column("Target", style="cyan", width=25)
        results_table.add_column("Status", width=8)
        results_table.add_column("Details", style="dim")
        
        # Test WhatsApp OTP
        with Status(f"[cyan]Testing WhatsApp OTP to {phone}...", console=self.console):
            try:
                success, message = send_whatsapp_otp(phone)
                if success:
                    results_table.add_row("WhatsApp", phone, "[green]✅[/green]", message)
                else:
                    results_table.add_row("WhatsApp", phone, "[red]❌[/red]", message)
            except Exception as e:
                results_table.add_row("WhatsApp", phone, "[red]❌[/red]", str(e))
        
        # Test Email OTP  
        with Status(f"[cyan]Testing Email OTP to {email}...", console=self.console):
            try:
                success, message, otp_code = send_otp_email(email)
                if success:
                    results_table.add_row("Email", email, "[green]✅[/green]", f"Code: {otp_code}")
                else:
                    results_table.add_row("Email", email, "[red]❌[/red]", message)
            except Exception as e:
                results_table.add_row("Email", email, "[yellow]⚠️[/yellow]", f"Not available: {str(e)[:50]}")
        
        self.console.print(results_table)

    def test_sms(self, phone):
        """Test SMS functionality with Rich interface."""
        self.console.print()
        
        with Status(f"[cyan]Sending SMS to {phone}...", console=self.console) as status:
            try:
                result = send_sms(phone, "Test SMS from Django CFG Twilio")
                
                # Create result panel
                result_content = Text.assemble(
                    ("✅ SMS sent successfully\n", "green"),
                    (f"SID: {result['sid']}\n", "dim"),
                    (f"Status: {result['status']}", "dim")
                )
                
                panel = Panel(
                    result_content,
                    title=f"📱 SMS Test to {phone}",
                    border_style="green"
                )
                self.console.print(panel)
                
            except Exception as e:
                error_panel = Panel(
                    f"❌ SMS test failed: {e}",
                    title=f"📱 SMS Test to {phone}",
                    border_style="red"
                )
                self.console.print(error_panel)

    def test_whatsapp(self, phone):
        """Test WhatsApp functionality with Rich interface."""
        self.console.print()
        
        with Status(f"[cyan]Sending WhatsApp to {phone}...", console=self.console) as status:
            try:
                result = send_whatsapp(phone, "Test WhatsApp from Django CFG Twilio")
                
                # Create result panel
                result_content = Text.assemble(
                    ("✅ WhatsApp sent successfully\n", "green"),
                    (f"SID: {result['sid']}\n", "dim"),
                    (f"Status: {result['status']}", "dim")
                )
                
                panel = Panel(
                    result_content,
                    title=f"💬 WhatsApp Test to {phone}",
                    border_style="green"
                )
                self.console.print(panel)
                
            except Exception as e:
                error_panel = Panel(
                    f"❌ WhatsApp test failed: {e}",
                    title=f"💬 WhatsApp Test to {phone}",
                    border_style="red"
                )
                self.console.print(error_panel)

    def test_email(self, email):
        """Test email functionality with Rich interface."""
        self.console.print()
        
        with Status(f"[cyan]Sending email to {email}...", console=self.console) as status:
            try:
                send_mail(
                    "Test Email from Django CFG",
                    "This is a test email from Django CFG Twilio integration.",
                    "noreply@example.com",
                    [email],
                    fail_silently=False,
                )
                
                success_panel = Panel(
                    "✅ Email sent successfully",
                    title=f"📧 Email Test to {email}",
                    border_style="green"
                )
                self.console.print(success_panel)
                
            except Exception as e:
                error_panel = Panel(
                    f"❌ Email test failed: {e}",
                    title=f"📧 Email Test to {email}",
                    border_style="red"
                )
                self.console.print(error_panel)