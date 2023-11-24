from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import *
from rest_framework.response import Response
from Notification.models import *
from django.shortcuts import get_object_or_404
from Notification.serializers import *
from Account.models import Users
from rest_framework import status
from BaseApi.AppEnum import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def user_notifications(request): 
    user = request.user
    notifications = Notifications.objects.filter(receiver = user)
    
    if notifications.exists():
        serializer = NotificationsSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Aucune notification pour cet utilisateur.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def notification_details(request, notification_id):
    try:
        notification = Notifications.objects.get(id = notification_id, receiver = request.user)
    except Notifications.DoesNotExist:
        return Response({'message': 'La notification n\'existe pas ou n\'appartient pas à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = NotificationsSerializer(notification)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def notification_vues(notification_id):
    try:
        notification = Notifications.objects.get(id = notification_id)
    except Notifications.DoesNotExist:
        return Response({'message': 'La notification n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

    if not notification.is_see:
        notification.is_see = True
        notification.is_send = True
        notification.save()

    return Response({'message': 'La notification a été vue.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def notification_send(notification_id):
    try:
        notification = Notifications.objects.get(id = notification_id)
    except Notifications.DoesNotExist:
        return Response({'message': 'La notification n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

    if not notification.is_send:
        notification.is_send = True
        notification.save()

    return Response({'message': 'La notification a été envoyée.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_notification(request):
    if request.method == 'POST':
        serializer = NotificationsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
