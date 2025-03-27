from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    ProtectedView,
    RefreshTokenView,
    UserManagementView,
    UserDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('users/', UserManagementView.as_view(), name='user-management'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
]