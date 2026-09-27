from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    check_auth_status,
    generate_auth_token
)

urlpatterns = [
    path('generate-auth/', generate_auth_token),
    path('auth-status/<str:token>/', check_auth_status),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
