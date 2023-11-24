from rest_framework import serializers
from Notification.models import Notifications
from Account.serializers import UsersSerializer

class NotificationsSerializer(serializers.ModelSerializer):
    receiver = UsersSerializer() 
    class Meta:
        model = Notifications
        fields = '__all__'