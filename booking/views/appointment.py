from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from booking.models import Appointment
from booking.serializers import AppointmentSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_appointment(request):
    user = request.user
    if not user.is_cosmetologist():
        return Response({'error': 'Только косметологи могут создавать записи'}, status=status.HTTP_403_FORBIDDEN)

    date = request.data.get('date')
    time = request.data.get('time')

    if not date or not time:
        return Response({'error': 'Дата и время обязательны'}, status=status.HTTP_400_BAD_REQUEST)

    data = {
        'date': date,
        'time': time,
        'status': True,
    }
    serializer = AppointmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(cosmetologist=user.cosmetologist_profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_appointment(request, appointment_id):
    user = request.user
    if not user.is_cosmetologist():
        return Response({'error': 'Только косметологи могут удалять записи'}, status=status.HTTP_403_FORBIDDEN)

    try:
        appointment = Appointment.objects.get(id=appointment_id, cosmetologist=user.cosmetologist_profile)
    except Appointment.DoesNotExist:
        return Response({'error': 'Запись не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    appointment.delete()
    return Response({'detail': 'Запись успешно удалена'}, status=status.HTTP_204_NO_CONTENT)
