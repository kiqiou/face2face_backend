from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from booking.views.booking import calculate_free_intervals
from users.models import User
from booking.models import Category, Cosmetologist, Procedure, Booking, Product, WorkDay
from booking.serializers import (
    CategorySerializer, CosmetologistSerializer, ProcedureSerializer, BookingSerializer, ProductSerializer, WorkDaySerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_cosmetologists(request):
    cosmetologists = Cosmetologist.objects.all()
    serializer = CosmetologistSerializer(cosmetologists, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cosmetologist_by_id(request, cosmetologist_id):
    cosmetologist = Cosmetologist.objects.get(
        id=cosmetologist_id,
    )
    serializer = CosmetologistSerializer(cosmetologist, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cosmetologist_by_user_id(request, user_id):
    cosmetologist = Cosmetologist.objects.get(
        user__id=user_id,
    )
    serializer = CosmetologistSerializer(cosmetologist, context={'request': request})
    return Response(serializer.data)
