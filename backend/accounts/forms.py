from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User


class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True, help_text="This will be used for login"
    )
    name = forms.CharField(
        max_length=150, required=True, help_text="Your name"
    )
    bankaccount = forms.CharField(
        max_length=20,
        required=False,
        help_text="Bank account number (optional)",
    )

    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "password1",
            "password2",
            "bankaccount",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email address already exists."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # Use email as username
        user.first_name = ""
        user.last_name = self.cleaned_data["name"]
        if commit:
            user.save()
            # Update the account with bankaccount info
            account = user.account
            account.bankaccount = self.cleaned_data.get("bankaccount", "")
            account.save()
        return user


class UserSignInForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
            }
        ),
        help_text="Enter the email address associated with your account.",
    )


class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New password"}
        ),
        label="New password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
            }
        ),
        label="Confirm new password",
    )
