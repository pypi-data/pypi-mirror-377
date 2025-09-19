import re

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .utils import get_admin_2fa_settings, should_require_2fa


class Admin2FAMiddleware:
    """Middleware to enforce 2FA for admin users."""

    def __init__(self, get_response):
        self.get_response = get_response
        # Compile a list of exempt URLs
        self.exempt_urls = [
            re.compile(r"^/admin/login/$"),
            re.compile(r"^/admin/logout/$"),
            re.compile(r"^/admin-2fa-plus/"),
            re.compile(r"^/static/"),
            re.compile(r"^/media/"),
        ]

        # Add any user-defined exempt URLs
        user_exempt = getattr(settings, "ADMIN_2FA_PLUS", {}).get("EXEMPT_URLS", [])
        for url in user_exempt:
            self.exempt_urls.append(re.compile(url))

    def __call__(self, request):
        # Skip if the user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip if the path is in exempt URLs
        path = request.path_info.lstrip("/")
        for exempt_url in self.exempt_urls:
            if exempt_url.match(path):
                return self.get_response(request)

        # Check if path is in the admin
        if not path.startswith("admin/"):
            return self.get_response(request)

        # Check if user needs 2FA
        if not should_require_2fa(request.user):
            return self.get_response(request)

        # Check if 2FA is already verified
        if request.session.get("is_2fa_verified", False):
            return self.get_response(request)

        # Check for trusted device
        if self._is_trusted_device(request):
            request.session["is_2fa_verified"] = True
            return self.get_response(request)

        # Redirect to 2FA verification
        verify_url = reverse("admin-2fa-verify")
        messages.warning(request, "Two-factor authentication is required to access the admin area.")
        return redirect(verify_url)

    def _is_trusted_device(self, request):
        """Check if the current device is trusted."""
        # Import here to avoid circular imports
        from .models import TrustedDevice

        # Get the trusted device token from cookie
        token = request.COOKIES.get("admin_2fa_trust")
        if not token:
            return False

        # Try to find a matching trusted device
        try:
            device = TrustedDevice.objects.get(device_identifier=token, device__user=request.user)
            return device.is_valid()
        except TrustedDevice.DoesNotExist:
            return False


class Rate2FALimitMiddleware:
    """Middleware to handle rate limiting for 2FA attempts."""

    def __init__(self, get_response):
        self.get_response = get_response
        # Only check rate limiting on these paths
        self.rate_limit_paths = [
            reverse("admin-2fa-verify"),
            reverse("admin-2fa-recovery"),
        ]

    def __call__(self, request):
        # Only check POST requests to rate limited paths
        if request.method == "POST" and request.path in self.rate_limit_paths:
            if self._is_rate_limited(request):
                messages.error(request, "Too many attempts. Please try again later.")
                return redirect(request.path)

        return self.get_response(request)

    def _is_rate_limited(self, request):
        """Check if the current request is rate limited."""
        from django.core.cache import cache

        if not request.user.is_authenticated:
            return False

        settings_dict = get_admin_2fa_settings()
        max_attempts = settings_dict.get("RATE_LIMIT_ATTEMPTS", 5)
        timeout = settings_dict.get("RATE_LIMIT_TIMEOUT", 300)

        # Create a key for this user and path
        key = f"2fa_attempts_{request.user.id}_{request.path}"
        attempts = cache.get(key, 0)

        if attempts >= max_attempts:
            return True

        # Increment attempt counter
        cache.set(key, attempts + 1, timeout)
        return False
