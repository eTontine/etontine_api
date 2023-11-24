from django.db import models
from BaseApi.AppEnum import *

class Rules(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    online = models.BooleanField(default=False)
    type = models.CharField(max_length=255, choices=[(name.value, name.name) for name in TypeRuleEnum])
    key = models.CharField(max_length=255, null=True, unique=True)
    field_type = models.CharField(max_length=255, choices=[('TEXT', 'Text'), ('NUMBER', 'Number'), ('DATE', 'Date'), ('TIME', 'Time'), ('DATETIME', 'Datetime'), ('SELECT', 'Select'), ('CHECKBOX', 'Checkbox'), ('RADIO', 'Radio'), ('FILE', 'File'), ('IMAGE', 'Image'), ('URL', 'Url')])
    default_value = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def serialize(self, *args, **kwargs):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'online': self.online,
            'type': self.type,
            'field_type': self.field_type,
            'default_value': self.default_value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Rule_values(models.Model):
    rule = models.ForeignKey('TontineRule.Rules', on_delete=models.CASCADE)
    value = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, choices=[(TypeRuleEnum.CARTES.value, TypeRuleEnum.CARTES.name), (TypeRuleEnum.GROUPES.value, TypeRuleEnum.GROUPES.name)])
    carte_or_groupe_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def serialize(self, *args, **kwargs):
        return {
            'id': self.id,
            'rule': self.rule.serialize(),
            'value': self.value,
            'type': self.type,
            'carte_or_groupe_id': self.carte_or_groupe_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }