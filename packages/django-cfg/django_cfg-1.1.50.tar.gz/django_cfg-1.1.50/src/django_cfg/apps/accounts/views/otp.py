from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
import logging
import traceback

from ..services import OTPService
from ..serializers.otp import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    OTPRequestResponseSerializer,
    OTPVerifyResponseSerializer,
    OTPErrorResponseSerializer,
)
from ..serializers.profile import UserSerializer
from django.contrib.auth import get_user_model
from ..utils.notifications import AccountNotifications

logger = logging.getLogger(__name__)


class OTPViewSet(viewsets.GenericViewSet):
    """OTP authentication ViewSet with nested router support."""

    permission_classes = [permissions.AllowAny]
    serializer_class = OTPRequestSerializer  # Default serializer for OPTIONS requests

    @extend_schema(
        request=OTPRequestSerializer,
        responses={
            200: OTPRequestResponseSerializer,
            400: OTPErrorResponseSerializer,
            500: OTPErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="request")
    def request_otp(self, request):
        """Request OTP code to email."""
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        channel = serializer.validated_data.get("channel")
        source_url = serializer.validated_data.get("source_url")
        logger.debug(f"Starting OTP request for {identifier} via {channel}, source: {source_url}")

        try:
            if channel == 'phone':
                success, error_type = OTPService.request_phone_otp(identifier, source_url)
            else:  # email channel (default)
                success, error_type = OTPService.request_email_otp(identifier, source_url)
        except Exception as e:
            # Log the full traceback for debugging
            logger.error(f"OTP request failed with exception: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return Response(
                {"error": "Internal server error during OTP request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if success:
            channel_name = "phone number" if channel == 'phone' else "email address"
            return Response(
                {"message": f"OTP sent to your {channel_name}"}, status=status.HTTP_200_OK
            )
        else:
            if error_type in ["invalid_email", "invalid_phone"]:
                field_name = "phone number" if error_type == "invalid_phone" else "email address"
                logger.warning(f"Invalid {field_name} provided: {identifier}")
                return Response(
                    {"error": f"Invalid {field_name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif error_type == "user_creation_failed":
                # Log additional details for user creation failure
                logger.error(f"User creation failed for {identifier}: {error_type}")
                logger.error(
                    f"Full traceback for user creation failure: {traceback.format_exc()}"
                )
                return Response(
                    {"error": "Failed to create user account"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            elif error_type in ["email_send_failed", "phone_send_failed"]:
                # Handle delivery failures
                channel_name = "phone number" if error_type == "phone_send_failed" else "email address"
                logger.error(f"Failed to send OTP to {channel_name}: {identifier}")
                return Response(
                    {"error": f"Failed to send OTP to your {channel_name}. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            else:
                logger.error(f"Unknown error type: {error_type} for {identifier}")
                return Response(
                    {"error": "Failed to send OTP"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: OTPVerifyResponseSerializer,
            400: OTPErrorResponseSerializer,
            410: OTPErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="verify")
    def verify_otp(self, request):
        """Verify OTP code and return JWT tokens."""
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        otp = serializer.validated_data["otp"]
        channel = serializer.validated_data.get("channel")
        source_url = serializer.validated_data.get("source_url")

        if channel == 'phone':
            user = OTPService.verify_phone_otp(identifier, otp, source_url)
        else:  # email channel (default)
            user = OTPService.verify_email_otp(identifier, otp, source_url)

        if user:
            # Check if this is a new user (created recently, within last 5 minutes)
            from django.utils import timezone
            from datetime import timedelta
            
            is_new_user = (timezone.now() - user.date_joined) < timedelta(minutes=5)
            
            # Send welcome email only for new users
            if is_new_user:
                try:
                    AccountNotifications.send_welcome_email(user, send_email=True, send_telegram=False)
                    logger.info(f"Welcome email sent to new user: {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send welcome email to {user.email}: {e}")
            
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Check if user was deleted after OTP was sent
            try:
                User = get_user_model()
                if channel == 'phone':
                    User.objects.get(phone=identifier)
                else:
                    User.objects.get(email=identifier)
                # User exists but OTP is invalid
                return Response(
                    {"error": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                # User was deleted after OTP was sent
                return Response(
                    {"error": "User account has been deleted"},
                    status=status.HTTP_410_GONE,
                )
