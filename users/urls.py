from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    generate_auth_token,
    login_or_register,
    confirm_phone_code,
    resend_code,
)

urlpatterns = [
    path('generate-auth/', generate_auth_token, name='generate_auth_token'),
    path('register/',login_or_register,),
    path('confirm/', confirm_phone_code, name='confirm_phone_code'),
    path('resend/', resend_code, name='resend_code'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
