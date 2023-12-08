from django.db import models
from BaseApi.AppEnum import *

class Abonnement(models.Model):
    name = models.CharField(max_length=255)
    sale_price = models.DecimalField(max_digits=60, decimal_places=2)
    can_create_groupe = models.BooleanField()
    can_create_carte = models.BooleanField()
    duration_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class TontinierAbonnement(models.Model):
    abonnement = models.ForeignKey('Abonnement.Abonnement', on_delete=models.CASCADE)
    tontinier =  models.ForeignKey('Account.Users', on_delete=models.CASCADE)
    expired_date = models.DateField(null=True)
    status_abonnement = models.CharField(max_length=50, choices=[(name.value, name.name) for name in StatusAbonnementEnum], default=StatusAbonnementEnum.NO_VALIDATE.value)
    is_default = models.BooleanField(default=True)
    sale_price = models.DecimalField(max_digits=60, decimal_places=2)
    data = models.JSONField()
    transaction_state = models.CharField(max_length=50, default=AbonnementTransactionStatusEnum.NO_PAYE.value, choices=[(name.value, name.name) for name in AbonnementTransactionStatusEnum])
    transaction_status = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in StatusTransactionEnum], null=True)
    reseau_transaction_id = models.CharField(max_length=255, null=True)
    external_id = models.CharField(max_length=255, unique=True, null=True)
    referenceId = models.CharField(max_length=255, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)