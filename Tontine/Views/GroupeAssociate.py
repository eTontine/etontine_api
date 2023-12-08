from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
from BaseApi.AppEnum import *
from Abonnement.Views.Function import * 
from Tontine.models import Groupes, Groupe_associate
from Tontine.serializers import Groupe_associateSerializer, Groupe_associateSerializerAdd, GroupesSerializer
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from Tontine.models import PaymentPeriod
from Transaction.Views.views import getGroupePenality
from Transaction.models import Transaction
from Transaction.serializers import TransactionSerializer
from Account.models import Users

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def addUserInGroupe(request):
    data = request.data
    groupeId = data.get('groupe')
    user_phones = data.get('user_phones')

    if groupeId is None or user_phones is None or len(user_phones) == 0:
        return Response({'error': "Veuillez remplir tous les champs obligatoires"}, status=status.HTTP_400_BAD_REQUEST)
    
    groupe = get_object_or_404(Groupes, id=groupeId)
    if groupe.status != StatusGroupeEnum.INSCRIPTION.value:
        return Response({'error': "Le groupe est fermé ou la phase d'inscription est terminée"}, status=status.HTTP_400_BAD_REQUEST)
    
    dataSerializers = []
    for user_phone in user_phones:
        user = Users.objects.filter(phone=user_phone).first()
        if user:
            data['groupe'] = groupe.id
            data['user'] = user.id
            data['invitation_status'] = InvitationStatusEnum.PENDING.value

            dataSerializer = Groupe_associateSerializerAdd(data=data)
            if dataSerializer.is_valid():
                dataSerializer.save()
                dataSerializers.append(dataSerializer.data)
        else:
            dataSerializers.append({'user': user_phone, 'error': "L'utilisateur n'existe pas"})
    return Response(dataSerializers, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def validateOrRejectGroupeInvitation(request, groupe_associate_id):
    groupeAssociate = get_object_or_404(Groupe_associate, id=groupe_associate_id)

    if request.user.id != groupeAssociate.user.id:
        return Response({'error': "Vous n'avez pas les droits pour valider cette invitation"}, status=status.HTTP_400_BAD_REQUEST)
    
    new_status = request.data.get('status')
    if new_status is None:
        return Response({'message': "Veuillez entrer un status"}, status=status.HTTP_400_BAD_REQUEST)
    if new_status not in [InvitationStatusEnum.ACCEPTED.value, InvitationStatusEnum.REJECTED.value, InvitationStatusEnum.CANCELLED.value]:
        return Response({'message': "Veuillez entrer un status valide"}, status=status.HTTP_400_BAD_REQUEST)

    if groupeAssociate.groupe.status != StatusGroupeEnum.INSCRIPTION.value:
        return Response({'message': "Le groupe est fermé ou la phase d'inscription est terminée"}, status=status.HTTP_400_BAD_REQUEST)

    if groupeAssociate.invitation_status == InvitationStatusEnum.ACCEPTED.value:
        return Response({'message': "Vous avez déjà accepté cette invitation"}, status=status.HTTP_400_BAD_REQUEST)
    if groupeAssociate.invitation_status == InvitationStatusEnum.REJECTED.value:
        return Response({'message': "Vous avez déjà refusé cette invitation"}, status=status.HTTP_400_BAD_REQUEST)
    if groupeAssociate.invitation_status == InvitationStatusEnum.CANCELLED.value:
        return Response({'message': "Vous avez déjà annulé cette invitation"}, status=status.HTTP_400_BAD_REQUEST)

    groupeAssociate.invitation_status = new_status
    groupeAssociate.save()
    return Response({'message': 'Invitation acceptée avec succès'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getGroupeAssociate(request, groupe_associate_id):
    groupeAssociate = get_object_or_404(Groupe_associate, id=groupe_associate_id)
    paymentPeriods = []
    transactionDatas = []
    periodPaymentRequest = PaymentPeriod.objects.filter(groupe_associate=groupeAssociate)
    if periodPaymentRequest.exists():
        for period in periodPaymentRequest:
            amount = groupeAssociate.groupe.amount
            penality_value = 0
            if period.is_pay_penality == True:
                penality_value = getGroupePenality(groupeAssociate.groupe.id)
                amout += penality_value
            paymentPeriods.append({
                'period_id': period.id,
                'amount': amount,
                'is_pay_penality': period.is_pay_penality,
                'penality_value': penality_value,
                'payment_date': period.payment_date,
                'status': period.status,
            })

    filters = Q(object=groupeAssociate.id)
    
    transactionRequest = Transaction.objects.filter(filters)
    if transactionRequest.exists():
        for transaction in transactionRequest:
            transactionSerializer = TransactionSerializer(transaction)
            transactionDatas.append(transactionSerializer.data)

    dataSerializer = Groupe_associateSerializer(groupeAssociate)
    return Response({'data': dataSerializer.data, 'payment_periods': paymentPeriods, 'transactions': transactionDatas}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getAssociateGroupes(request):
    # Filtres de recherche
    amount = request.query_params.get('amount')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    tontinier = request.query_params.get('tontinier')
    user = request.query_params.get('user')
    status = request.query_params.get('status')
    invitation_status = request.query_params.get('invitation_status')
    search = request.query_params.get('search')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('limit')

    # Filtres de base
    filters = Q()

    if amount:
        filters &= Q(groupe__amount=amount)
    if start_date:
        filters &= Q(created_at__gte=start_date)
    if end_date:
        filters &= Q(created_at__lte=end_date)
    if tontinier:
        filters &= Q(groupe__tontinier=tontinier)
    if user:
        filters &= Q(user=user)
    if status:
        filters &= Q(status=status)
    if invitation_status:
        filters &= Q(invitation_status=invitation_status)
    if search:
        filters &= (
            Q(groupe__name__icontains=search) |
            Q(user__name__icontains=search) |
            Q(collection_date__icontains=search)
        )

    associate_groupes = Groupe_associate.objects.filter(filters)
    if page_size is None or page_size == "":
        serializer = Groupe_associateSerializer(associate_groupes, many=True)
        return Response({'data': serializer.data}, status=200)

    paginator = Paginator(associate_groupes, page_size)
    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    serializer = Groupe_associateSerializer(paginated_data, many=True)
    response_data = {
        'total_pages': paginator.num_pages,
        'current_page': paginated_data.number,
        'total_items': paginator.count,
        'data': serializer.data
    }
    return Response(response_data, status=200)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getGroupeAssociateToUser(request, user_id):
    user = get_object_or_404(Users, id=user_id)
    search = request.query_params.get('search')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('limit')
    groupes = []
    filters = Q(user=user)
    if search:
        filters &= (
            Q(groupe__name__icontains=search) 
        )
    groupeAssociates = Groupe_associate.objects.filter(filters)

    if groupeAssociates.exists():
        for groupeAssociate in groupeAssociates:
            groupe = groupeAssociate.groupe
            if groupe not in groupes:
                groupes.append(groupe)

    if page_size is None or page_size == "":
        serializer = GroupesSerializer(groupes, many=True)
        return Response({'data': serializer.data}, status=200)

    paginator = Paginator(groupes, page_size)
    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)
    
    serializer = GroupesSerializer(paginated_data, many=True)
    response_data = {
        'total_pages': paginator.num_pages,
        'current_page': paginated_data.number,
        'total_items': paginator.count,
        'data': serializer.data
    }