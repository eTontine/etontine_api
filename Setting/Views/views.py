from Setting.models import Setting
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from Setting.serializers import SettingSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def addSetting(request):
    key = request.data.get('key')
    value = request.data.get('value')
    if key is not None and value is not None:
        setting, created = Setting.objects.get_or_create(key=key, defaults={'value': value})
        if not created:
            return Response({'message': 'Le paramètre existe déjà.'}, status=status.HTTP_BAD_REQUEST)
        serializer = SettingSerializer(setting)
        return Response(serializer.data, status=status.HTTP_CREATED)
    else:
        return Response({'message': "Vous devez fournir une clé et une valeur pour le paramètre."}, status=status.HTTP_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def updateSetting(request, setting_key):
    value = request.data.get('value')
    try:
        setting = Setting.objects.get(key=setting_key)
        setting.value = value
        setting.save()
        serializer = SettingSerializer(setting)
        return Response(serializer.data)
    except Setting.DoesNotExist:
        return Response({'message': "Le paramètre n'existe pas."}, status=status.HTTP_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getSetting(request, setting_key):
    try:
        setting = Setting.objects.get(key=setting_key)
        serializer = SettingSerializer(setting)
        return Response(serializer.data)
    except Setting.DoesNotExist:
        return Response({'message': "Le paramètre n'existe pas."}, status=status.HTTP_NOT_FOUND)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def deleteSetting(request, setting_key):
    try:
        setting = Setting.objects.get(key=setting_key)
        setting.delete()
        return Response({'message': "Le paramètre a été supprimé."})
    except Setting.DoesNotExist:
        return Response({'message': "Le paramètre n'existe pas."}, status=status.HTTP_NOT_FOUND)