from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role', 'personal_data_consent_at', 'personal_data_consent_ip', 'telegram_id', 'manual_discount_percent']
