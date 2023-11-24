from datetime import datetime, timedelta
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from Transaction.models import Transaction
from Abonnement.models import TontinierAbonnement
from BaseApi.AppEnum import *
from Transaction.Requests.General import *
from Transaction.Requests.Payment import *
from Tontine.models import Associate_carte
from Transaction.Cron.Cron import *
from Transaction.Cron.StartCron import *

def sendAbonnementTransaction(tontinier_abonnement, user_phone, amount):
    with transaction.atomic():
        external_id = getExternalIdUnique()
        referentId = getUniqueReferenceUuid()
        tontinier_abonnement = TontinierAbonnement.objects.get(id=tontinier_abonnement)
        amount = float(amount)
        payment_status, response = makePaymentRequest(user_phone, amount, f"Abonnement {tontinier_abonnement.abonnement.name} - Amount: {tontinier_abonnement.sale_price} - Phone: {user_phone}", external_id, referentId)
        if payment_status:
            tontinier_abonnement.transaction_status = StatusTransactionEnum.PENDING.value
            tontinier_abonnement.external_id = external_id
            tontinier_abonnement.referenceId = referentId
            tontinier_abonnement.save()
            return True, response
        else:
            tontinier_abonnement.transaction_status = StatusTransactionEnum.UNKNOWN.value
            tontinier_abonnement.save()
            return False, response
    return True

def sendCarteBuyTransaction(carte_associate, user_phone):
    with transaction.atomic():
        external_id = getExternalIdUnique()
        referentId = getUniqueReferenceUuid()
        carte_associate = Associate_carte.objects.get(id=carte_associate)
        amount = float(carte_associate.carte.sale_price)
        payment_status, response = makePaymentRequest(user_phone, amount, f"Achat carte: {carte_associate.carte.name} - Amount: {carte_associate.carte.sale_price} - Phone: {user_phone}", external_id, referentId)
        if payment_status:
            if carte_associate.transaction_status == StatusTransactionEnum.SUCCESSFUL.value:
                pass
            else:
                carte_associate.transaction_status = StatusTransactionEnum.PENDING.value
            carte_associate.external_id = external_id
            carte_associate.referenceId = referentId
            carte_associate.save()
            return True, response
        else:
            carte_associate.transaction_status = StatusTransactionEnum.UNKNOWN.value
            carte_associate.save()
            return False, response
    return True

def sendCarteParticipationTransaction(transaction_id, sender_phone):
    with transaction.atomic():
        external_id = getExternalIdUnique()
        referentId = getUniqueReferenceUuid()
        transaction_data = Transaction.objects.get(id=transaction_id)
        amount = transaction_data.amount
        amount = float(amount)
        payment_status, response = makePaymentRequest(sender_phone, amount, f"Paiement carte - Amount: {amount} - Phone: {sender_phone}", external_id, referentId)
        if payment_status:
            transaction_data.transaction_status = StatusTransactionEnum.PENDING.value
            transaction_data.external_id = external_id
            transaction_data.referenceId = referentId
            transaction_data.save()
            return True, response
        else:
            transaction_data.transaction_status = StatusTransactionEnum.UNKNOWN.value
            transaction_data.save()
            return False, response
    return True

def sendGroupeTransactionParticipation(transaction_id, sender_phone):
    with transaction.atomic():
        external_id = getExternalIdUnique()
        referentId = getUniqueReferenceUuid()
        transaction_data = Transaction.objects.get(id=transaction_id)
        amount = transaction_data.amount
        amount = float(amount)
        payment_status, response = makePaymentRequest(sender_phone, amount, f"Participation  Tontine - Amount: {amount} - Phone: {sender_phone}", external_id, referentId)
        if payment_status:
            transaction_data.transaction_status = StatusTransactionEnum.PENDING.value
            transaction_data.external_id = external_id
            transaction_data.referenceId = referentId
            transaction_data.save()
            return True, response
        else:
            transaction_data.transaction_status = StatusTransactionEnum.UNKNOWN.value
            transaction_data.save()
            return False, response
    return True

def mobilWalletUser(user_phone):
    data = userBasicInfoRequest(user_phone)
    if data:
        return data.json()
    return None

@api_view(['GET'])
@permission_classes([AllowAny])
def testApiMomo(request, phone):    
    data = userBasicInfoRequest(phone)
    if data:
        return Response({'data': data.json()})
    else: 
        return Response({'data': data})

@api_view(['GET'])
@permission_classes([AllowAny])
def launchCron(request):
    data = startCron()
    return Response({'message': data})