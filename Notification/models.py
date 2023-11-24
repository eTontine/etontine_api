from django.db import models
from BaseApi.AppEnum import *

class Notifications(models.Model):
    receiver = models.ForeignKey('Account.Users', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in NotificationType])
    is_see = models.BooleanField(default=False)
    is_send = models.BooleanField(default=False)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)