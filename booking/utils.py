from django.utils import timezone
from datetime import datetime
from .models import Appointment, Booking

def close_past_appointments_and_bookings():
    now = timezone.now()
    
    # 1. НАЙДИ ID старых аппоинтментов (ДО update!)
    past_appointment_ids = Appointment.objects.filter(
        status=True,
        date__lt=now.date()
    ).values_list('id', flat=True)
    
    print(f"Найдено {len(past_appointment_ids)} старых аппоинтментов")
    
    # 2. Обнови сами аппоинтменты
    Appointment.objects.filter(id__in=past_appointment_ids).update(status=False)
    
    # 3. Обнови БУКИНГИ по тем же ID (не queryset!)
    Booking.objects.filter(
        status=True,
        appointment__id__in=past_appointment_ids
    ).update(status=False)
    
    print("Готово!")

