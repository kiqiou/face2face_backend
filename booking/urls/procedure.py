from django.urls import path
from booking.views.procedure import add_procedure, update_procedure, delete_procedure

urlpatterns = [
    path('add_procedure/', add_procedure,),
    path('update_procedure/<int:procedure_id>/', update_procedure,),
    path('delete_procedure/<int:procedure_id>/', delete_procedure,),
]
