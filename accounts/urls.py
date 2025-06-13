from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from accounts.views import (
    RegisterUserAPIView,
    UserProfileView,
    DeleteAccountView, LogoutView
)

app_name = "accounts"

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name="login"),
    path('login/refresh/', TokenRefreshView.as_view(), name="refresh_token"),
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="user_profile"),
    path('delete-account/', DeleteAccountView.as_view(), name="delete_account"),
]
