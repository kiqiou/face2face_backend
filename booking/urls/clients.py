# promotions/urls.py
from django.urls import path
from booking.views.clients import get_clients, set_client_discount

urlpatterns = [
    path('clients/', get_clients),
    path('clients/<int:user_id>/discount/', set_client_discount),
]