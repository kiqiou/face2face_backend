from django.urls import path
from booking.views.booking import cancel_booking, create_booking, get_all_bookings, get_cosmetologist_bookings, get_user_bookings, update_booking

urlpatterns = [
    path('get_user_bookings/', get_user_bookings,),
    path('get_all_bookings/', get_all_bookings),
    path('get_cosmetologist_bookings/', get_cosmetologist_bookings),
    path('create_booking/', create_booking,),
    path('cancel_booking/<int:booking_id>/', cancel_booking),
    path('update_booking/<int:booking_id>/', update_booking)
]
