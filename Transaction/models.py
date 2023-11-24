from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from BaseApi.AppEnum import *

class Transaction(models.Model):
    type_de_tontine = models.CharField(max_length=255, choices=[(tag.value, tag.name) for tag in TontineTypeEnum])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    number_payment = models.IntegerField(default=1)
    object = models.PositiveIntegerField()
    id_association = GenericForeignKey('content_type', 'object')
    receiver = models.ForeignKey('Account.Users', on_delete=models.CASCADE, related_name='receiver_transactions')
    receiver_phone = models.CharField(max_length=255)
    send = models.ForeignKey('Account.Users', on_delete=models.CASCADE, related_name='sender_transactions')
    sender_phone = models.CharField(max_length=255)
    amount =  models.DecimalField(max_digits=60, decimal_places=2)
    status = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in StatusTransactionEnum], default=StatusTransactionEnum.PENDING.value)
    payment_date = models.DateTimeField(null=True)
    verification_payment_date = models.DateTimeField(null=True)
    reseau_id_transaction = models.CharField(max_length=255,null=True, unique=True)
    external_id = models.CharField(max_length=255, unique=True, null=True)
    referenceId = models.CharField(max_length=255, unique=True, null=True)
    is_transfert_to_tontinier = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_send = models.BooleanField(default=False)
    receiver_data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

