from django.urls import path
from booking.views.cosmetologist import (
    get_cosmetologist_by_id, get_cosmetologist_by_user_id, list_cosmetologists,
)

urlpatterns = [
    path('get_cosmetologists/', list_cosmetologists,),
    path('get_cosmetologist_by_user_id/<int:user_id>/', get_cosmetologist_by_user_id),
    path('get_cosmetologist_by_id/<int:cosmetologist_id>/', get_cosmetologist_by_id,),
]
