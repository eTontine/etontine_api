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
from Account.serializers import UsersSerializerAdd, UsersSerializer
from Transaction.Views.views import mobilWalletUser

@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def register(request):
    """
    Register a new user.
    """
    phone = request.data.get('phone')
    if not phone:
        return Response({
            'message': 'Le téléphone est requis'
            }, status=status.HTTP_400_BAD_REQUEST)

    walletUser = mobilWalletUser(phone)
    if walletUser:
        new_user = {
            'username': request.data.get('phone'),
            'password': make_password(request.data.get('code')),
            'account_type': request.data.get('account_type', AccountTypeEnum.SIMPLE.value),
            'country': request.data.get('country'),
            'name': walletUser.get("name"),
            'phone': phone,
        }
        serializer = UsersSerializerAdd(data=new_user)
        if serializer.is_valid():
            serializer.save()
            return Response({
            'message': 'Utilisateur créé avec succès',
            'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
            'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'message': 'Numéro de transaction mobile invalide'
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Get the current user.
    """
    serializer = UsersSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users(request):
    """
    Get all users.
    """
    if request.user.account_type!= AccountTypeEnum.ADMIN.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    users = Users.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user(request, id):
    """
    Get a specific user.
    """
    user = get_object_or_404(Users, id=id)
    serializer = UsersSerializer(user)
    return Response(serializer.data)