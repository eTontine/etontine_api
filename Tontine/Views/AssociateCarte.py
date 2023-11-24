from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from BaseApi.AppEnum import *
from Account.models import Users
from Abonnement.Views.Function import * 
from Tontine.models import Cartes, Associate_carte
from Tontine.serializers import CartesSerializer, Associate_carteSerializer, Associate_carteSerializerAdd
from Transaction.Views.views import *
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from copy import deepcopy
from Transaction.models import Transaction
from django.db.models import Sum

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def associateCarte(request):
    data = deepcopy(request.data)  # Create a mutable copy

    data['status'] = StatusTontinierEnum.NOT_COLLECTED.value
    data['invitation_status'] = InvitationStatusEnum.PENDING.value

    user_phone = data.get('phone')
    if user_phone is None:
        return Response({'message': "Veuillez entrer un numéro de téléphone"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = get_object_or_404(Users, phone=user_phone)
    if user is None:
        return Response({'message': "Ce numéro n'a pas de compte"}, status=status.HTTP_UNPROCESSABLE_ENTITY)
    data['user'] = user.id

    if userBasicInfoRequest(user_phone) is None:
        return Response({'message': "Ce numéro n'a pas de compte"}, status=status.HTTP_UNPROCESSABLE_ENTITY)

    dataSerializer = Associate_carteSerializerAdd(data=data)
    if dataSerializer.is_valid():
        associateCarteResponse = dataSerializer.save()
        gain_str = str(associateCarteResponse.carte.gain)
        sale_price_str = str(associateCarteResponse.carte.sale_price)
        number_day_str = str(associateCarteResponse.carte.number_day)

        associateCarteResponse.data = {
            'gain': gain_str,
            'sale_price': sale_price_str,
            'number_day': number_day_str,
        }
        associateCarteResponse.transaction_status = StatusTransactionEnum.PENDING.value
        associateCarteResponse.save()
        return Response(dataSerializer.data, status=status.HTTP_201_CREATED)

    return Response(dataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getAssociateCartes(request):
    # Filtres de recherche
    amount = request.query_params.get('amount')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    tontinier = request.query_params.get('tontinier')
    status = request.query_params.get('status')
    transaction_status = request.query_params.get('transaction_status')
    invitation_status = request.query_params.get('invitation_status')
    search = request.query_params.get('search')
    user = request.query_params.get('user')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('limit')

    filters = Q()

    if amount:
        filters &= Q(carte__amount=amount)
    if start_date:
        filters &= Q(created_at__gte=start_date)
    if end_date:
        filters &= Q(created_at__lte=end_date)
    if tontinier:
        filters &= Q(carte__tontinier=tontinier)
    if user:
        filters &= Q(user=user)
    if status:
        filters &= Q(status=status)
    if transaction_status:
        filters &= Q(transaction_status=transaction_status)
    if invitation_status:
        filters &= Q(invitation_status=invitation_status)
    if search:
        filters &= Q(
            Q(carte__name__icontains=search) |
            Q(tontinier__name__icontains=search) |
            Q(reseau_transaction_id__icontains=search) |
            Q(referenceId__icontains=search)
        )

    associate_cartes = Associate_carte.objects.filter(filters)
    if page_size is None or page_size == "":
        serializer = Associate_carteSerializer(associate_cartes, many=True)
        return Response({'data': serializer.data}, status=200)

    paginator = Paginator(associate_cartes, page_size)
    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    serialized_data = Associate_carteSerializer(paginated_data, many=True)
    response_data = {
        'total_pages': paginator.num_pages,
        'current_page': paginated_data.number,
        'total_items': paginator.count,
        'data': serialized_data.data
    }
    return Response(response_data, status=200)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getAssociateCarte(request, associate_carte_id):
    associate_carte = get_object_or_404(Associate_carte, id=associate_carte_id)

    totalPay = Transaction.objects.filter(type_de_tontine=TontineTypeEnum.CARTE.value, object=associate_carte.id, status=StatusTransactionEnum.SUCCESSFUL.value).aggregate(Sum('number_payment'))['number_payment__sum']
    if totalPay is None:
        totalPay = 0

    serializer = Associate_carteSerializer(associate_carte)
    return Response({'data': serializer.data, 'total_pay': totalPay})

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def setAssociateCarteUserTontinierStatus(request, associate_carte_id):
    associate_carte = get_object_or_404(Associate_carte, id=associate_carte_id)
    new_status = request.data.get('status')
    user_phone = request.data.get('phone')

    if request.user.id != associate_carte.user.id:
        return Response({'message': "Vous n'avez pas le droit de faire cette opération sur cette carte"}, status=status.HTTP_403_FORBIDDEN)

    if new_status is None:
        return Response({'message': "Veuillez entrer un status"}, status=status.HTTP_400_BAD_REQUEST)
    if new_status not in [InvitationStatusEnum.ACCEPTED.value, InvitationStatusEnum.REJECTED.value, InvitationStatusEnum.CANCELLED.value]:
        return Response({'message': "Veuillez entrer un status valide"}, status=status.HTTP_400_BAD_REQUEST)

    if user_phone is None:
        return Response({'message': "Veuillez entrer un numéro de téléphone"}, status=status.HTTP_400_BAD_REQUEST)
    
    if associate_carte.invitation_status == InvitationStatusEnum.ACCEPTED.value and associate_carte.transaction_status == StatusTransactionEnum.SUCCESSFUL.value:
        return Response({'message': 'Status déjà accepté pour cette carte.'}, status=status.HTTP_400_BAD_REQUEST)
   
    associate_carte.invitation_status = new_status
    associate_carte.save()
    
    if new_status == InvitationStatusEnum.ACCEPTED.value:
        sendCarteBuyTransaction(associate_carte.id, user_phone)

    return Response({'message': 'Carte Associate validé avec succès'}, status=status.HTTP_200_OK)  