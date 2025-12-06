from django.urls import path
from booking.views.get_lists import (
    list_cosmetologists, list_procedures,
    list_appointments_by_cosmetologist, list_procedures_by_cosmetologist, list_user_bookings,
)

urlpatterns = [
    path('get_cosmetologists/', list_cosmetologists,),
    path('get_procedures/', list_procedures,),
    path('get_appointments/<int:cosmetologist_id>/', list_appointments_by_cosmetologist,),
    path('list_procedures_by_cosmetologist/<int:cosmetologist_id>/', list_procedures_by_cosmetologist),
    path('get_user_bookings/', list_user_bookings,),
]
