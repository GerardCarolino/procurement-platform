from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class VendorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    organization = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'organization', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.VENDOR
        user.is_verified = False  # requires admin approval
        user.email = self.cleaned_data['email']
        user.organization = self.cleaned_data['organization']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)