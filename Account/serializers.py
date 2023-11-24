from rest_framework import serializers
from Account.models import Countries, Users

class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    country = CountriesSerializer()
    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class UsersSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}