from django import forms


class TOTPVerificationForm(forms.Form):
    token = forms.CharField(max_length=6, required=True)


class TrustedDeviceForm(forms.Form):
    trust_device = forms.BooleanField(required=False)


class RecoveryCodeForm(forms.Form):
    code = forms.CharField(label="Backup Code", max_length=12)
