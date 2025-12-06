from django.urls import path
from booking.views.appointment import add_appointment, delete_appointment

urlpatterns = [
    path('add_appointment/', add_appointment,),
    path('delete_appointment/<int:appointment_id>/', delete_appointment,),
]
