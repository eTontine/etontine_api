from django.db import models
from BaseApi.AppEnum import *

class Cartes(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    number_day = models.IntegerField()
    gain = models.DecimalField(max_digits=10, decimal_places=2)
    online = models.BooleanField(default=True)
    tontinier =  models.ForeignKey('Account.Users', on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Associate_carte(models.Model):
    carte = models.ForeignKey('Tontine.Cartes', on_delete=models.CASCADE)
    user = models.ForeignKey('Account.Users', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[(name.value, name.name) for name in StatusTontinierEnum], default=StatusTontinierEnum.NOT_COLLECTED.value)
    collection_date = models.DateTimeField(null=True)
    invitation_status = models.CharField(max_length=20, choices=[(name.value, name.name) for name in InvitationStatusEnum], default=InvitationStatusEnum.PENDING.value)

    transaction_status = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in StatusTransactionEnum], null=True)
    reseau_transaction_id = models.CharField(max_length=255, null=True)
    external_id = models.CharField(max_length=255, unique=True, null=True)
    referenceId = models.CharField(max_length=255, unique=True, null=True)
    data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Groupes(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[(name.value, name.name) for name in StatusGroupeEnum], default=StatusGroupeEnum.INSCRIPTION.value)
    start_date = models.DateTimeField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gain = models.DecimalField(max_digits=10, decimal_places=2)
    descriptions = models.TextField(null=True)
    contribution_period = models.CharField(max_length=10, choices=[(tag.value, tag.name) for tag in Period])
    time_contribution = models.TimeField(default="10:00")
    day_contribution = models.CharField(max_length=20, choices=[(day.name, day.value['fr']) for day in daysEnum])
    tontinier =  models.ForeignKey('Account.Users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Groupe_associate(models.Model):
    groupe = models.ForeignKey('Tontine.Groupes', on_delete=models.CASCADE)
    user = models.ForeignKey('Account.Users', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[(name.value, name.name) for name in StatusTontinierEnum], default=StatusTontinierEnum.NOT_COLLECTED.value)
    invitation_status = models.CharField(max_length=20, choices=[(name.value, name.name) for name in InvitationStatusEnum], default=InvitationStatusEnum.PENDING.value)
    collection_date = models.DateTimeField(null=True)
    position = models.IntegerField(default=0)
    date_collect = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentPeriod(models.Model):
    groupe_associate = models.ForeignKey('Tontine.Groupe_associate', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    payment_date = models.DateTimeField()
    is_pay_penality = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)