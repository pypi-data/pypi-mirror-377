"""
Custom admin filters for Accounts app.
"""

from django.contrib import admin
from django.utils import timezone
from django.db import models
from datetime import timedelta


class UserStatusFilter(admin.SimpleListFilter):
    title = "User Status"
    parameter_name = "user_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("staff", "Staff"),
            ("superuser", "Superuser"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True, is_staff=False)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False)
        elif self.value() == "staff":
            return queryset.filter(is_staff=True)
        elif self.value() == "superuser":
            return queryset.filter(is_superuser=True)
        return queryset


class OTPStatusFilter(admin.SimpleListFilter):
    title = "OTP Status"
    parameter_name = "otp_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("used", "Used"),
            ("expired", "Expired"),
            ("recent", "Recent (24h)"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "active":
            return queryset.filter(is_used=False, expires_at__gt=now)
        elif self.value() == "used":
            return queryset.filter(is_used=True)
        elif self.value() == "expired":
            return queryset.filter(is_used=False, expires_at__lte=now)
        elif self.value() == "recent":
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        return queryset


class RegistrationSourceStatusFilter(admin.SimpleListFilter):
    title = "Registration Source Status"
    parameter_name = "registration_source_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("inactive", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False)
        return queryset


class ActivityTypeFilter(admin.SimpleListFilter):
    title = "Activity Type"
    parameter_name = "activity_type"

    def lookups(self, request, model_admin):
        return (
            ("login", "Login"),
            ("logout", "Logout"),
            ("otp_requested", "OTP Requested"),
            ("otp_verified", "OTP Verified"),
            ("profile_updated", "Profile Updated"),
            ("registration", "Registration"),
            ("recent", "Recent (24h)"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "recent":
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif self.value():
            return queryset.filter(activity_type=self.value())
        return queryset


class TwilioResponseStatusFilter(admin.SimpleListFilter):
    title = "Response Status"
    parameter_name = "twilio_status"

    def lookups(self, request, model_admin):
        return (
            ("successful", "Successful"),
            ("error", "Has Error"),
            ("recent", "Recent (24h)"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "successful":
            return queryset.filter(error_code__isnull=True, error_message__isnull=True)
        elif self.value() == "error":
            return queryset.filter(
                models.Q(error_code__isnull=False) | models.Q(error_message__isnull=False)
            )
        elif self.value() == "recent":
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        return queryset


class TwilioResponseTypeFilter(admin.SimpleListFilter):
    title = "Response Type"
    parameter_name = "twilio_response_type"

    def lookups(self, request, model_admin):
        return (
            ("sms", "SMS"),
            ("verification", "Verification"),
            ("call", "Call"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(response_type=self.value())
        return queryset
