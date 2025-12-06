from django.urls import path
from users.views import (
    login_or_register,
    confirm_phone_code,
    resend_code,
    update_avatar,
)

urlpatterns = [
    path('register/',login_or_register,),
    path('confirm/', confirm_phone_code, name='confirm_phone_code'),
    path('resend/', resend_code, name='resend_code'),
    path('<int:user_id>/avatar/', update_avatar),
]
