import random
import string

import pyotp
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class TOTPDevice(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_2fa_totp_devices",
        verbose_name="user",
    )
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    digits = models.PositiveIntegerField(default=6)
    step = models.PositiveIntegerField(default=30)
    algorithm = models.CharField(max_length=32, default="sha1")

    def generate_qr_code_uri(self, issuer_name):
        """Generate the TOTP URI for QR code."""
        return pyotp.totp.TOTP(self.secret_key).provisioning_uri(name=self.user.email, issuer_name=issuer_name)

    def verify_token(self, token):
        """Verify if the token provided is correct."""
        totp = pyotp.TOTP(self.secret_key, digits=self.digits, interval=self.step)
        return totp.verify(token)


class BackupCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    used = models.BooleanField(default=False)
    device = models.ForeignKey(TOTPDevice, on_delete=models.CASCADE, related_name="backup_codes")

    def use(self):
        """Mark the backup code as used."""
        self.used = True
        self.save()

    @property
    def username(self):
        if self.device and self.device.user:
            return self.device.user.username
        return "(no user)"

class TrustedDevice(models.Model):
    device = models.ForeignKey(TOTPDevice, on_delete=models.CASCADE, related_name="trusted_devices")
    device_identifier = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at

    @classmethod
    def create_for_request(cls, device, days_valid=30):
        device_identifier = f"{device.user.username}_{random_string(16)}"
        expires_at = timezone.now() + timezone.timedelta(days=days_valid)
        return cls.objects.create(device=device, device_identifier=device_identifier, expires_at=expires_at)

    @property
    def username(self):
        if self.device and self.device.user:
            return self.device.user.username
        return "(no user)"

def random_string(length):
    """Generate a random string of the given length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
