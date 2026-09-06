from django.contrib.auth.backends import BaseBackend
from .models import CustomUser

def authenticate(self, request, username=None, password=None):
    try:
        user = CustomUser.objects.get(username=username)
        if user.check_password(password):
            return user
    except CustomUser.DoesNotExist:
        return None

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        return authenticate(request, username=username, password=password)
        