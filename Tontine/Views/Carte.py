from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from BaseApi.AppEnum import *
from Abonnement.Views.Function import * 
from Tontine.models import Cartes, Associate_carte
from Tontine.serializers import CartesSerializer, CartesSerializerAdd
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def createCarte(request):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    if not abonnementIsActiveAndValidate(request.user.id):
        return Response({'message': 'Abonnement not active or not validate'}, status=status.HTTP_403_FORBIDDEN)

    dataSerializer = CartesSerializerAdd(data=request.data)
    if dataSerializer.is_valid():
        dataSerializer.save()
        return Response(dataSerializer.data, status=status.HTTP_201_CREATED)
    return Response(dataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getCartes(request, tontinier_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    online = request.query_params.get('online')
    amount = request.query_params.get('amount')
    name = request.query_params.get('name')
    gain = request.query_params.get('gain')
    number_day = request.query_params.get('number_day')
    search = request.query_params.get('search')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('limit', None)

    filters = Q(tontinier=tontinier_id)
    if online:
        filters &= Q(online=online)
    if amount:
        filters &= Q(amount=amount)
    if name:
        filters &= Q(name__icontains=name)
    if gain:
        filters &= Q(gain=gain)
    if number_day:
        filters &= Q(number_day=number_day)
    if start_date:
        filters &= Q(created_at__gte=start_date)
    if end_date:
        filters &= Q(created_at__lte=end_date)
    
    if search:
        filters &= (
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(amount__icontains=search) |
            Q(gain__icontains=search) | 
            Q(online__icontains=search)
        )
    
    cartes = Cartes.objects.filter(filters)

    if page_size is None or page_size == "":
        serializer = CartesSerializer(cartes, many=True)
        return Response({'data': serializer.data}, status=200)

    paginator = Paginator(cartes, page_size)
    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    serializer = CartesSerializer(paginated_data, many=True)
    response_data = {
        'total_pages': paginator.num_pages,
        'current_page': paginated_data.number,
        'total_items': paginator.count,
        'data': serializer.data
    }
    return Response(response_data, status=200)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getCarte(request, carte_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    carte = get_object_or_404(Cartes, id=carte_id)
    serializer = CartesSerializer(carte)
    return Response(serializer.data)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def updateCarte(request, carte_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    carte = get_object_or_404(Cartes, id=carte_id)
    dataSerializer = CartesSerializerAdd(carte, data=request.data, partial=True)
    if dataSerializer.is_valid():
        dataSerializer.save()
        return Response(dataSerializer.data, status=status.HTTP_200_OK)
    return Response(dataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def deleteCarte(request, carte_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    carte = get_object_or_404(Cartes, id=carte_id)
    if carte.tontinier.id != request.user.id:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if Associate_carte.objects.filter(carte=carte_id).exists():
        return Response({'message': 'Carte is used'}, status=status.HTTP_400_BAD_REQUEST)

    carte.delete()
    return Response({'message': 'Carte deleted'}, status=status.HTTP_200_OK)


    