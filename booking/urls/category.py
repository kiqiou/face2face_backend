from django.urls import path
from booking.views.category import add_category, update_category, delete_category

urlpatterns = [
    path('add_category/', add_category,),
    path('update_category/<int:category_id>/', update_category,),
    path('delete_category/<int:category_id>/', delete_category,),
]
