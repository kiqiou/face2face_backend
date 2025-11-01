from django.urls import path
from booking.views.appointment import add_appointment, delete_appointment

urlpatterns = [
    path('api/add_appointment/', add_appointment,),
    path('api/delete_appointment/<int:appointment_id>/', delete_appointment,),
]
