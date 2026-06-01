from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from booking import models
from booking.models import Booking, Procedure, WorkDay
from booking.serializers import BookingSerializer
from datetime import datetime, timedelta
from django.db.models import Q

from tg_bot.signals import send_booking_created

def calculate_free_intervals(work_day):
    bookings = Booking.objects.filter(
        cosmetologist=work_day.cosmetologist,
        date=work_day.date,
        status=True
    ).order_by('start_time')

    free_intervals = []

    current_start = work_day.start_time

    for booking in bookings:
        if booking.start_time > current_start:
            free_intervals.append((current_start, booking.start_time))
        current_start = max(current_start, booking.end_time)

    if current_start < work_day.end_time:
        free_intervals.append((current_start, work_day.end_time))

    return free_intervals

def find_slot_for_duration(free_intervals, duration, date):
    for start, end in free_intervals:
        start_dt = datetime.combine(date, start)
        end_dt = datetime.combine(date, end)

        if end_dt - start_dt >= duration:
            return start_dt

    return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    user = request.user
    procedure_ids = request.data.get('procedure_ids')
    work_day_id = request.data.get('work_day_id')
    start_time_str = request.data.get('start_time') 

    work_day = WorkDay.objects.get(id=work_day_id, is_working=True)
    procedures = Procedure.objects.filter(id__in=procedure_ids)
    
    duration = timedelta()

    for p in procedures:
        duration += p.duration
        duration += p.buffer_time 

    if start_time_str:
        start_dt = datetime.combine(work_day.date, datetime.strptime(start_time_str, '%H:%M').time())
    else:
        free_intervals = calculate_free_intervals(work_day)
        start_dt = find_slot_for_duration(free_intervals, duration, work_day.date)

    end_dt = start_dt + duration

    if start_dt.time() < work_day.start_time or end_dt.time() > work_day.end_time:
        return Response({'error': 'Вне рабочего времени'}, status=400)

    booking = Booking.objects.create(
        user=user,
        cosmetologist=work_day.cosmetologist,
        date=work_day.date,
        start_time=start_dt.time(),
        end_time=end_dt.time(),
        duration=duration,
        price=sum(p.price for p in procedures),
        status=True
    )

    booking.procedures.set(procedures)

    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=201)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_booking(request, booking_id):
    user = request.user
    work_day_id = request.data.get('work_day_id')        
    start_time_str = request.data.get('start_time')     
    
    try:
        booking = Booking.objects.get(id=booking_id, status=True)
        
        if user != booking.user and user != booking.cosmetologist.user:
            return Response({'error': 'Нет прав на изменение этой брони'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if work_day_id:
            work_day = WorkDay.objects.get(id=work_day_id, is_working=True)
        else:
            work_day = WorkDay.objects.get(
                cosmetologist=booking.cosmetologist, 
                date=booking.date, 
                is_working=True
            )

        if start_time_str:
            start_dt = datetime.combine(work_day.date, datetime.strptime(start_time_str, '%H:%M').time())
        else:

            free_intervals = calculate_free_intervals(work_day)
            start_dt = find_slot_for_duration(free_intervals, booking.duration, work_day.date)
            if not start_dt:
                return Response({'error': 'Нет свободного времени для указанной длительности'}, status=400)
        
        end_dt = start_dt + booking.duration
        

        if start_dt.time() < work_day.start_time or end_dt.time() > work_day.end_time:
            return Response({'error': 'Вне рабочего времени'}, status=400)
        
        overlapping_bookings = Booking.objects.filter(
            cosmetologist=work_day.cosmetologist,
            date=work_day.date,
            status=True
        ).exclude(id=booking_id).filter(

            Q(
                start_time__lt=end_dt.time(),
                end_time__gt=start_dt.time()
            )
        )
        
        if overlapping_bookings.exists():
            return Response({'error': 'В указанное время уже есть бронирование'}, status=400)
        
        booking.user = user
        booking.cosmetologist = work_day.cosmetologist
        booking.date = work_day.date
        booking.start_time = start_dt.time()
        booking.end_time = end_dt.time()
        booking.save()
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=200)
        
    except Booking.DoesNotExist:
        return Response({'error': 'Бронирование не найдено'}, status=status.HTTP_404_NOT_FOUND)
    except WorkDay.DoesNotExist:
        return Response({'error': 'Рабочий день не найден или не активен'}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    user = request.user
    
    try:
        booking = Booking.objects.get(id=booking_id)
        
        if user == booking.user or user == booking.cosmetologist.user:
            booking.delete()
            return Response({'detail': 'Бронирование отменено'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Нет прав на отмену этой брони'}, status=status.HTTP_403_FORBIDDEN)
            
    except Booking.DoesNotExist:
        return Response({'error': 'Бронирование не найдено'}, status=status.HTTP_404_NOT_FOUND)