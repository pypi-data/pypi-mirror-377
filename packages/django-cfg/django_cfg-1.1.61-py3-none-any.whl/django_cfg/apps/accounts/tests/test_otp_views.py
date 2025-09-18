"""
Tests for OTP views with controlled welcome email notifications.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from ..models import OTPSecret
from ..utils.notifications import AccountNotifications

User = get_user_model()


class OTPViewWelcomeEmailTestCase(TestCase):
    """Test cases for controlled welcome email in OTP views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.email = "test@example.com"
        self.otp_code = "123456"

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_welcome_email")
    def test_welcome_email_sent_for_new_user(self, mock_welcome_email):
        """Test that welcome email is sent only for new users during OTP verification."""
        # Create a new user (simulating recent registration)
        user = User.objects.create_user(email=self.email, username="newuser")
        
        # Create OTP for the user
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = self.otp_code
        otp.save()
        
        # Mock the OTP verification to return the new user
        with patch("django_cfg.apps.accounts.services.otp_service.OTPService.verify_email_otp") as mock_verify:
            mock_verify.return_value = user
            
            # Make OTP verification request
            response = self.client.post(
                reverse("cfg_accounts:otp-verify-otp"),
                data={
                    "identifier": self.email,
                    "otp": self.otp_code,
                },
                format="json"
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Welcome email should be sent for new user
            mock_welcome_email.assert_called_once_with(
                user, send_email=True, send_telegram=False
            )

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_welcome_email")
    def test_no_welcome_email_for_existing_user(self, mock_welcome_email):
        """Test that welcome email is NOT sent for existing users during OTP verification."""
        # Create an existing user (older than 5 minutes)
        old_time = timezone.now() - timedelta(minutes=10)
        user = User.objects.create_user(email=self.email, username="olduser")
        user.date_joined = old_time
        user.save()
        
        # Create OTP for the user
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = self.otp_code
        otp.save()
        
        # Mock the OTP verification to return the existing user
        with patch("django_cfg.apps.accounts.services.otp_service.OTPService.verify_email_otp") as mock_verify:
            mock_verify.return_value = user
            
            # Make OTP verification request
            response = self.client.post(
                reverse("cfg_accounts:otp-verify-otp"),
                data={
                    "identifier": self.email,
                    "otp": self.otp_code,
                },
                format="json"
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Welcome email should NOT be sent for existing user
            mock_welcome_email.assert_not_called()

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_welcome_email")
    def test_welcome_email_error_handling(self, mock_welcome_email):
        """Test that OTP verification succeeds even if welcome email fails."""
        # Create a new user
        user = User.objects.create_user(email=self.email, username="newuser")
        
        # Create OTP for the user
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = self.otp_code
        otp.save()
        
        # Mock welcome email to raise an exception
        mock_welcome_email.side_effect = Exception("Email service error")
        
        # Mock the OTP verification to return the new user
        with patch("django_cfg.apps.accounts.services.otp_service.OTPService.verify_email_otp") as mock_verify:
            mock_verify.return_value = user
            
            # Make OTP verification request
            response = self.client.post(
                reverse("cfg_accounts:otp-verify-otp"),
                data={
                    "identifier": self.email,
                    "otp": self.otp_code,
                },
                format="json"
            )
            
            # OTP verification should still succeed
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("access", response.data)
            self.assertIn("refresh", response.data)
            
            # Welcome email should have been attempted
            mock_welcome_email.assert_called_once()

    def test_integration_with_notifications_class(self):
        """Test integration with AccountNotifications class methods."""
        # Create a user
        user = User.objects.create_user(email=self.email, username="testuser")
        
        # Test that AccountNotifications methods exist and are callable
        self.assertTrue(hasattr(AccountNotifications, "send_welcome_email"))
        self.assertTrue(hasattr(AccountNotifications, "send_otp_notification"))
        self.assertTrue(hasattr(AccountNotifications, "send_otp_verification_success"))
        
        # Test that methods are static
        self.assertTrue(callable(AccountNotifications.send_welcome_email))
        self.assertTrue(callable(AccountNotifications.send_otp_notification))
        self.assertTrue(callable(AccountNotifications.send_otp_verification_success))
