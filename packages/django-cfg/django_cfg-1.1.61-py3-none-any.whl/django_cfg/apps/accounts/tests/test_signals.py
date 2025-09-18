"""
Tests for account signals and email notifications.
"""

import logging
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from django_cfg.apps.accounts.signals import trigger_login_notification
from django_cfg.apps.accounts.utils.notifications import AccountNotifications

User = get_user_model()


class AccountSignalsTestCase(TestCase):
    """Test cases for account signals."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }
    
    def test_user_registration_signal_disabled(self):
        """Test that welcome email is NOT sent automatically when new user is created."""
        # This test verifies that the signal is disabled by checking that the signal function is commented out
        
        # Read the signals.py file to verify the signal is disabled
        import inspect
        from django_cfg.apps.accounts import signals
        
        # Get the source code of the signals module
        source = inspect.getsource(signals)
        
        # Check that send_user_registration_email is commented out
        self.assertIn("# @receiver(post_save, sender=User)", source)
        self.assertIn("# def send_user_registration_email", source)
        
        print("✅ Welcome email signal is properly disabled")

    def test_user_profile_update_signal(self):
        """Test that security alert is sent when user profile is updated."""
        with patch(
            "django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_profile_update_notification"
        ) as mock_send_security:
            user = User.objects.create(**self.user_data)

            # Change email directly on the user object and save
            user.email = "newemail@example.com"
            user.save()

            # Check that the signal was triggered
            mock_send_security.assert_called()
            args, kwargs = mock_send_security.call_args
            # The second argument should be the changes list
            self.assertIn("email address", args[1])

    def test_signal_error_handling(self):
        """Test that signals handle errors gracefully."""
        with patch(
            "django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_profile_update_notification",
            side_effect=Exception("Email service error"),
        ):
            user = User.objects.create(**self.user_data)
            # Change profile to trigger signal
            user.email = "newemail@example.com"
            user.save()
            # Test passes if no exception is raised

    def test_multiple_profile_changes(self):
        """Test that security alert is sent for multiple profile changes."""
        with patch(
            "django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_profile_update_notification"
        ) as mock_send:
            user = User.objects.create(**self.user_data)

            # Change multiple fields directly on the user object
            user.email = "newemail@example.com"
            user.username = "newusername"
            user.first_name = "New"
            user.save()

            mock_send.assert_called()
            args, kwargs = mock_send.call_args
            # The second argument should be the changes list
            changes_list = args[1]
            self.assertIn("email address", changes_list)
            self.assertIn("username", changes_list)
            self.assertIn("name", changes_list)

    def test_login_notification_signal(self):
        """Test that login notification is sent when user logs in."""
        user = User.objects.create(**self.user_data)

        with patch(
            "django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_login_notification"
        ) as mock_send_login:
            # Simulate login signal
            trigger_login_notification(user=user, ip_address="127.0.0.1")

            # Check that the signal was triggered
            mock_send_login.assert_called()
            args, kwargs = mock_send_login.call_args
            # Check that the user is passed as first argument
            self.assertEqual(args[0], user)