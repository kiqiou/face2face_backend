from django.urls import path

from booking.views.orders import (
    create_order, delete_order, get_analytics, get_order_by_id, get_orders,
    update_order_status, get_my_orders, 
)

urlpatterns = [
    path('create_order/', create_order, name='create_order'),
    path('analytics/', get_analytics, name='get_analytics'),
    path('get_orders/', get_orders, name='get_orders'),
    path('get_order_by_id/<int:order_id>/', get_order_by_id, name='get_order'),
    path('get_my_orders/', get_my_orders, name='get_my_orders'),
    path('update_order_status/<int:order_id>/', update_order_status, name='update_order_status'),
    path('delete_order/<int:order_id>/', delete_order, name='delete_order'),
]