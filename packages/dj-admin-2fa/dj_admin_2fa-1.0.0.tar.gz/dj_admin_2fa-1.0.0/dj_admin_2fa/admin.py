from django.contrib import admin

from .models import BackupCode, TOTPDevice, TrustedDevice


class TOTPDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "confirmed", "secret_key", "digits", "algorithm")

class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ("username", "code", "used")
    search_fields = ["code"]


class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ("username", "device_identifier", "expires_at")
    search_fields = ["device_identifier"]


admin.site.register(TOTPDevice, TOTPDeviceAdmin)
admin.site.register(BackupCode, BackupCodeAdmin)
admin.site.register(TrustedDevice, TrustedDeviceAdmin)
