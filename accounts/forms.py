from django import forms
from accounts.models import User


class LoginForm(forms.ModelForm):
    """A form for logging in new users. Includes all the required
        fields, plus a repeated password."""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'email',
        ]