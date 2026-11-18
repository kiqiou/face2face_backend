from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    check_auth_status,
    generate_auth_token,
    my_skin_type,
    update_profile_name
)

urlpatterns = [
    path('generate-auth/', generate_auth_token),
    path('update-name/', update_profile_name),
    path('my_skin_type/', my_skin_type),
    path('auth-status/<str:token>/', check_auth_status),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
