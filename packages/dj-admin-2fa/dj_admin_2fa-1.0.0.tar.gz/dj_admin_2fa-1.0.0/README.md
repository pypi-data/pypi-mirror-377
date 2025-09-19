# Dj Admin 2FA

[![PyPI](https://img.shields.io/pypi/v/django-admin-2fa-plus)](https://pypi.org/project/django-admin-2fa-plus/)
[![License: MIT](https://img.shields.io/pypi/l/dj-admin-2fa)](LICENSE)
[![Django Versions](https://img.shields.io/badge/Django-3.2%2B-blue)](https://www.djangoproject.com/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your-username/django-admin-2fa-plus)

**Dj Admin 2FA ** is a secure, easy-to-use Two-Factor Authentication package for Django Admin. It provides TOTP-based verification (Google Authenticator, Authy, etc.), recovery codes, and optional trusted devices.

---

## 🌟 Features

- 🔐 Secure Django Admin with 2FA
- 📱 TOTP Authentication (Google Authenticator, Authy, 1Password, etc.)
- 🔑 One-time use Backup Recovery Codes
- 📩 Optional Email OTP fallback (configurable)
- 🧩 Admin interface to manage TOTP Devices
- 🎛️ Trusted Device support (via cookies)
- 🎨 Customizable templates
- ⚙️ Middleware-based enforcement
- ⚡ Works with Django 3.2+

---

## 📦 Installation

```bash
pip install dj-admin-2fa
```

Add it to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "dj_admin_2fa",
]
```

Add the middleware near the top of your middleware stack:

```python
MIDDLEWARE = [
    "dj_admin_2fa.middleware.Admin2FAMiddleware",
    ...
]
```

Include the URLs:

```python
# urls.py
path("admin-2fa/", include("dj_admin_2fa.urls")),
```

Run migrations:

```bash
python manage.py migrate
```

---

## 🚀 Quick Start

1. Log in to Django Admin.
2. Go to `/admin-2fa/setup/` to begin TOTP setup.
3. Scan the QR code using your authenticator app.
4. Enter the generated code to confirm.
5. Save the backup codes displayed — each can be used once.
6. Done! 2FA is now required to access the admin area.

---

## ⚙️ Optional Settings

You can override the default behavior using these settings in your Django `settings.py`:
## Admin 2FA settings
DJ_ADMIN_2FA = {
    "ISSUER_NAME": "Django Admin Example",
}

| Setting | Default | Description |
|--------|---------|-------------|
| `REDIRECT_URL` | `/admin/` | URL to redirect to after successful verification |
| `LOGIN_URL` | `/admin/` | URL to Login Admin |
| `ISSUER_NAME` | `Django Admin Example` | Name of the issuer |
| `TOTP_DIGITS` | `6` | Number of digits for the TOTP code |
| `TOTP_STEP` | `30` | Step size in seconds for TOTP code rotation |
| `TOTP_ALGORITHM` | `'sha1'` | Algorithm used for TOTP (`'sha1'`, `'sha256'`, `'sha512'`) |
| `BACKUP_CODES_COUNT` | `10` | Number of backup codes generated |
| `TRUSTED_DEVICE_DAYS` | `30` | Days to trust a device when user selects "Remember this device" |
| `VERIFICATION_TIMEOUT` | `300` |  Default 5 minutes |

---

## 🧪 Testing

Unit test are pending


## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Update code, if needed, as per pre-commit logs
5. Push to the branch: `git push origin feature/my-feature`
6. Open a Pull Request

Please follow PEP8, isort and write tests for any new functionality.

---

## 📬 Support

For questions, bug reports, or feature requests, please open an [issue](https://github.com/SurajPysquad/dj-admin-2fa/issues) on GitHub.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Secure your Django Admin with ease ✨
