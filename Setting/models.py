from django.db import models

class Setting(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)