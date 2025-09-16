import logging
import traceback
from django.utils import timezone
from django.db import transaction
from typing import Optional, Tuple
import re

from django_cfg.modules.django_telegram import DjangoTelegram
from django_cfg.modules.django_twilio import SimpleTwilioService
from ..models import OTPSecret, CustomUser
from ..utils.notifications import AccountNotifications
from ..signals import notify_failed_otp_attempt

logger = logging.getLogger(__name__)


class OTPService:
    """Simple OTP service for authentication supporting both email and phone channels."""
    
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        # Clean phone number - remove spaces, dashes, parentheses
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        # Basic phone validation - E.164 format: +[1-9][0-9]{6,14}
        phone_pattern = r'^\+[1-9]\d{6,14}$'  # E.164 format: minimum 7 digits, maximum 15
        return bool(re.match(phone_pattern, clean_phone))
    
    @staticmethod
    def _get_temp_email_domain(source_url: Optional[str] = None) -> str:
        """
        Get domain for temporary email addresses.
        
        Priority:
        1. Extract domain from source_url
        2. Use config.site_url domain
        3. Fallback to 'temp.local'
        """
        try:
            from django_cfg.core.config import get_current_config
            from urllib.parse import urlparse
            
            config = get_current_config()
            
            # Try to extract domain from source_url
            if source_url:
                try:
                    parsed = urlparse(source_url)
                    if parsed.netloc:
                        # Remove www. prefix if present
                        domain = parsed.netloc
                        if domain.startswith("www."):
                            domain = domain[4:]
                        return domain
                except:
                    pass
            
            # Try to use config.site_url domain
            if config and config.site_url:
                try:
                    parsed = urlparse(config.site_url)
                    if parsed.netloc:
                        domain = parsed.netloc
                        if domain.startswith("www."):
                            domain = domain[4:]
                        return domain
                except:
                    pass
            
            # Fallback to temp.local
            return "temp.local"
            
        except Exception:
            return "temp.local"

    @staticmethod
    def _determine_channel(identifier: str) -> str:
        """Determine if identifier is email or phone."""
        if '@' in identifier:
            return 'email'
        elif identifier.startswith('+') or identifier.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
            return 'phone'
        else:
            # Default to email for backward compatibility
            return 'email'

    @staticmethod
    def _get_otp_url(otp_code: str) -> str:
        """Get OTP verification URL from configuration."""
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'get_otp_url'):
                return config.get_otp_url(otp_code)
            else:
                # Fallback URL if config is not available
                return f"#otp-{otp_code}"
        except Exception as e:
            logger.warning(f"Could not generate OTP URL: {e}")
            return f"#otp-{otp_code}"

    @staticmethod
    @transaction.atomic
    def request_otp(
        identifier: str, 
        channel: Optional[str] = None, 
        source_url: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Generate and send OTP to email or phone. Returns (success, error_type)."""
        return OTPService._request_otp_internal(identifier, channel, source_url)
    
    @staticmethod
    @transaction.atomic
    def request_email_otp(email: str, source_url: Optional[str] = None) -> Tuple[bool, str]:
        """Generate and send OTP to email (backward compatibility)."""
        return OTPService._request_otp_internal(email, 'email', source_url)
    
    @staticmethod
    @transaction.atomic
    def request_phone_otp(phone: str, source_url: Optional[str] = None) -> Tuple[bool, str]:
        """Generate and send OTP to phone."""
        return OTPService._request_otp_internal(phone, 'phone', source_url)
    
    @staticmethod
    @transaction.atomic
    def _request_otp_internal(
        identifier: str, 
        channel: Optional[str] = None, 
        source_url: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Internal method to generate and send OTP to email or phone."""
        # Auto-detect channel if not specified
        if not channel:
            channel = OTPService._determine_channel(identifier)
        
        # Clean and validate identifier
        if channel == 'email':
            cleaned_identifier = identifier.strip().lower()
            if not cleaned_identifier or '@' not in cleaned_identifier:
                return False, "invalid_email"
        elif channel == 'phone':
            cleaned_identifier = identifier.strip()
            if not OTPService._validate_phone(cleaned_identifier):
                return False, "invalid_phone"
        else:
            return False, "invalid_channel"

        # Find or create user using the manager's register_user method
        try:
            if channel == 'email':
                logger.info(f"Attempting to register user for email: {cleaned_identifier}")
                user, created = CustomUser.objects.register_user(
                    cleaned_identifier, source_url=source_url
                )
            else:  # phone channel
                logger.info(f"Attempting to find/create user for phone: {cleaned_identifier}")
                # For phone, we need to find user by phone or create with temp email
                try:
                    user = CustomUser.objects.get(phone=cleaned_identifier)
                    created = False
                except CustomUser.DoesNotExist:
                    # Create user with temp email based on phone and domain
                    phone_clean = cleaned_identifier.replace('+', '').replace(' ', '')
                    domain = OTPService._get_temp_email_domain(source_url)
                    temp_email = f"phone_{phone_clean}@{domain}"
                    user, created = CustomUser.objects.register_user(
                        temp_email, source_url=source_url
                    )
                    user.phone = cleaned_identifier
                    user.save()

            if created:
                logger.info(f"Created new user: {cleaned_identifier}")

        except Exception as e:
            logger.error(
                f"Error creating/finding user for {channel} {cleaned_identifier}: {str(e)}"
            )
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False, "user_creation_failed"

        # Check for existing active OTP
        existing_otp = OTPSecret.objects.filter(
            recipient=cleaned_identifier,
            channel_type=channel,
            is_used=False, 
            expires_at__gt=timezone.now()
        ).first()

        if existing_otp and existing_otp.is_valid:
            otp_code = existing_otp.secret
            logger.info(f"Reusing active OTP for {cleaned_identifier} ({channel})")
        else:
            # Invalidate old OTPs for this identifier and channel
            OTPSecret.objects.filter(
                recipient=cleaned_identifier,
                channel_type=channel,
                is_used=False
            ).update(is_used=True)

            # Generate new OTP using the appropriate class method
            if channel == 'email':
                otp_secret = OTPSecret.create_for_email(cleaned_identifier)
            else:  # phone
                otp_secret = OTPSecret.create_for_phone(cleaned_identifier)
            
            otp_code = otp_secret.secret
            logger.info(f"Generated new OTP for {cleaned_identifier} ({channel})")

        # Send OTP via appropriate channel
        try:
            if channel == 'email':
                # Generate OTP link
                otp_link = OTPService._get_otp_url(otp_code)
                # Send OTP email
                AccountNotifications.send_otp_notification(
                    user, otp_code, is_new_user=created, source_url=source_url, channel='email'
                )
            else:  # phone channel
                # Send OTP via SMS using Twilio
                AccountNotifications.send_phone_otp_notification(
                    user, otp_code, cleaned_identifier, is_new_user=created, source_url=source_url
                )

            return True, "success"
        except Exception as e:
            logger.error(f"Failed to send OTP via {channel}: {e}")
            return False, f"{channel}_send_failed"

    @staticmethod
    def verify_otp(
        identifier: str, 
        otp_code: str, 
        channel: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Optional[CustomUser]:
        """Verify OTP and return user if valid."""
        return OTPService._verify_otp_internal(identifier, otp_code, channel, source_url)
    
    @staticmethod
    def verify_email_otp(
        email: str, otp_code: str, source_url: Optional[str] = None
    ) -> Optional[CustomUser]:
        """Verify email OTP (backward compatibility)."""
        return OTPService._verify_otp_internal(email, otp_code, 'email', source_url)
    
    @staticmethod
    def verify_phone_otp(
        phone: str, otp_code: str, source_url: Optional[str] = None
    ) -> Optional[CustomUser]:
        """Verify phone OTP."""
        return OTPService._verify_otp_internal(phone, otp_code, 'phone', source_url)
    
    @staticmethod
    def _verify_otp_internal(
        identifier: str, 
        otp_code: str, 
        channel: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Optional[CustomUser]:
        """Internal method to verify OTP."""
        if not identifier or not otp_code:
            return None

        # Auto-detect channel if not specified
        if not channel:
            channel = OTPService._determine_channel(identifier)
        
        # Clean identifier
        if channel == 'email':
            cleaned_identifier = identifier.strip().lower()
        else:
            cleaned_identifier = identifier.strip()
        
        cleaned_otp = otp_code.strip()

        if not cleaned_identifier or not cleaned_otp:
            return None

        try:
            otp_secret = OTPSecret.objects.filter(
                recipient=cleaned_identifier,
                channel_type=channel,
                secret=cleaned_otp,
                is_used=False,
                expires_at__gt=timezone.now(),
            ).first()

            if not otp_secret or not otp_secret.is_valid:
                logger.warning(f"Invalid OTP for {cleaned_identifier} ({channel})")
                
                # Send notification for failed OTP attempt
                AccountNotifications.send_failed_otp_attempt(
                    cleaned_identifier, channel=channel, reason="Invalid or expired OTP"
                )
                
                return None

            # Mark OTP as used
            otp_secret.mark_used()

            # Get user based on channel
            try:
                if channel == 'email':
                    user = CustomUser.objects.get(email=cleaned_identifier)
                else:  # phone channel
                    user = CustomUser.objects.get(phone=cleaned_identifier)
                    # Mark phone as verified
                    if not user.phone_verified:
                        user.phone_verified = True
                        user.save(update_fields=['phone_verified'])

                # Link user to source if provided (for existing users logging in from new sources)
                if source_url:
                    CustomUser.objects._link_user_to_source(
                        user, source_url, is_new_user=False
                    )

                # Send notification for successful OTP verification
                AccountNotifications.send_otp_verification_success(user, source_url)

                logger.info(f"OTP verified for {cleaned_identifier} ({channel})")
                return user
            except CustomUser.DoesNotExist:
                # User was deleted after OTP was sent
                logger.warning(f"User was deleted after OTP was sent: {cleaned_identifier} ({channel})")
                return None

        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return None
