"""
OTP admin configuration.
"""

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin

from ..models import OTPSecret
from .filters import OTPStatusFilter
from .twilio_response import TwilioResponseInline


@admin.register(OTPSecret)
class OTPSecretAdmin(ModelAdmin):
    list_display = ["recipient", "channel_type", "secret", "status", "twilio_responses_count", "created", "expires"]
    list_display_links = ["recipient", "secret"]
    list_filter = [OTPStatusFilter, "channel_type", "is_used", "created_at"]
    search_fields = ["recipient", "secret"]
    readonly_fields = ["created_at", "expires_at"]
    ordering = ["-created_at"]
    inlines = [TwilioResponseInline]

    fieldsets = (
        (
            "OTP Details",
            {
                "fields": ("channel_type", "recipient", "secret", "is_used"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "expires_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def status(self, obj):
        """Simple OTP status."""
        if obj.is_used:
            return "Used"
        elif obj.is_valid:
            return "✅ Valid"
        else:
            return "⏰ Expired"

    status.short_description = "Status"

    def created(self, obj):
        """Created time with natural time."""
        return naturaltime(obj.created_at)

    created.short_description = "Created"

    def expires(self, obj):
        """Expires time with natural time."""
        return naturaltime(obj.expires_at)

    expires.short_description = "Expires"

    def twilio_responses_count(self, obj):
        """Count of related Twilio responses."""
        count = obj.twilio_responses.count()
        if count == 0:
            return "—"
        return f"{count} response{'s' if count != 1 else ''}"

    twilio_responses_count.short_description = "Twilio"
