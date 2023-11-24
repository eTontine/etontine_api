from rest_framework import serializers
from Tontine.models import Cartes, Associate_carte, Groupes, Groupe_associate
from BaseApi.AppEnum import *
from Account.serializers import UsersSerializer

class CartesSerializer(serializers.ModelSerializer):
    tontinier = UsersSerializer()
    class Meta:
        model = Cartes
        fields = '__all__'
        
class CartesSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Cartes
        fields = '__all__'

class Associate_carteSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Associate_carte
        fields = '__all__'

class Associate_carteSerializer(serializers.ModelSerializer):
    carte = CartesSerializer()
    user = UsersSerializer()
    class Meta:
        model = Associate_carte
        fields = '__all__'

class GroupesSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=StatusGroupeEnum)
    contribution_period = serializers.ChoiceField(choices=Period)
    tontinier = UsersSerializer()

    class Meta:
        model = Groupes
        fields = '__all__'
        
class GroupesSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Groupes
        fields = '__all__'


class Groupe_associateSerializer(serializers.ModelSerializer):
    groupe = GroupesSerializer()
    user = UsersSerializer()
    class Meta:
        model = Groupe_associate
        fields = '__all__'

class Groupe_associateSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Groupe_associate
        fields = '__all__'