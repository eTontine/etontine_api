from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Abonnement.models import Abonnement, TontinierAbonnement
from Abonnement.serializers import *
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from Abonnement.serializers import *
from Account.models import Users
from django.db import transaction
from rest_framework import status
from BaseApi.AppEnum import *
from Transaction.Views.views import *
import json
from Abonnement.Views.Function import *

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def tontinierAbonnements(request, tontinier_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(Users, id=tontinier_id)
    user_abonnements = TontinierAbonnement.objects.filter(tontinier=user).order_by('-created_at')

    if user_abonnements:
        serializer = TontinierAbonnementSerializer(user_abonnements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Aucun abonnement trouvé pour ce tontinier.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET']) 
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def tontinierDefaultAbonnement(request):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    user = request.user
    user_abonnements = TontinierAbonnement.objects.filter(tontinier=user, is_default=True).first()

    if user_abonnements:
        serializer = TontinierAbonnementSerializer(user_abonnements)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Aucun abonnement trouvé.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def abonnements(request):
    try:
        abonnements = Abonnement.objects.all() 
        serializer = AbonnementSerializer(abonnements, many=True)
        return Response(serializer.data)
    except Abonnement.DoesNotExist:
        return Response({'error': 'Abonnement non trouvé'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def abonnement(request, abonnement_id):
    try:
        abonnement = Abonnement.objects.get(id=abonnement_id)
        serializer = AbonnementSerializer(abonnement)
        return Response(serializer.data)
    except Abonnement.DoesNotExist:
        return Response({'error': 'Abonnement non trouvé'}, status=404)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def choiceAbonnement(request):
    tontinier = request.user
    abonnement_id = request.data.get('abonnement')
    user_phone = request.data.get('user_phone')

    if abonnement_id is None or user_phone is None:
        return Response({'message': "Vous devez renseigner l'abonnement et le numéro de téléphone"}, status=status.HTTP_BAD_REQUEST)

    if user_phone != tontinier.phone:
        if userBasicInfoRequest(user_phone) is None:
            return Response({'message': "Ce numéro n'a pas de compte"}, status=status.HTTP_UNPROCESSABLE_ENTITY)

    TontinierAbonnement.objects.filter(tontinier=tontinier, is_default=True).update(is_default=False, status_abonnement=StatusAbonnementEnum.FINISH.value)
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    tontinier_abonnement = TontinierAbonnement.objects.create(
        tontinier=tontinier,
        abonnement=abonnement,
        status_abonnement=StatusAbonnementEnum.NO_VALIDATE.value,
        sale_price=abonnement.sale_price,
        data={
            'name': abonnement.name,
            'can_create_groupe': abonnement.can_create_groupe,
            'can_create_carte': abonnement.can_create_carte,
        },
        is_default=True,
        transaction_state=AbonnementTransactionStatusEnum.NO_PAYE.value,
        transaction_status = StatusTransactionEnum.PENDING.value,
    )
    
    tontinier_abonnement.save()
    setUserStatus(tontinier.id)
    abonnementTransactionStatus, abonnementTransaction = sendAbonnementTransaction(tontinier_abonnement.id, user_phone, abonnement.sale_price)
    tontinier_abonnement_serializer = TontinierAbonnementSerializer(TontinierAbonnement.objects.get(id=tontinier_abonnement.id))
    
    return Response({'message': "Abonnement choisi avec succès", 'transaction': abonnementTransaction, 'tontinier_abonnement': tontinier_abonnement_serializer.data}, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def setDefaultAbonnement(request, tontinier_abonnement_id):
    tontinier = request.user.id
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    TontinierAbonnement.objects.filter(tontinier=tontinier, is_default=True).update(is_default=False, status_abonnement=StatusAbonnementEnum.FINISH.value)
    tontinier_abonnement = get_object_or_404(TontinierAbonnement, id=tontinier_abonnement_id)
    tontinier_abonnement.is_default = True
    tontinier_abonnement.status_abonnement = StatusAbonnementEnum.IN_PROGRESS.value
    tontinier_abonnement.save()