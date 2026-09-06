from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    global_id = models.AutoField(primary_key=True,unique=True)
    email = models.EmailField(_("email address"), default = '00000',unique=True)
    username = models.CharField(max_length=100 ,default = '00000' ,unique=True) 
    fullname = models.CharField(max_length=100, default = '00000')
    organization = models.CharField(max_length=100, default = False)

    telephone = models.CharField(max_length=15, blank=True, null=True)
    is_staff = models.BooleanField(default=False, verbose_name='is_publisher')
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False, verbose_name='is_admin')
    class Role(models.IntegerChoices):
        ADMIN = 1, 'Admin'
        STAFF = 2, 'Publisher'
        STUDENT = 3, 'User'
    role = models.IntegerField(choices=Role.choices, default=Role.STUDENT) 
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    def clean(self):
        if self.is_superuser and self.role != 1:
            raise ValidationError("Admins must have role 'Admin'")
        if self.role == 1 and self.is_superuser:
            raise ValidationError("Admin must have 'is_admin'")
        if self.is_staff and self.role != 2:
            raise ValidationError("Publisher most have role 'Publisher")
        if self.role == 2 and not self.is_staff:
            raise ValidationError("Publisher must have 'is_publisher'")
        if  (not self.is_superuser or not self.is_staff) and self.role == 1:
            raise ValidationError("Admins must have 'is_admin' and 'is_publisher' true")
    class Meta:
        verbose_name_plural = "users"
        verbose_name = "user"

class Department(models.Model):

    DepID = models.AutoField(primary_key=True,unique=True)
    DepName = models.CharField(max_length=100, default = '00000', verbose_name="Department name")
    staff = models.ManyToManyField(CustomUser,related_name='departments',verbose_name="Publisher",blank=True)

    def __str__(self):
        return self.DepName

class Tag (models.Model):
    TagID = models.AutoField(primary_key=True,unique=True)
    TagName = models.CharField(max_length=100, default = '00000')

    def __str__(self):
        return self.TagName


    