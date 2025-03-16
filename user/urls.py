# user/urls.py
from django.urls import path
from .views import RegisterView, LoginView, ProtectedView,RefreshTokenView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
]