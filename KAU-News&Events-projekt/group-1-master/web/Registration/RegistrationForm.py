from django import forms
from django.contrib.auth.forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model



class RegistrationForm(UserCreationForm):

    fullname = forms.CharField(max_length=200, required=True)  # Add a name field to the form. Must be filled in
    username = forms.CharField(max_length=150, required=True)  # Add a username field to the form. Must be filled in
    organization = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=15, required=False)  # Add a telephone field to the form. Not mandatory
    role = 3 # Default role is set to Student

    #Meta class to specify to configurate the form/model and fields to be used in the form
    class Meta():
        model =  get_user_model() # Django the form is tied to the User model. ==> The form will generate a new User instance and some field that are default in the User model
        fields = ['fullname', 'email', 'telephone', 'username', 'password1', 'organization'] #Show fields to be included in the form  defined in the RegistrationForm Class
