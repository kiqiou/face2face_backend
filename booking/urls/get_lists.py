from django.urls import path
from booking.views.get_lists import (
    list_cosmetologists, list_procedures,
    list_appointments_by_cosmetologist, list_user_bookings,
)

urlpatterns = [
    path('api/get_cosmetologists/', list_cosmetologists,),
    path('api/get_procedures/', list_procedures,),
    path('api/get_appointments/<int:cosmetologist_id>/', list_appointments_by_cosmetologist,),
    path('api/get_user_bookings/', list_user_bookings,),
]
