from django.urls import path
from booking.views.booking import create_booking

urlpatterns = [
    path('api/add_booking/', create_booking,),
]
