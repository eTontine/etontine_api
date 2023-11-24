from rest_framework import serializers
from Transaction.models import Transaction
from BaseApi.AppEnum import *
from Account.serializers import UsersSerializer
from django.contrib.contenttypes.models import ContentType

class TransactionSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'
