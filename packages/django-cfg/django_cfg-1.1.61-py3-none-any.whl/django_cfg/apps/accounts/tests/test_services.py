from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch
from datetime import timedelta

from ..services import OTPService
from ..models import OTPSecret, RegistrationSource, UserRegistrationSource

User = get_user_model()


class OTPServiceTest(TestCase):
    """Test OTPService."""

    def setUp(self):
        self.email = "test@example.com"
        self.source_url = "https://reforms.ai"

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_otp_notification")
    def test_request_otp_new_user(self, mock_email):
        """Test OTP request for new user."""
        mock_email.return_value = True

        success, error_type = OTPService.request_email_otp(self.email)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # User should be created
        user = User.objects.get(email=self.email)
        self.assertIsNotNone(user)

        # OTP should be created
        otp = OTPSecret.objects.get(recipient=self.email, channel_type='email')
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.secret), 6)
        self.assertTrue(otp.secret.isdigit())

        # OTP notification should be sent
        mock_email.assert_called_once()

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_otp_notification")
    def test_request_otp_new_user_with_source_url(self, mock_email):
        """Test OTP request for new user with source_url."""
        mock_email.return_value = True

        success, error_type = OTPService.request_email_otp(self.email, self.source_url)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # User should be created
        user = User.objects.get(email=self.email)
        self.assertIsNotNone(user)

        # Source should be created
        source = RegistrationSource.objects.get(url=self.source_url)
        self.assertIsNotNone(source)
        self.assertEqual(source.name, "reforms.ai")

        # User-source relationship should be created
        user_source = UserRegistrationSource.objects.get(user=user, source=source)
        self.assertIsNotNone(user_source)
        self.assertTrue(user_source.first_registration)

        # OTP should be created
        otp = OTPSecret.objects.get(recipient=self.email, channel_type='email')
        self.assertIsNotNone(otp)

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_otp_notification")
    def test_request_otp_existing_user(self, mock_email):
        """Test OTP request for existing user."""
        mock_email.return_value = True

        # Create existing user
        User.objects.create_user(email=self.email, username="existing_user")

        success, error_type = OTPService.request_email_otp(self.email)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Should not create duplicate user
        users = User.objects.filter(email=self.email)
        self.assertEqual(users.count(), 1)

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_otp_notification")
    def test_request_otp_existing_user_with_source_url(self, mock_email):
        """Test OTP request for existing user with source_url."""
        mock_email.return_value = True

        # Create existing user
        user = User.objects.create_user(email=self.email, username="existing_user")

        success, error_type = OTPService.request_email_otp(self.email, self.source_url)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Source should be created
        source = RegistrationSource.objects.get(url=self.source_url)
        self.assertIsNotNone(source)

        # User-source relationship should be created
        user_source = UserRegistrationSource.objects.get(user=user, source=source)
        self.assertIsNotNone(user_source)
        self.assertFalse(user_source.first_registration)  # Not first registration

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_otp_notification")
    def test_request_otp_reuse_active(self, mock_email):
        """Test OTP request reuses active OTP."""
        mock_email.return_value = True

        # Create existing OTP with known secret
        existing_otp = OTPSecret.create_for_email(self.email)
        existing_secret = existing_otp.secret

        success, error_type = OTPService.request_email_otp(self.email)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Should reuse existing OTP
        otp_count = OTPSecret.objects.filter(recipient=self.email, channel_type='email').count()
        self.assertEqual(otp_count, 1)

        # Should use existing secret
        otp = OTPSecret.objects.get(recipient=self.email, channel_type='email')
        self.assertEqual(otp.secret, existing_secret)

    @patch("django_cfg.apps.accounts.utils.notifications.AccountNotifications.send_otp_notification")
    def test_request_otp_email_failure(self, mock_email):
        """Test OTP request when email fails."""
        mock_email.side_effect = Exception("Email service error")

        success, error_type = OTPService.request_email_otp(self.email)

        self.assertFalse(success)
        self.assertEqual(error_type, "email_send_failed")

    def test_request_otp_invalid_email(self):
        """Test OTP request with invalid email."""
        success, error_type = OTPService.request_email_otp("")

        self.assertFalse(success)
        self.assertEqual(error_type, "invalid_email")

    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        # Create user and OTP
        user = User.objects.create_user(email=self.email, username="testuser")
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = "123456"  # Set known secret for test
        otp.save()

        # Verify OTP
        result_user = OTPService.verify_email_otp(self.email, "123456")

        self.assertIsNotNone(result_user)
        self.assertEqual(result_user, user)

        # OTP should be marked as used
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_verify_otp_success_with_source_url(self):
        """Test successful OTP verification with source_url."""
        # Create user and OTP
        user = User.objects.create_user(email=self.email, username="testuser")
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = "123456"  # Set known secret for test
        otp.save()

        # Verify OTP with source_url
        result_user = OTPService.verify_email_otp(self.email, "123456", self.source_url)

        self.assertIsNotNone(result_user)
        self.assertEqual(result_user, user)

        # Source should be created
        source = RegistrationSource.objects.get(url=self.source_url)
        self.assertIsNotNone(source)

        # User-source relationship should be created
        user_source = UserRegistrationSource.objects.get(user=user, source=source)
        self.assertIsNotNone(user_source)
        self.assertFalse(user_source.first_registration)  # Not first registration

    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code."""
        # Create user and OTP
        User.objects.create_user(email=self.email, username="testuser")
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = "123456"  # Set known secret for test
        otp.save()

        # Try to verify with wrong code
        result_user = OTPService.verify_email_otp(self.email, "654321")

        self.assertIsNone(result_user)

    def test_verify_otp_expired(self):
        """Test OTP verification with expired OTP."""
        # Create user and expired OTP
        User.objects.create_user(email=self.email, username="testuser")
        expired_time = timezone.now() - timedelta(minutes=11)
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = "123456"  # Set known secret for test
        otp.expires_at = expired_time
        otp.save()

        # Try to verify expired OTP
        result_user = OTPService.verify_email_otp(self.email, "123456")

        self.assertIsNone(result_user)

    def test_verify_otp_used(self):
        """Test OTP verification with used OTP."""
        # Create user and used OTP
        User.objects.create_user(email=self.email, username="testuser")
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = "123456"  # Set known secret for test
        otp.is_used = True
        otp.save()

        # Try to verify used OTP
        result_user = OTPService.verify_email_otp(self.email, "123456")

        self.assertIsNone(result_user)

    def test_verify_otp_no_user(self):
        """Test OTP verification when user doesn't exist."""
        # Create OTP but no user
        otp = OTPSecret.create_for_email(self.email)
        otp.secret = "123456"  # Set known secret for test
        otp.save()

        # Try to verify OTP
        result_user = OTPService.verify_email_otp(self.email, "123456")

        self.assertIsNone(result_user)

    def test_verify_otp_invalid_input(self):
        """Test OTP verification with invalid input."""
        # Test with empty email
        result_user = OTPService.verify_email_otp("", "123456")
        self.assertIsNone(result_user)

        # Test with empty OTP
        result_user = OTPService.verify_email_otp(self.email, "")
        self.assertIsNone(result_user)

        # Test with None values
        result_user = OTPService.verify_email_otp(None, "123456")
        self.assertIsNone(result_user)

        result_user = OTPService.verify_email_otp(self.email, None)
        self.assertIsNone(result_user)


