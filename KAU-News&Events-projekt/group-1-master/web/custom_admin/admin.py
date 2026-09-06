from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AdminAuthenticationForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

class MyAdminSite(admin.AdminSite):
    site_header = "KAU N&E Administration"
    site_title = "KARLSTAD"
    
admin_site = MyAdminSite(name="myadmin")

