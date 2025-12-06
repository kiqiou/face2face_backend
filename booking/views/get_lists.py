from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from users.models import User
from booking.models import Cosmetologist, Procedure, Appointment, Booking
from booking.serializers import (
    CosmetologistSerializer, ProcedureSerializer,
    AppointmentSerializer, BookingSerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_cosmetologists(request):
    cosmetologists = Cosmetologist.objects.all()
    serializer = CosmetologistSerializer(cosmetologists, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_procedures(request):
    procedures = Procedure.objects.all()
    serializer = ProcedureSerializer(procedures, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_appointments_by_cosmetologist(request, cosmetologist_id):
    appointments = Appointment.objects.filter(cosmetologist_id=cosmetologist_id, status=True)
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_procedures_by_cosmetologist(request, cosmetologist_id):
    procedures = Procedure.objects.filter(cosmetologist_id=cosmetologist_id,)
    serializer = ProcedureSerializer(procedures, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
