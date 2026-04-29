from django.urls import path
from booking.views.get_lists import (
    get_cosmetologist_by_id, get_cosmetologist_by_user_id, get_free_intervals, list_all_bookings, list_all_work_days, list_cosmetologist_bookings, list_cosmetologists, list_procedures,
    list_procedures_by_cosmetologist, list_user_bookings, list_work_days_by_cosmetologist,
)

urlpatterns = [
    path('get_cosmetologists/', list_cosmetologists,),
    path('get_cosmetologist_by_user_id/<int:user_id>/', get_cosmetologist_by_user_id),
    path('get_cosmetologist_by_id/<int:cosmetologist_id>/', get_cosmetologist_by_id,),
    path('get_procedures/', list_procedures,),
    path('get_work_days_by_cosmetologist/<int:cosmetologist_id>/', list_work_days_by_cosmetologist,),
    path('get_free_intervals/<int:work_day_id>/', get_free_intervals),
    path('get_all_work_days/', list_all_work_days),
    path('get_procedures_by_cosmetologist/<int:cosmetologist_id>/', list_procedures_by_cosmetologist),
    path('get_user_bookings/', list_user_bookings,),
    path('get_all_bookings/', list_all_bookings),
    path('get_cosmetologist_bookings/', list_cosmetologist_bookings),
]
