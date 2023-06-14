from typing import Any, Dict
from django import forms

from .models import Account


class AccountForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirme password"})
    )

    class Meta:
        model = Account
        fields = ("first_name", "last_name", "email", "password", "phone_number")

    def __init__(self, *args, **kargs):
        super(AccountForm, self).__init__(*args, **kargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter first name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter last name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter email address"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Enter phone number"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super(AccountForm, self).clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]
        if password != confirm_password:
            raise forms.ValidationError("Password does not match!")
