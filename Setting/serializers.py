from rest_framework import serializers
from Setting.models import Setting

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'