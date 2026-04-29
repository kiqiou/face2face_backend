from django.urls import path
from booking.views.work_day import create_work_day, delete_work_day, update_work_day

urlpatterns = [
    path('create_work_day/', create_work_day),
    path('update_work_day/<int:work_day_id>/', update_work_day),
    path('delete_work_day/<int:work_day_id>/', delete_work_day,),
]
