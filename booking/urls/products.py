from django.urls import path
from booking.views.products import add_collection, add_manufacturer, add_product, add_purpose, add_skin_type, delete_collection, delete_manufacturer, delete_product, delete_purpose, delete_skin_type, get_collections, get_manufacturers, get_product, get_products, get_purposes, get_skin_types, update_collection, update_manufacturer, update_product, update_purpose, update_skin_type

urlpatterns = [
    path('get_products/', get_products, name='get_products'),
    path('get_product/<int:product_id>/', get_product, name='get_product'),
    path('add_product/', add_product, name='add_product'),
    path('update_product/<int:product_id>/', update_product, name='update_product'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),

    path('get_manufacturers/', get_manufacturers, name='get_manufacturers'),
    path('add_manufacturer/', add_manufacturer, name='add_manufacturer'),
    path('update_manufacturer/<int:manufacturer_id>/', update_manufacturer, name='update_manufacturer'),
    path('delete_manufacturer/<int:manufacturer_id>/', delete_manufacturer, name='delete_manufacturer'),

    # skin types
    path('get_skin_types/', get_skin_types, name='get_skin_types'),
    path('add_skin_type/', add_skin_type, name='add_skin_type'),
    path('update_skin_type/<int:skin_type_id>/', update_skin_type, name='update_skin_type'),
    path('delete_skin_type/<int:skin_type_id>/', delete_skin_type, name='delete_skin_type'),

    # purposes
    path('get_purposes/', get_purposes, name='get_purposes'),
    path('add_purpose/', add_purpose, name='add_purpose'),
    path('update_purpose/<int:purpose_id>/', update_purpose, name='update_purpose'),
    path('delete_purpose/<int:purpose_id>/', delete_purpose, name='delete_purpose'),

    # collections
    path('get_collections/', get_collections, name='get_collections'),
    path('add_collection/', add_collection, name='add_collection'),
    path('update_collection/<int:collection_id>/', update_collection, name='update_collection'),
    path('delete_collection/<int:collection_id>/', delete_collection, name='delete_collection'),

]