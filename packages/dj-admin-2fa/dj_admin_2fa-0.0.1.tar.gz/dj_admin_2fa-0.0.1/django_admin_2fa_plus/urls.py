from django.urls import path

from . import views

urlpatterns = [
    path("setup/", views.setup_2fa, name="admin-2fa-setup"),
    path("verify-setup/", views.verify_setup, name="admin-2fa-verify-setup"),
    path("backup-codes/", views.backup_codes, name="admin-2fa-backup-codes"),
    path("verify-2fa/", views.verify_2fa, name="admin-2fa-verify"),
    path("recovery/", views.verify_with_recovery, name="admin-2fa-recovery"),
]
