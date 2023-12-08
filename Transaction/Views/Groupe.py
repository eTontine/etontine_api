from datetime import datetime, timedelta, timezone
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
from Tontine.models import Groupe_associate, Groupes, PaymentPeriod
from Tontine.serializers import GroupesSerializer
from dateutil.relativedelta import relativedelta
from Transaction.Cron.Cron import *
import pytz
from Transaction.Views.views import *
from TontineRule.models import Rule_values
from Tontine.serializers import Groupe_associateSerializer
from Account.models import Users

def getGroupePenality(groupe_id):
    pernality_value = Rule_values.objects.filter(carte_or_groupe_id=groupe_id, type=TypeRuleEnum.GROUPES.value, rule__key='PENALITY_PAYMENT').first()
    if pernality_value:
        return pernality_value.value
    return 0

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getPaymentDetails(request):
    data = request.data
    object_id = data['object_id']
    number_payment = data['number_payment']
    sender_phone = data['send_phone']
    paymentDate = data['payment_date']

    associateGroupe = get_object_or_404(Groupe_associate, id=object_id)
    amount = associateGroupe.groupe.amount
    
    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre associate groupe'}, status=400)
    if not number_payment or number_payment < 1:
        return Response({'message': 'Vous devez fournir le nombre de paiement et vérifier qu\'il est supérieur à 0'}, status=400)
    if associateGroupe.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    if sender_phone is None:
        return Response({'message': 'Vous devez fournir le numéro de téléphone de l\'utilisateur'}, status=400)
    if associateGroupe.groupe.status != StatusGroupeEnum.IN_PROGRESS.value:
        return Response({'message': 'Le groupe n\'est pas encore lancé'}, status=400)
    if paymentDate is None:
        return Response({'message': 'Vous devez fournir la date de paiement'}, status=400)
    

    paymentDates = PaymentPeriod.objects.filter(groupe_associate=associateGroupe.id, status=False).order_by('payment_date')[:number_payment]
    if len(paymentDates) < number_payment:
        return Response({'message': 'Vous devez fournir au moins'+ str(len(paymentDates)) +'paiements'}, status=400)

    penalityValue = getGroupePenality(associateGroupe.groupe.id)
    totalAmount = amount * number_payment
    current_date = datetime.now(timezone.utc)
    responseData = []

    for paymentDate in paymentDates:
        penality = 0
        date_string = str(paymentDate.payment_date)
        payment_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S%z')
        if payment_date < current_date:
            totalAmount += penalityValue
            penality = penalityValue
        responseData.append({
            'payment_date': paymentDate.payment_date,
            'amount': amount,
            'penality': penality,
        })
    return Response({'data': responseData, 'total_amount': totalAmount, 'groupe_name': associateGroupe.groupe.name, 'tontinier': associateGroupe.groupe.tontinier.name})
    

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def addGroupeAssociateTransaction(request):
    data = request.data
    object_id = data['object_id']
    type_de_tontine = TontineTypeEnum.GROUPE.value
    number_payment = data['number_payment']
    content_type = ContentType.objects.get_for_model(Groupe_associate)
    associateGroupe = get_object_or_404(Groupe_associate, id=object_id)
    amount = associateGroupe.groupe.amount
    receiver = associateGroupe.groupe.tontinier
    receiver_phone = associateGroupe.groupe.tontinier.phone
    send = request.user
    sender_phone = data['send_phone']
    paymentDate = data['payment_date']
    verification_payment_date = data['payment_date']

    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre associate groupe'}, status=400)
    if not number_payment or number_payment < 1:
        return Response({'message': 'Vous devez fournir le nombre de paiement et vérifier qu\'il est supérieur à 0'}, status=400)
    if associateGroupe.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    if sender_phone is None:
        return Response({'message': 'Vous devez fournir le numéro de téléphone de l\'utilisateur'}, status=400)
    if associateGroupe.groupe.status != StatusGroupeEnum.IN_PROGRESS.value:
        return Response({'message': 'Le groupe n\'est pas encore lancé'}, status=400)
    if paymentDate is None:
        return Response({'message': 'Vous devez fournir la date de paiement'}, status=400)

    paymentDates = PaymentPeriod.objects.filter(groupe_associate=associateGroupe.id, status=False, payment_date__gte=paymentDate).order_by('payment_date')[:number_payment]

    if len(paymentDates) < number_payment:
        return Response({'message': 'Vous devez fournir au moins'+ str(len(paymentDates)) +'paiements'}, status=400)
    
    penalityValue = getGroupePenality(associateGroupe.groupe.id)

    totalAmount = float(amount) * float(number_payment)
    current_date = datetime.now(timezone.utc)

    for paymentDate in paymentDates:
        date_string = str(paymentDate.payment_date)
        payment_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S%z')
        if payment_date < current_date:
            totalAmount += float(penalityValue)
    
    transaction = Transaction.objects.create(
        amount=totalAmount,
        receiver=receiver,
        receiver_phone=receiver_phone,
        send=send,
        sender_phone=sender_phone,
        payment_date=current_date,
        verification_payment_date = verification_payment_date,
        content_type=content_type,
        object=object_id,
        type_de_tontine=TontineTypeEnum.GROUPE.value,
        number_payment=number_payment,
        status=StatusTransactionEnum.PENDING.value,
        id_association=associateGroupe,
    )
    sendGroupeTransaction(transaction.id, sender_phone)
    return Response({'message': 'Participation tontine envoyée avec succès et encore en attente de paiement'})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def sendGroupeCollectTransaction(request):
    data = request.data
    object_id = data['object_id']
    content_type = ContentType.objects.get_for_model(Groupe_associate)
    groupeAssoociate = get_object_or_404(Groupe_associate, id=object_id)
    numberNumber = Groupe_associate.objects.filter(groupe=groupeAssoociate.groupe, invitation_status=InvitationStatusEnum.ACCEPTED.value).count()
    amount = float(groupeAssoociate.groupe.amount) * float(numberNumber) - float(groupeAssoociate.groupe.gain) 
    receiver = groupeAssoociate.user
    receiver_phone = groupeAssoociate.user.phone
    send = groupeAssoociate.groupe.tontinier
    sender_phone = data['sender_phone']

    if not object_id:
        return Response({'message': 'Vous devez fournir l\'id de votre groupe associer'}, status=400)
    if not sender_phone:
        return Response({'message': 'Vous devez fournir votre numéro de téléphone '}, status=400)
    if groupeAssoociate.invitation_status != InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': 'L\'invitation n\'est pas acceptée'}, status=400)
    
    _transaction = Transaction.objects.filter(object=groupeAssoociate.id, type_transaction=TypeTransactionEnum.COLLECTED.value).first()

    if _transaction is not None:
        if _transaction.status == StatusTransactionEnum.SUCCESSFUL.value:
            return Response({'message': 'Collecte déjà effectuée'}, status=400)
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
        type_de_tontine=TontineTypeEnum.GROUPE.value,
        type_transaction=TypeTransactionEnum.COLLECTED.value,
        status=StatusTransactionEnum.PENDING.value,
        id_association=groupeAssoociate,
    )
    groupeAssoociate.status = StatusTontinierEnum.REQUEST_IN_PROGRESS.value
    groupeAssoociate.save()
    sendGroupeTransaction(transaction.id, sender_phone)
    return Response({'message': 'Demande de collecte envoyé avec succès et en attente de validation'})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getGroupeCollectNoMake(request, tontinier_id):
    tontinier = get_object_or_404(Users, id=tontinier_id)
    filters = Q(status=StatusTontinierEnum.NOT_COLLECTED.value) & Q(groupe__tontinier=tontinier) & Q(groupe__status=StatusGroupeEnum.IN_PROGRESS.value) & Q(date_collect__lte=datetime.now())
    serializers = Groupe_associateSerializer(Groupe_associate.objects.filter(filters), many=True)
    return Response(serializers.data)