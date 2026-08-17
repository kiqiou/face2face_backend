from django.urls import path
from booking.views.work_day import create_work_day, delete_work_day, get_all_work_days, get_free_intervals, get_work_days_by_cosmetologist, update_work_day

urlpatterns = [
    path('get_work_days_by_cosmetologist/<int:cosmetologist_id>/', get_work_days_by_cosmetologist,),
    path('get_free_intervals/<int:work_day_id>/', get_free_intervals),
    path('get_all_work_days/', get_all_work_days),
    path('create_work_day/', create_work_day),
    path('update_work_day/<int:work_day_id>/', update_work_day),
    path('delete_work_day/<int:work_day_id>/', delete_work_day,),
    
]
