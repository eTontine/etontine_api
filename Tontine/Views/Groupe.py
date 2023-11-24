from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from BaseApi.AppEnum import *
from Abonnement.Views.Function import * 
from Tontine.models import Groupes, Groupe_associate, PaymentPeriod
from Tontine.serializers import GroupesSerializer, GroupesSerializerAdd
from TontineRule.Views.views import addGroupeRuleValues, getGroupeRuleValues
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def createGroupe(request):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    if not abonnementIsActiveAndValidate(request.user.id):
        return Response({'message': 'Abonnement not active or not validate'}, status=status.HTTP_403_FORBIDDEN)
    rule_answers = request.data.get('rule_answers')
    if rule_answers is None:
        return Response({'message': 'rule_answers is required'}, status=status.HTTP_400_BAD_REQUEST)

    request.data['tontinier'] = request.user.id
    
    dataSerializer = GroupesSerializerAdd(data=request.data)
    if dataSerializer.is_valid():
        groupeSave = dataSerializer.save()
        groupeRule = addGroupeRuleValues(rule_answers, groupeSave.id, TontineTypeEnum.GROUPE.value)
        return Response({'groupe': dataSerializer.data, 'rules': groupeRule}, status=status.HTTP_201_CREATED)
    return Response(dataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getGroupes(request, tontinier_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    status = request.query_params.get('status')
    amount = request.query_params.get('amount')
    name = request.query_params.get('name')
    gain = request.query_params.get('gain')
    number_day = request.query_params.get('number_day')
    search = request.query_params.get('search')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('limit', None)

    filters = Q(tontinier=tontinier_id)
    if status:
        filters &= Q(status=status)
    if amount:
        filters &= Q(amount=amount)
    if name:
        filters &= Q(name__icontains=name)
    if gain:
        filters &= Q(gain=gain)
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
            Q(status__icontains=search)
        )
    
    GroupeData = Groupes.objects.filter(filters)

    if page_size is None or page_size == "":
        serializer = GroupesSerializer(GroupeData, many=True)
        return Response({'data': serializer.data}, status=200)

    paginator = Paginator(GroupeData, page_size)
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
    return Response(response_data, status=200)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getGroupe(request, groupe_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    Groupe = get_object_or_404(Groupes, id=groupe_id)
    serializer = GroupesSerializer(Groupe)
    groupeRule = getGroupeRuleValues(Groupe.id, TontineTypeEnum.GROUPE.value)
    return Response({'groupe': serializer.data, 'rules': groupeRule}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def updateGroupe(request, groupe_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    Groupe = get_object_or_404(Groupes, id=groupe_id)
    dataSerializer = GroupesSerializer(Groupe, data=request.data, partial=True)
    if dataSerializer.is_valid():
        dataSerializer.save()
        return Response(dataSerializer.data, status=status.HTTP_200_OK)
    return Response(dataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def deleteGroupe(request, groupe_id):
    if request.user.account_type == AccountTypeEnum.SIMPLE.value:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    Groupe = get_object_or_404(Groupes, id=groupe_id)
    if Groupe.tontinier.id != request.user.id:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if Groupe_associate.objects.filter(groupe=groupe_id).exists():
        return Response({'message': 'Groupe is associate'}, status=status.HTTP_403_FORBIDDEN)

    Groupe.delete()
    return Response({'message': 'Groupe deleted'}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def setGroupeStatus(request, groupe_id):
    if request.user.account_type != AccountTypeEnum.TONTINE.value and request.user.account_type != AccountTypeEnum.ADMIN.value:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    data = request.data
    groupeData = get_object_or_404(Groupes, id=groupe_id)
    new_status = data.get('status')

    if request.user.id != groupeData.tontinier.id:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if groupeData.status == StatusGroupeEnum.IN_PROGESS.value:
        return Response({'message': "Vous ne pouvez plus changer le status de groupe en cours"}, status=status.HTTP_403_FORBIDDEN)
    
    if new_status is None:
        return Response({'message': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
    if new_status == StatusGroupeEnum.IN_PROGESS.value:
        groupeData.start_date = datetime.now()
        groupeData.save()
        addPaymentPeriodDays(groupe=groupeData.id)
    groupeData.status = new_status
    groupeData.save()
    return Response({'message': 'Status updated'}, status=status.HTTP_200_OK)
        
def addPaymentPeriodDays(groupe):
    group = get_object_or_404(Groupes, id=groupe)
    groupe_associate = Groupe_associate.objects.filter(groupe=group, invitation_status=InvitationStatusEnum.ACCEPTED.value)
    
    if groupe_associate.exists():
        contribution_period = group.contribution_period
        contribution_day = group.day_contribution
        contribution_time = group.time_contribution
        start_date = group.start_date

        number_associate_groupe = groupe_associate.count()
        payment_dates = []
        
        for i in range(number_associate_groupe):
            if contribution_period == 'DAY':
                i = i + 1
                payment_date = start_date + timedelta(days=i)
            elif contribution_period == 'WEEK':
                days_to_next_contribution_day = (formatWeekDay(contribution_day) - start_date.weekday() + 7) % 7
                next_contribution_date = start_date + timedelta(days=days_to_next_contribution_day)
                payment_date = next_contribution_date + timedelta(weeks=i)
            elif contribution_period == 'MONTH':
                i = i + 1
                payment_date = start_date + relativedelta(months=i)
            else:
                pass
            
            payment_date = datetime.combine(payment_date, contribution_time)
            payment_dates.append(payment_date)

        PaymentPeriod.objects.filter(groupe_associate__groupe=group).delete()

        i = 1
        for associate in groupe_associate:
            addDateCollect(associate.id, payment_dates, i)
            for payment_date in payment_dates:
                PaymentPeriod.objects.create(groupe_associate=associate, payment_date=payment_date)

        return True

def addDateCollect(associateId, payment_dates, period):
    associate = Groupe_associate.objects.get(id=associateId)
    associate.payment_period = period
    associate.date_collect = payment_dates[period-1]

def formatWeekDay(day):
    data = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    try:
        index = data.index(day.upper())
        return index
    except ValueError:
        return None
