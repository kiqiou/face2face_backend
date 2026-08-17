from django.urls import path
from booking.views.products import add_product, delete_product, get_products, update_product

urlpatterns = [
    path('get_products/', get_products, name='get_products'),
    path('add_product/', add_product, name='add_product'),
    path('update_product/<int:product_id>/', update_product, name='update_product'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
]