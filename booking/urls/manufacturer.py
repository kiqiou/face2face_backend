from django.urls import path

from booking.views.manufacturer import add_manufacturer, get_manufacturers


urlpatterns = [
    path('get_manufacturers/', get_manufacturers, name='get_manufacturers'),
    path('add_manufacturer/', add_manufacturer, name='add_manufacturer'),

]