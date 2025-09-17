from rest_framework import serializers
from ..models import OTPSecret
from .profile import UserSerializer


class OTPSerializer(serializers.ModelSerializer):
    """Serializer for OTP operations."""

    class Meta:
        model = OTPSecret
        fields = ["recipient", "channel_type", "secret"]
        read_only_fields = ["secret"]


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP request supporting both email and phone."""

    identifier = serializers.CharField(
        help_text="Email address or phone number for OTP delivery"
    )
    channel = serializers.ChoiceField(
        choices=[('email', 'Email'), ('phone', 'Phone')],
        required=False,
        help_text="Delivery channel - auto-detected if not specified"
    )
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking registration (e.g., https://reforms.ai)",
    )

    def validate_identifier(self, value):
        """Validate identifier format."""
        if not value:
            raise serializers.ValidationError("Identifier (email or phone) is required.")
        
        # Auto-detect if it's email
        if '@' in value:
            return value.lower()
        return value
    
    def validate(self, attrs):
        """Auto-detect channel if not specified."""
        identifier = attrs.get('identifier')
        
        # Auto-detect channel if not specified
        if not attrs.get('channel'):
            if '@' in identifier:
                attrs['channel'] = 'email'
            elif identifier.startswith('+') or identifier.replace(' ', '').replace('-', '').isdigit():
                attrs['channel'] = 'phone'
            else:
                attrs['channel'] = 'email'  # Default
        
        return attrs

    def validate_source_url(self, value):
        """Validate source URL format."""
        if not value or not value.strip():
            return None
        return value


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification supporting both email and phone."""

    identifier = serializers.CharField(
        help_text="Email address or phone number used for OTP request"
    )
    otp = serializers.CharField(max_length=6, min_length=6)
    channel = serializers.ChoiceField(
        choices=[('email', 'Email'), ('phone', 'Phone')],
        required=False,
        help_text="Delivery channel - auto-detected if not specified"
    )
    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Source URL for tracking login (e.g., https://reforms.ai)",
    )

    def validate_identifier(self, value):
        """Validate identifier format."""
        if not value:
            raise serializers.ValidationError("Identifier (email or phone) is required.")
        
        # Auto-detect if it's email
        if '@' in value:
            return value.lower()
        return value

    def validate_otp(self, value):
        """Validate OTP format."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value
    
    def validate(self, attrs):
        """Auto-detect channel if not specified."""
        identifier = attrs.get('identifier')
        
        # Auto-detect channel if not specified
        if not attrs.get('channel'):
            if '@' in identifier:
                attrs['channel'] = 'email'
            elif identifier.startswith('+') or identifier.replace(' ', '').replace('-', '').isdigit():
                attrs['channel'] = 'phone'
            else:
                attrs['channel'] = 'email'  # Default
        
        return attrs

    def validate_source_url(self, value):
        """Validate source URL format."""
        if not value or not value.strip():
            return None
        return value


class OTPVerifyResponseSerializer(serializers.Serializer):
    """OTP verification response."""

    refresh = serializers.CharField(help_text="JWT refresh token")
    access = serializers.CharField(help_text="JWT access token")
    user = UserSerializer(help_text="User information")


class OTPRequestResponseSerializer(serializers.Serializer):
    """OTP request response."""

    message = serializers.CharField(help_text="Success message")


class OTPErrorResponseSerializer(serializers.Serializer):
    """Error response for OTP operations."""

    error = serializers.CharField(help_text="Error message")