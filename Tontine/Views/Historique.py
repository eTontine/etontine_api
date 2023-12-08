from Tontine.models import *
from Tontine.serializers import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getUserCartesGroupes(request):
    user = request.user
    number = request.query_params.get('number', 3)
    
    filterGroupes = Q(
        Q(user=user) |
        Q(groupe__tontinier=user)
    )
    
    filterCartes = Q(
        Q(user=user) |
        Q(carte__tontinier=user)
    )
    
    last_three_cartes = Associate_carte.objects.filter(filterCartes).order_by('-created_at')[:number]
    last_three_groupes = Groupe_associate.objects.filter(filterGroupes).order_by('-created_at')[:number]
    
    serialiser_carte = Associate_carteSerializer(last_three_cartes, many=True)
    serialiser_groupe = Groupe_associateSerializer(last_three_groupes, many=True)
    
    result = {
        'last_three_cartes': serialiser_carte.data,
        'last_three_groupes': serialiser_groupe.data,
    }

    return Response(result) 