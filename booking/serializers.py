from rest_framework import serializers
from users.models import User
from booking.models import Cosmetologist, Procedure, Appointment, Booking
from users.serializers.user import UserSerializer

class CosmetologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = Cosmetologist
        fields = ['user', 'bio', 'specializations', 'id', 'avatar_url']

    def get_avatar_url(self, obj):
        if obj.user.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.user.avatar.url)
        return None

class ProcedureSerializer(serializers.ModelSerializer):
    cosmetologist = serializers.SerializerMethodField()

    class Meta:
        model = Procedure
        fields = ['id', 'name', 'price', 'duration', 'cosmetologist']

    def get_cosmetologist(self, obj):
        if not obj.cosmetologist:
            return None
        return {
            'id': obj.cosmetologist.id,
        }

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'date', 'time', 'status']

class BookingSerializer(serializers.ModelSerializer):
    procedure = ProcedureSerializer(read_only=True)
    cosmetologist = serializers.CharField(source='appointment.cosmetologist.user.username', read_only=True)
    date = serializers.DateField(source='appointment.date', read_only=True)
    time = serializers.TimeField(source='appointment.time', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'procedure', 'cosmetologist', 'date', 'time', 'status']

class BookingCreateSerializer(serializers.Serializer):
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(status=True)
    )
