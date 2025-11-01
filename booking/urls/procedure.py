from django.urls import path
from booking.views.procedure import add_procedure, update_procedure, delete_procedure

urlpatterns = [
    path('api/add_procedure/', add_procedure,),
    path('api/update_procedures/<int:procedure_id>/', update_procedure,),
    path('api/delete_procedures/<int:procedure_id>/delete/', delete_procedure,),
]
