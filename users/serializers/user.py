from rest_framework import serializers
from users.models import SkinQuizResult, User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'personal_data_consent_at', 'personal_data_consent_ip', 'telegram_id', 'manual_discount_percent', 'is_staff' ]

from rest_framework import serializers
from users.models import SkinQuizResult, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'phone',
            'personal_data_consent_at',
            'personal_data_consent_ip',
            'telegram_id',
            'manual_discount_percent',
            'is_staff'
        ]


class SkinQuizResultSerializer(serializers.ModelSerializer):
    skin_type = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = SkinQuizResult
        fields = ['id', 'skin_type', 'updated_at', 'user']

    def get_skin_type(self, obj):
        return {
            'id': obj.skin_type.id,
            'name': obj.skin_type.name,
            'description': obj.skin_type.description
        }