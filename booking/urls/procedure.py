from django.urls import path
from booking.views.procedure import add_procedure, update_procedure, delete_procedure, list_procedures, list_procedures_by_cosmetologist

urlpatterns = [
    path('get_procedures/', list_procedures,),
    path('get_procedures_by_cosmetologist/<int:cosmetologist_id>/', list_procedures_by_cosmetologist),
    path('add_procedure/', add_procedure,),
    path('update_procedure/<int:procedure_id>/', update_procedure,),
    path('delete_procedure/<int:procedure_id>/', delete_procedure,),
]
