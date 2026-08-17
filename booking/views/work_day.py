from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from booking.models import Cosmetologist, WorkDay
from booking.serializers import WorkDaySerializer
from booking.models import Booking
from booking.views.booking import calculate_free_intervals


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_work_days(request):
    work_days = WorkDay.objects.filter(is_working=True).prefetch_related('cosmetologist')
    serializer = WorkDaySerializer(work_days, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_work_days_by_cosmetologist(request, cosmetologist_id):
    work_days = WorkDay.objects.filter(
        cosmetologist_id=cosmetologist_id,
        is_working=True
    )

    serializer = WorkDaySerializer(work_days, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_free_intervals(request, work_day_id):
    try:
        work_day = WorkDay.objects.get(id=work_day_id, is_working=True)
    except WorkDay.DoesNotExist:
        return Response({'error': 'Рабочий день не найден'}, status=404)

    free = calculate_free_intervals(work_day)

    free_list = [
        {"start": start.strftime("%H:%M"), "end": end.strftime("%H:%M")}
        for start, end in free
    ]

    return Response(free_list)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_work_day(request):
    user = request.user

    if not hasattr(user, 'cosmetologist_profile'): 
        return Response( {'error': 'Пользователь не косметолог'}, status=status.HTTP_403_FORBIDDEN ) 
    
    cosmetologist = Cosmetologist.objects.get(user=user.id)

    date = request.data.get('date')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')

    if not date or not start_time or not end_time:
        return Response({'error': 'Не все поля переданы'}, status=400)

    if start_time >= end_time:
        return Response({'error': 'Некорректное время'}, status=400)

    work_day = WorkDay.objects.create(
        cosmetologist=cosmetologist,
        date=date,
        start_time=start_time,
        end_time=end_time,
    )

    return Response({'id': work_day.id}, status=201)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_work_day(request, work_day_id):
    user = request.user

    if not user.is_cosmetologist():
        return Response({'error': 'Только косметолог'}, status=403)

    try:
        work_day = WorkDay.objects.get(
            id=work_day_id,
            cosmetologist=user.cosmetologist_profile
        )
    except WorkDay.DoesNotExist:
        return Response({'error': 'Не найден'}, status=404)

    serializer = WorkDaySerializer(
        work_day,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)

    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_work_day(request, work_day_id):
    user = request.user

    if not user.is_cosmetologist():
        return Response({'error': 'Только косметологи'}, status=403)

    try:
        work_day = WorkDay.objects.get(
            id=work_day_id,
            cosmetologist=user.cosmetologist_profile
        )
    except WorkDay.DoesNotExist:
        return Response({'error': 'Не найден'}, status=404)

    work_day.delete()

    return Response({'detail': 'Удалено'}, status=204)
