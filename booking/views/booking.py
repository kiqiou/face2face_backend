from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from booking.models import Booking
from booking.serializers import BookingCreateSerializer, BookingSerializer
from django.utils import timezone
from datetime import datetime, timedelta

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    user = request.user
    serializer = BookingCreateSerializer(data=request.data)
    if serializer.is_valid():
        appointment = serializer.validated_data['appointment']
        if not appointment.status:
            return Response({'error': 'Это свободное окно уже занято'}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=user, appointment=appointment, status=True)

        appointment.status = False
        appointment.save()

        return Response({'detail': 'Запись подтверждена', 'booking_id': booking.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    user = request.user
    try:
        booking = Booking.objects.get(id=booking_id, user=user)
    except Booking.DoesNotExist:
        return Response({'error': 'Бронирование не найдено'}, status=status.HTTP_404_NOT_FOUND)

    appointment = booking.appointment
    now = timezone.now()

    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.date, appointment.time)
    )

    if appointment_datetime - now < timedelta(hours=12):
        return Response({'error': 'Самостоятельная отмена невозможна менее чем за 12 часов до процедуры'}, status=status.HTTP_400_BAD_REQUEST)

    booking.delete()
    
    appointment.status = True
    appointment.save()

    return Response({'detail': 'Бронирование отменено'}, status=status.HTTP_204_NO_CONTENT)
