from django.urls import path
from .views import RegisterView, JobPostingView
from .admin_views import AdminMenuView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/menu/', AdminMenuView.as_view(), name='admin_menu'),
    path('jobs/', JobPostingView.as_view(), name='job_postings'),
]
