import base64
import io
import random
import string

import pyotp
import qrcode
from django.conf import settings


def generate_secret_key():
    """Generate a random secret key for TOTP."""
    return pyotp.random_base32()


def generate_qr_code(data_uri):
    """Generate a QR code as a base64-encoded image."""
    img = qrcode.make(data_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def generate_backup_codes(count=10, length=10):
    """Generate backup/recovery codes."""
    chars = string.ascii_uppercase + string.digits
    # Exclude potentially confusing characters
    chars = chars.replace("0", "").replace("O", "").replace("1", "").replace("I", "")

    codes = []
    for _ in range(count):
        # Format as XXXX-XXXX-XX for readability
        code = "".join(random.choices(chars, k=length))
        formatted_code = f"{code[:4]}-{code[4:8]}-{code[8:]}"
        codes.append(formatted_code)

    return codes


def get_admin_2fa_settings():
    """Get 2FA settings with defaults."""
    defaults = {
        "ISSUER_NAME": "Django Admin SurajPatidar",
        "REDIRECT_URL": "/admin/",
        "LOGIN_URL": "admin:login",
        "BACKUP_CODES_COUNT": 10,
        "TRUSTED_DEVICE_DAYS": 30,
        "TOTP_DIGITS": 6,
        "TOTP_STEP": 30,
        "TOTP_ALGORITHM": "sha1",
        "VERIFICATION_TIMEOUT": 300,  # 5 minutes
        "RATE_LIMIT_ATTEMPTS": 5,
        "RATE_LIMIT_TIMEOUT": 300,  # 5 minutes
    }

    user_settings = getattr(settings, "DJ_ADMIN_2FA", {})

    # Merge defaults with user settings
    return {**defaults, **user_settings}


def should_require_2fa(user):
    """Determine if a user should be required to use 2FA."""
    # Admin users should always use 2FA
    if user.is_superuser or user.is_staff:
        return True

    # Check if 2FA is required for specific users or groups
    settings_dict = get_admin_2fa_settings()
    required_groups = settings_dict.get("REQUIRED_GROUPS", [])

    if required_groups:
        return user.groups.filter(name__in=required_groups).exists()

    # Check setting to require 2FA for all users
    return settings_dict.get("REQUIRED_FOR_ALL", False)
