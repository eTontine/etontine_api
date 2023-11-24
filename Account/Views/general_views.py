from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework.permissions import AllowAny
from Account.models import Countries
from Account.serializers import CountriesSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def countries(request):
    countries = Countries.objects.all()
    serializer = CountriesSerializer(countries, many=True)
    return Response(serializer.data)