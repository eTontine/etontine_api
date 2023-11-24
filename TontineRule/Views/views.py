from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from BaseApi.AppEnum import *
from TontineRule.models import Rule_values, Rules
from django.db.models import Q

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getRules(request, type):
    if request.user.account_type != AccountTypeEnum.TONTINE.value and request.user.account_type != AccountTypeEnum.ADMIN.value:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    filters = Q(type=type) | Q(type=TypeRuleEnum.COMMUN.value)
    rules = Rules.objects.filter(filters)
    serializerData = [rule.serialize() for rule in rules]
    return Response(serializerData, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def addRuleValues(request):
    if request.user.account_type != AccountTypeEnum.TONTINE.value and request.user.account_type != AccountTypeEnum.ADMIN.value:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    data = request.data
    serializerData = []
    for rule_answer in data['rule_answers']:
        rule_value = Rule_values.objects.get_or_create(
            rule=get_object_or_404(Rules, id=rule_answer['rule_id']),
            type=rule_answer['type'],
            carte_or_groupe_id=rule_answer['carte_or_groupe_id'],
            defaults = {
                'value': rule_answer['value'],
            }
        )
        serializerData.append(rule_value.serialize())
    return Response(serializerData, status=status.HTTP_200_OK)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getRuleValues(request, type, carte_or_groupe_id):
    if request.user.account_type != AccountTypeEnum.TONTINE.value and request.user.account_type != AccountTypeEnum.ADMIN.value:
        return Response(status=status.HTTP_403_FORBIDDEN)

    filters = Q(type=type, carte_or_groupe_id=carte_or_groupe_id)
    
    rules = Rule_values.objects.filter(filters)
    serializerData = [rule.serialize() for rule in rules]
    return Response(serializerData, status=status.HTTP_200_OK)

def addGroupeRuleValues(data, carte_or_groupe_id, type):
    ruleData = []
    if not data:
        return False
    else:
        for rule_answer in data:
            rule_instance, created = Rule_values.objects.get_or_create(
                rule=get_object_or_404(Rules, id=rule_answer['rule_id']),
                type=type,
                carte_or_groupe_id=carte_or_groupe_id,
                defaults={
                    'value': rule_answer['value'],
                }
            )
            ruleData.append(rule_instance.serialize())
    return ruleData
            
def getGroupeRuleValues(carte_or_groupe_id, type):
    filters = Q(type=type, carte_or_groupe_id=carte_or_groupe_id)
    rules = Rule_values.objects.filter(filters)
    serializerData = [rule.serialize() for rule in rules]
    return serializerData