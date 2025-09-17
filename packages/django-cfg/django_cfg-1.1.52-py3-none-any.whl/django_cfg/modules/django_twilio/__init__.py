"""
Django Twilio Module for django_cfg.

Auto-configuring Twilio services for OTP and messaging via WhatsApp, Email, and SMS.
Supports both sync and async operations following Django 5.2+ patterns.

Features:
- WhatsApp OTP with SMS fallback
- Email OTP via SendGrid with templates
- SMS OTP via Twilio Verify API
- Unified OTP service with smart channel selection
- Full async/await support
- Type-safe configuration with Pydantic v2
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.modules.django_twilio.models import TwilioConfig
    from django_cfg.modules.django_twilio.service import (
        DjangoTwilioService,
        WhatsAppOTPService,
        EmailOTPService,
        SMSOTPService,
        UnifiedOTPService,
    )
    from django_cfg.modules.django_twilio.simple_service import SimpleTwilioService
    from django_cfg.modules.django_twilio.exceptions import (
        TwilioError,
        TwilioConfigurationError,
        TwilioVerificationError,
        TwilioSendError,
    )


def __getattr__(name: str):
    """Lazy import mechanism for Twilio module components."""
    
    # Configuration model
    if name == "TwilioConfig":
        from django_cfg.modules.django_twilio.models import TwilioConfig
        return TwilioConfig
    
    # New unified services
    elif name == "TwilioService":
        from django_cfg.modules.django_twilio.twilio_service import TwilioService
        return TwilioService
    
    elif name == "SendGridService":
        from django_cfg.modules.django_twilio.sendgrid_service import SendGridService
        return SendGridService
    
    # Legacy service aliases for backward compatibility
    elif name == "SimpleTwilioService":
        from django_cfg.modules.django_twilio.twilio_service import TwilioService
        return TwilioService
    
    elif name == "DjangoTwilioService":
        from django_cfg.modules.django_twilio.twilio_service import TwilioService
        return TwilioService
    
    # Exceptions
    elif name == "TwilioError":
        from django_cfg.modules.django_twilio.exceptions import TwilioError
        return TwilioError
    
    elif name == "TwilioConfigurationError":
        from django_cfg.modules.django_twilio.exceptions import TwilioConfigurationError
        return TwilioConfigurationError
    
    elif name == "TwilioVerificationError":
        from django_cfg.modules.django_twilio.exceptions import TwilioVerificationError
        return TwilioVerificationError
    
    elif name == "TwilioSendError":
        from django_cfg.modules.django_twilio.exceptions import TwilioSendError
        return TwilioSendError
    
    # Twilio convenience functions
    elif name == "send_whatsapp":
        from django_cfg.modules.django_twilio.twilio_service import send_whatsapp
        return send_whatsapp
    
    elif name == "send_sms":
        from django_cfg.modules.django_twilio.twilio_service import send_sms
        return send_sms
    
    elif name == "send_whatsapp_otp":
        from django_cfg.modules.django_twilio.twilio_service import send_whatsapp_otp
        return send_whatsapp_otp
    
    elif name == "send_whatsapp_otp_hybrid":
        from django_cfg.modules.django_twilio.twilio_service import send_whatsapp_otp_hybrid
        return send_whatsapp_otp_hybrid
    
    elif name == "send_sms_otp":
        from django_cfg.modules.django_twilio.twilio_service import send_sms_otp
        return send_sms_otp
    
    elif name == "verify_otp":
        from django_cfg.modules.django_twilio.twilio_service import verify_otp
        return verify_otp
    
    elif name == "get_message_status":
        from django_cfg.modules.django_twilio.twilio_service import get_message_status
        return get_message_status
    
    # SendGrid convenience functions
    elif name == "send_email":
        from django_cfg.modules.django_twilio.sendgrid_service import send_email
        return send_email
    
    elif name == "send_otp_email":
        from django_cfg.modules.django_twilio.sendgrid_service import send_otp_email
        return send_otp_email
    
    elif name == "verify_email_otp":
        from django_cfg.modules.django_twilio.sendgrid_service import verify_email_otp
        return verify_email_otp
    
    # Legacy aliases
    elif name == "send_email_otp":
        from django_cfg.modules.django_twilio.sendgrid_service import send_otp_email
        return send_otp_email
    
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Public API
__all__ = [
    # Configuration
    "TwilioConfig",
    
    # Services
    "DjangoTwilioService",
    "SimpleTwilioService",
    "WhatsAppOTPService", 
    "EmailOTPService",
    "SMSOTPService",
    "UnifiedOTPService",
    
    # Exceptions
    "TwilioError",
    "TwilioConfigurationError", 
    "TwilioVerificationError",
    "TwilioSendError",
    
    # OTP functions
    "send_whatsapp_otp",
    "send_whatsapp_otp_hybrid",
    "send_email_otp", 
    "send_sms_otp",
    "verify_otp",
    
    # Simple messaging functions
    "send_whatsapp",
    "send_sms",
]
