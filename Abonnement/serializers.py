from rest_framework import serializers
from Abonnement.models import Abonnement, TontinierAbonnement
from Account.serializers import UsersSerializer

class AbonnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abonnement
        fields = '__all__'

class TontinierAbonnementSerializer(serializers.ModelSerializer):
    abonnement = AbonnementSerializer()
    class Meta:
        model = TontinierAbonnement
        fields = '__all__'