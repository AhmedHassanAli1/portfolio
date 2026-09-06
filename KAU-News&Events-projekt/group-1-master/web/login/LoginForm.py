from django import forms
from django.contrib.auth.forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


class loginForm(AuthenticationForm) :
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