class PhoneOTPServiceTest(TestCase):
    """Test Phone OTP Service functionality."""

    def setUp(self):
        self.phone = "+1234567890"
        self.email = "test@example.com"

    @patch("django_cfg.apps.accounts.services.otp_service.send_whatsapp_otp")
    def test_request_phone_otp_new_user(self, mock_whatsapp_otp):
        """Test phone OTP request for new user."""
        mock_whatsapp_otp.return_value = (True, "OTP sent successfully")

        success, error_type = OTPService.request_phone_otp(self.phone)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # User should be created with temp email
        users = User.objects.filter(phone=self.phone)
        self.assertEqual(users.count(), 1)
        user = users.first()
        self.assertIsNotNone(user)
        self.assertTrue(user.email.startswith("phone_"))

        # OTP should be created for phone
        otp = OTPSecret.objects.get(recipient=self.phone, channel_type='phone')
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.secret), 6)
        self.assertTrue(otp.secret.isdigit())
        self.assertEqual(otp.channel_type, 'phone')  # Phone channel

        # WhatsApp OTP should be sent
        mock_whatsapp_otp.assert_called_once()

    @patch("django_cfg.apps.accounts.services.otp_service.send_whatsapp_otp")
    def test_request_phone_otp_existing_user(self, mock_whatsapp_otp):
        """Test phone OTP request for existing user."""
        mock_whatsapp_otp.return_value = (True, "OTP sent successfully")

        # Create existing user with phone
        User.objects.create_user(
            email=self.email, 
            username="existing_user",
            phone=self.phone
        )

        success, error_type = OTPService.request_phone_otp(self.phone)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Should not create duplicate user
        users = User.objects.filter(phone=self.phone)
        self.assertEqual(users.count(), 1)

    def test_request_phone_otp_invalid_phone(self):
        """Test phone OTP request with invalid phone."""
        success, error_type = OTPService.request_phone_otp("invalid-phone")

        self.assertFalse(success)
        self.assertEqual(error_type, "invalid_phone")

    @patch("django_cfg.apps.accounts.services.otp_service.verify_otp")
    def test_verify_phone_otp_success(self, mock_verify_otp):
        """Test successful phone OTP verification."""
        mock_verify_otp.return_value = (True, "OTP verified successfully")
        
        # Create user with phone
        user = User.objects.create_user(
            email=self.email,
            username="testuser",
            phone=self.phone
        )
        
        # Create phone OTP
        otp = OTPSecret.create_for_phone(self.phone)
        otp.secret = "123456"  # Set known secret for test
        otp.save()

        # Verify OTP
        result_user = OTPService.verify_phone_otp(self.phone, "123456")

        self.assertIsNotNone(result_user)
        self.assertEqual(result_user, user)
        self.assertTrue(result_user.phone_verified)  # Should mark phone as verified

        # Mock verify_otp was called
        mock_verify_otp.assert_called_once_with(self.phone, "123456")

    @patch("django_cfg.apps.accounts.services.otp_service.verify_otp")
    def test_verify_phone_otp_invalid_code(self, mock_verify_otp):
        """Test phone OTP verification with invalid code."""
        mock_verify_otp.return_value = (False, "Invalid OTP code")
        
        # Create user with phone
        User.objects.create_user(
            email=self.email,
            username="testuser", 
            phone=self.phone
        )
        
        # Create phone OTP
        otp = OTPSecret.create_for_phone(self.phone)
        otp.secret = "123456"  # Set known secret for test
        otp.save()

        # Try to verify with wrong code
        result_user = OTPService.verify_phone_otp(self.phone, "654321")

        self.assertIsNone(result_user)

    def test_phone_validation(self):
        """Test phone number validation."""
        from ..services.otp_service import OTPService
        
        # Valid phones
        self.assertTrue(OTPService._validate_phone("+1234567890"))
        self.assertTrue(OTPService._validate_phone("+12345678901234"))
        
        # Invalid phones
        self.assertFalse(OTPService._validate_phone("1234567890"))  # No +
        self.assertFalse(OTPService._validate_phone("+0234567890"))  # Starts with 0
        self.assertFalse(OTPService._validate_phone(""))  # Empty
        self.assertFalse(OTPService._validate_phone("+12"))  # Too short

    def test_channel_detection(self):
        """Test automatic channel detection."""
        from ..services.otp_service import OTPService
        
        # Email detection
        self.assertEqual(OTPService._determine_channel("test@example.com"), "email")
        self.assertEqual(OTPService._determine_channel("user+tag@domain.co.uk"), "email")
        
        # Phone detection
        self.assertEqual(OTPService._determine_channel("+1234567890"), "phone")
        self.assertEqual(OTPService._determine_channel("1234567890"), "phone")
        self.assertEqual(OTPService._determine_channel("(555) 123-4567"), "phone")
        
        # Default to email for unclear cases
        self.assertEqual(OTPService._determine_channel("unclear"), "email")
