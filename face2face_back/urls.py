from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/appointment/', include('booking.urls.appointment')),
    path('api/procedures/', include('booking.urls.procedure')),
    path('api/booking/', include('booking.urls.booking')),
    path('api/get_lists/', include('booking.urls.get_lists')),
]
