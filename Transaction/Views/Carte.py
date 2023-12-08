from datetime import datetime, timedelta
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Transaction.models import Transaction
from BaseApi.AppEnum import *
from Transaction.Requests.General import *
from Transaction.Requests.Payment import *
from Tontine.models import Associate_carte, Cartes
from Tontine.serializers import CartesSerializer
from dateutil.relativedelta import relativedelta
from Transaction.Cron.Cron import *
import pytz
from Transaction.Views.views import *
from django.db.models import Sum
from Transaction.serializers import TransactionSerializer
from Account.models import Users

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getCartePaymentDetails(request):
    data = request.data
    object_id = data['object_id']
    number_payment = data['number_payment']
    sender_phone = data['send_phone']

    associateCarte = get_object_or_404(Associate_carte, id=object_id)
    amount = associateCarte.carte.amount
    espected_number = associateCarte.carte.number_day
    
    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre associate carte'}, status=400)
    if not number_payment or number_payment < 1:
        return Response({'message': 'Vous devez fournir le nombre de paiement et vérifier qu\'il est supérieur à 0'}, status=400)
    if associateCarte.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    if associateCarte.transaction_status != StatusTransactionEnum.SUCCESSFUL.value:
        return Response({'message': 'La carte n\'est pas encore payée'}, status=400)    
    if sender_phone is None:
        return Response({'message': 'Vous devez fournir le numéro de téléphone de l\'utilisateur'}, status=400)
    
    totalPay = Transaction.objects.filter(type_de_tontine=TontineTypeEnum.CARTE.value, object=associateCarte.id, status=StatusTransactionEnum.SUCCESSFUL.value).aggregate(Sum('number_payment'))['number_payment__sum']
    if totalPay is None:
        totalPay = 0
    totaux = totalPay + number_payment
    if espected_number < totaux:
        numberRest = espected_number - totalPay
        return Response({'message': f'Il ne vous reste que {numberRest} jours à payer '}, status=400)

    totalAmount = amount * number_payment

    responseData = {
        'totalAmount': totalAmount,
        'amount': amount,
        'number_payment': number_payment,
        'sender_phone': sender_phone,
        'carte_name': associateCarte.carte.name,
        'tontinier': associateCarte.carte.tontinier.name,
        'total_pay': totalPay,
        'total_expected': espected_number
    }
    return Response({'data': responseData})
    

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def addCarteAssociateTransaction(request):
    data = request.data
    object_id = data['object_id']
    number_payment = data['number_payment']
    content_type = ContentType.objects.get_for_model(Associate_carte)
    associateCarte = get_object_or_404(Associate_carte, id=object_id)
    amount = associateCarte.carte.amount
    receiver = associateCarte.carte.tontinier
    receiver_phone = associateCarte.carte.tontinier.phone
    espected_number = associateCarte.carte.number_day
    send = request.user
    sender_phone = data['send_phone']

    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre associate carte'}, status=400)
    if not number_payment or number_payment < 1:
        return Response({'message': 'Vous devez fournir le nombre de paiement et vérifier qu\'il est supérieur à 0'}, status=400)
    if associateCarte.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    if associateCarte.transaction_status != StatusTransactionEnum.SUCCESSFUL.value:
        return Response({'message': 'La carte n\'est pas encore payée'}, status=400)
    if sender_phone is None:
        return Response({'message': 'Vous devez fournir le numéro de téléphone de l\'utilisateur'}, status=400)

    totalPay = Transaction.objects.filter(type_de_tontine=TontineTypeEnum.CARTE.value, object=associateCarte.id, status=StatusTransactionEnum.SUCCESSFUL.value).aggregate(Sum('number_payment'))['number_payment__sum']
    if totalPay is None:
        totalPay = 0
    totaux = totalPay+number_payment
    if espected_number < totaux:
        numberRest = espected_number - totalPay
        return Response({'message': f'Il ne vous reste que {numberRest} jours à payer '}, status=400)

    totalAmount = float(amount) * float(number_payment)
    current_date = datetime.now()
    
    transaction = Transaction.objects.create(
        amount=totalAmount,
        receiver=receiver,
        receiver_phone=receiver_phone,
        send=send,
        sender_phone=sender_phone,
        payment_date=current_date,
        content_type=content_type,
        object=object_id,
        type_de_tontine=TontineTypeEnum.CARTE.value,
        number_payment=number_payment,
        status=StatusTransactionEnum.PENDING.value,
        id_association=associateCarte,
    )
    sendCarteTransaction(transaction.id, sender_phone)
    return Response({'message': 'Paiment carte envoyé avec succès et en attente de confirmation'})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def makeCarteCollectRequest(request):
    data = request.data
    object_id = data['object_id']
    content_type = ContentType.objects.get_for_model(Associate_carte)
    associateCarte = get_object_or_404(Associate_carte, id=object_id)
    receiver = associateCarte.user
    receiver_phone = data['receiver_phone']
    send = associateCarte.carte.tontinier
    sender_phone = associateCarte.carte.tontinier.phone

    totalPay = Transaction.objects.filter(type_de_tontine=TontineTypeEnum.CARTE.value, object=associateCarte.id, status=StatusTransactionEnum.SUCCESSFUL.value).aggregate(Sum('number_payment'))['number_payment__sum']
    if totalPay is None:
        totalPay = 0
    
    if totalPay == 0:
        return Response({'message': 'Vous n\'avez pas encore payé'}, status=400)

    amount = float(associateCarte.carte.amount) * float(totalPay) - float(associateCarte.carte.gain)

    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre carte'}, status=400)
    if not receiver_phone:
        return Response({'message': 'Vous devez fournir le numéro de téléphone du destinataire'}, status=400)
    if associateCarte.transaction_status != StatusTransactionEnum.SUCCESSFUL.value:
        return Response({'message': 'La carte n\'est pas encore payée'}, status=400)
    if associateCarte.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    
    _transaction = Transaction.objects.filter(object=associateCarte.id, type_transaction=TypeTransactionEnum.COLLECTED.value).first()

    if _transaction is not None:
        if _transaction.status == StatusTransactionEnum.SUCCESSFUL.value:
            return Response({'message': 'Vous avez déjà collecté la carte'}, status=400)
        return Response({'message': 'Vous avez déjà effectué une demande de collecte'}, status=400)
    
    transaction = Transaction.objects.create(
        amount=amount,
        receiver=receiver,
        receiver_phone=receiver_phone,
        send=send,
        sender_phone=sender_phone,
        payment_date=datetime.now(),
        content_type=content_type,
        object=object_id,
        type_de_tontine=TontineTypeEnum.CARTE.value,
        type_transaction=TypeTransactionEnum.COLLECTED.value,
        status=StatusTransactionEnum.PENDING.value,
        id_association=associateCarte,
    )
    associateCarte.status = StatusTontinierEnum.REQUEST_SENT.value
    associateCarte.save()

    return Response({'message': 'Demande de collecte envoyé avec succès et en attente de validation'})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def sendCarteCollectTransaction(request):
    data = request.data
    object_id = data['object_id']
    content_type = ContentType.objects.get_for_model(Associate_carte)
    associateCarte = get_object_or_404(Associate_carte, id=object_id)
    receiver = associateCarte.user
    receiver_phone = associateCarte.user.phone
    send = associateCarte.carte.tontinier
    sender_phone = data['sender_phone']

    totalPay = Transaction.objects.filter(type_de_tontine=TontineTypeEnum.CARTE.value, object=associateCarte.id, status=StatusTransactionEnum.SUCCESSFUL.value).aggregate(Sum('number_payment'))['number_payment__sum']
    if totalPay is None:
        totalPay = 0
    
    if totalPay == 0:
        return Response({'message': 'Aucun payment effectué sur la carte'}, status=400)
    amount = float(associateCarte.carte.amount) * float(totalPay) - float(associateCarte.carte.gain)

    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre carte'}, status=400)
    if not sender_phone:
        return Response({'message': 'Vous devez fournir votre numéro de téléphone '}, status=400)
    if associateCarte.transaction_status != StatusTransactionEnum.SUCCESSFUL.value:
        return Response({'message': 'La carte n\'est pas encore payée'}, status=400)
    if associateCarte.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    
    _transaction = Transaction.objects.filter(object=associateCarte.id, type_transaction=TypeTransactionEnum.COLLECTED.value).first()

    if _transaction is not None:
        if _transaction.status == StatusTransactionEnum.SUCCESSFUL.value:
            return Response({'message': 'La carte a déjà été collecté'}, status=400)
        _transaction.delete()
    
    transaction = Transaction.objects.create(
        amount=amount,
        receiver=receiver,
        receiver_phone=receiver_phone,
        send=send,
        sender_phone=sender_phone,
        payment_date=datetime.now(),
        content_type=content_type,
        object=object_id,
        type_de_tontine=TontineTypeEnum.CARTE.value,
        type_transaction=TypeTransactionEnum.COLLECTED.value,
        status=StatusTransactionEnum.PENDING.value,
        id_association=associateCarte,
    )
    associateCarte.status = StatusTontinierEnum.REQUEST_IN_PROGRESS.value
    associateCarte.save()
    sendCarteTransaction(transaction.id, sender_phone)
    return Response({'message': 'Demande de collecte envoyé avec succès et en attente de validation'})

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def validateCarteCollectRequest(request, transaction_id):
    data = request.data
    sender_phone = data['sender_phone']
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if transaction.status == StatusTransactionEnum.SUCCESSFUL.value:
        return Response({'message': 'Vous avez déjà validé la demande de collecte'}, status=400)
    if transaction.type_transaction != TypeTransactionEnum.COLLECTED.value:
        return Response({'message': 'Vous ne pouvez valider que des demandes de collecte'}, status=400)
    if transaction.status!= StatusTransactionEnum.PENDING.value:
        return Response({'message': 'Vous ne pouvez valider que des demandes en attente'}, status=400)
    if sender_phone is None:
        return Response({'message': 'Vous ne pouvez fournir votre numéro de transaction'}, status=400)

    transaction.sender_phone = sender_phone
    transaction.save()
    sendCarteTransaction(transaction.id, sender_phone)
    associateCarte = transaction.id_association
    associateCarte.status = StatusTontinierEnum.REQUEST_IN_PROGRESS.value
    associateCarte.save()
    return Response({'message': 'Demande de collecte validé avec succès'})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getCarteCollectRequest(request, tontinier_id):
    tontinier = get_object_or_404(Users, id=tontinier_id)
    transactions = Transaction.objects.filter(type_transaction=TypeTransactionEnum.COLLECTED.value, status=StatusTransactionEnum.PENDING.value, type_de_tontine=TontineTypeEnum.CARTE.value, send=tontinier)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)