from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from BaseApi.AppEnum import *

class Countries(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    phone_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Users(AbstractBaseUser):
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    country = models.ForeignKey('Account.Countries', on_delete=models.CASCADE, null=True)
    account_type = models.CharField(max_length=20, choices=[(name.value, name.name) for name in AccountTypeEnum])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'phone'