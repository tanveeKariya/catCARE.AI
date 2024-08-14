from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=100)
    username = models.CharField(_('User Name'),unique=True, max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name','last_name','gender','email']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class History(models.Model):
    username = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    machine = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    parameter = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    failure = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username}"

class Recommendation(models.Model):
    component = models.CharField(max_length=100)
    heading1 = models.CharField(max_length=100,null=True,blank=True)
    Recommendations1 = models.CharField(max_length=300,null=True,blank=True)
    heading2 = models.CharField(max_length=100,null=True,blank=True)
    Recommendations2 = models.CharField(max_length=300,null=True,blank=True)
    heading3 = models.CharField(max_length=100,null=True,blank=True)
    Recommendations3 = models.CharField(max_length=300,null=True,blank=True)
    heading4 = models.CharField(max_length=100,null=True,blank=True)
    Recommendations4 = models.CharField(max_length=300,null=True,blank=True)
    heading5 = models.CharField(max_length=100,null=True,blank=True)
    Recommendations5 = models.CharField(max_length=300,null=True,blank=True)

    def __str__(self):
        return f"{self.component}"
