from django.urls import path
from booking.views.booking import cancel_booking, create_booking, update_booking

urlpatterns = [
    path('create_booking/', create_booking,),
    path('cancel_booking/<int:booking_id>/', cancel_booking),
    path('update_booking/<int:booking_id>/', update_booking)
]
