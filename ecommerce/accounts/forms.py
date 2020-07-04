from django import forms
from django.forms import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class GuestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={
            "class": "form-control",
            "placeholder": "abc@example.com"
        })
    )


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(
            attrs={
                "class": "form_control",
                "placeholder": "Your first name"
                })
            )
    last_name = forms.CharField(widget=forms.TextInput(
            attrs={
                "class": "form_control",
                "placeholder": "Your last name"
                })
            )
    email = forms.EmailField(widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "abc@example.com"
                })
            )
    username = forms.CharField(widget=forms.TextInput(
            attrs={
                    "class": "form-control",
                    "placeholder": "Your username"
                })
            )
    password = forms.CharField(widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your password"
                })
            )
    confirm_password = forms.CharField(widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Write password again"
                })
            )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise ValidationError("username has been taken. Kindly choose new one")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise ValidationError("email has been taken. Kindly choose new one")
        return email

    def clean(self):
        form_data = self.cleaned_data
        if form_data.get("password") != form_data.get("confirm_password"):
            raise ValidationError("Password must match.")
        del form_data["confirm_password"]
        return form_data
