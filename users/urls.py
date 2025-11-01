from django.urls import path
from users.views import (
    register_user,
    confirm_phone_code,
    resend_code,
    UpdateAvatarView,
)

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('confirm/', confirm_phone_code, name='confirm_phone_code'),
    path('resend/', resend_code, name='resend_code'),
    path('avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
]
