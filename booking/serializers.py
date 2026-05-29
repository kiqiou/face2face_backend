from rest_framework import serializers
from users.models import User
from booking.models import Category, Cosmetologist, Procedure, Booking, WorkDay
from users.serializers.user import UserSerializer

class CosmetologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Cosmetologist
        fields = ['user', 'bio', 'specializations', 'id', 'avatar_url']

    def get_avatar_url(self, obj):
        return obj.avatar_url

class CategorySerializer(serializers.ModelSerializer):
    model = Category
    fields = ['id', 'name']

class ProcedureSerializer(serializers.ModelSerializer):
    cosmetologist = CosmetologistSerializer()
    category = CategorySerializer()

    class Meta:
        model = Procedure
        fields = ['id', 'name', 'price', 'duration', 'description',  'isSale', 'cosmetologist']

class WorkDaySerializer(serializers.ModelSerializer):
    cosmetologist = CosmetologistSerializer()

    class Meta:
        model = WorkDay
        fields = [
            'id',
            'date',
            'start_time',
            'end_time',
            'is_working',
            'cosmetologist'
        ]

class WorkDayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkDay
        fields = [
            'id',
            'date',
            'start_time',
            'end_time',
            'is_working'
        ]

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    cosmetologist = CosmetologistSerializer()
    procedures = ProcedureSerializer(many=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'cosmetologist',
            'date',
            'start_time',
            'end_time',
            'duration',
            'price',
            'status',
            'procedures'
        ]
