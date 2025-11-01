from rest_framework import serializers

from users.models import Role

class RoleSerializer(serializers.ModelSerializer):
    model = Role
    class Meta:
        fields = ['id', 'name']