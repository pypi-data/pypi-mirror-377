from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from .forms import RecoveryCodeForm, TOTPVerificationForm, TrustedDeviceForm
from .models import BackupCode, TOTPDevice, TrustedDevice
from .utils import generate_backup_codes, generate_qr_code, generate_secret_key, get_admin_2fa_settings


def _redirect(request, name, msg=None, level=messages.ERROR):
    if msg:
        messages.add_message(request, level, msg)
    return redirect(reverse(name))


@login_required
def setup_2fa(request):
    """Set up 2FA for a user."""
    settings_dict = get_admin_2fa_settings()
    device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    if device:
        return _redirect(request, "admin:index", "You already have 2FA set up.", messages.INFO)

    device, _ = TOTPDevice.objects.get_or_create(
        user=request.user,
        confirmed=False,
        defaults={
            "secret_key": generate_secret_key(),
            "digits": settings_dict.get("TOTP_DIGITS", 6),
            "step": settings_dict.get("TOTP_STEP", 30),
            "algorithm": settings_dict.get("TOTP_ALGORITHM", "sha1"),
        },
    )

    if not device.secret_key:
        device.secret_key = generate_secret_key()
        device.save()

    request.session["2fa_setup_device_id"] = str(device.id)

    context = {
        "device": device,
        "qr_code": generate_qr_code(device.generate_qr_code_uri(settings_dict.get("ISSUER_NAME"))),
        "secret": device.secret_key,
    }
    return render(request, "admin_2fa_plus/setup.html", context)


@login_required
@never_cache
def verify_setup(request):
    """Verify 2FA setup with a token."""
    device_id = request.session.get("2fa_setup_device_id")
    if not device_id:
        return _redirect(request, "admin-2fa-setup", "Setup session expired. Please start again.")

    try:
        device = TOTPDevice.objects.get(id=device_id, user=request.user)
    except TOTPDevice.DoesNotExist:
        return _redirect(request, "admin-2fa-setup", "Device not found. Please start setup again.")

    if device.confirmed:
        return redirect(get_admin_2fa_settings().get("REDIRECT_URL", "/admin/"))

    settings_dict = get_admin_2fa_settings()

    if request.method == "POST":
        form = TOTPVerificationForm(request.POST)

        if form.is_valid():
            if device.verify_token(form.cleaned_data["token"]):
                device.confirmed = True
                device.save()

                codes = generate_backup_codes(count=settings_dict.get("BACKUP_CODES_COUNT", 10))
                BackupCode.objects.bulk_create([BackupCode(device=device, code=code) for code in codes])

                request.session.update(
                    {
                        "is_2fa_verified": True,
                        "backup_codes": codes,
                    }
                )
                request.session.pop("2fa_setup_device_id", None)

                return redirect(reverse("admin-2fa-backup-codes"))

            messages.error(request, "Invalid verification code. Please try again.")
        else:
            messages.error(request, f"Please fix the errors below. {form.errors}")
    else:
        form = TOTPVerificationForm()

    return render(request, "admin_2fa_plus/verify_setup.html", {"form": form, "device": device})


@login_required
@never_cache
def backup_codes(request):
    """Display and clear backup codes from session after setup."""
    codes = request.session.pop("backup_codes", None)
    if not codes:
        return _redirect(request, "admin:index", "No backup codes to display.", messages.INFO)

    return render(request, "admin_2fa_plus/backup_codes.html", {"codes": codes})


@login_required
def verify_2fa(request):
    """Verify 2FA for admin access."""
    if request.session.get("is_2fa_verified"):
        return redirect(get_admin_2fa_settings().get("REDIRECT_URL", "/admin/"))

    device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    if not device:
        return _redirect(
            request,
            "admin-2fa-setup",
            "You need to set up two-factor authentication first.",
            messages.INFO,
        )

    settings_dict = get_admin_2fa_settings()

    if request.method == "POST":
        form = TOTPVerificationForm(request.POST)
        trust_form = TrustedDeviceForm(request.POST)

        if form.is_valid() and device.verify_token(form.cleaned_data["token"]):
            request.session["is_2fa_verified"] = True
            response = redirect(settings_dict.get("REDIRECT_URL", "/admin/"))

            if trust_form.is_valid() and trust_form.cleaned_data.get("trust_device"):
                trusted = TrustedDevice.create_for_request(
                    device,
                    days_valid=settings_dict.get("TRUSTED_DEVICE_DAYS", 30),
                )
                response.set_cookie(
                    "admin_2fa_trust",
                    trusted.device_identifier,
                    max_age=60 * 60 * 24 * 30,
                    httponly=True,
                    samesite="Lax",
                )
            return response

        messages.error(request, "Invalid verification code. Please try again.")
    else:
        form = TOTPVerificationForm()
        trust_form = TrustedDeviceForm()

    return render(
        request,
        "admin_2fa_plus/verify.html",
        {
            "form": form,
            "trust_form": trust_form,
            "device": device,
            "show_recovery": True,
        },
    )


@login_required
def verify_with_recovery(request):
    """Allow users to verify with a backup code."""
    if request.session.get("is_2fa_verified"):
        return redirect(get_admin_2fa_settings().get("REDIRECT_URL", "/admin/"))

    if request.method == "POST":
        form = RecoveryCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            backup_code = BackupCode.objects.filter(device__user=request.user, code=code, used=False).first()

            if backup_code:
                backup_code.used = True
                backup_code.save()
                request.session["is_2fa_verified"] = True
                return redirect(get_admin_2fa_settings().get("REDIRECT_URL", "/admin/"))

            messages.error(request, "Invalid or already used backup code.")
    else:
        form = RecoveryCodeForm()

    return render(request, "admin_2fa_plus/recovery.html", {"form": form})
