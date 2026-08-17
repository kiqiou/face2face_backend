from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/work_days/', include('booking.urls.work_day')),
    path('api/procedures/', include('booking.urls.procedure')),
    path('api/products/', include('booking.urls.products')),
    path('api/booking/', include('booking.urls.booking')),
    path('api/category/', include('booking.urls.category')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)