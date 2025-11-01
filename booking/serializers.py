from rest_framework import serializers
from users.models import User
from booking.models import Procedure, Appointment, Booking

class CosmetologistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ['id', 'name', 'price', 'duration']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'date', 'time', 'status']

class BookingSerializer(serializers.ModelSerializer):
    procedure = serializers.CharField(source='appointment.procedure.name', read_only=True)
    cosmetologist = serializers.CharField(source='appointment.cosmetologist.user.username', read_only=True)
    date = serializers.DateField(source='appointment.date', read_only=True)
    time = serializers.TimeField(source='appointment.time', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'procedure', 'cosmetologist', 'date', 'time', 'status']
