from django.urls import path
from .views import RegisterView, JobPostingView, ResumeView, CoverLetterView, GenerateResumeView, GenerateCoverLetterView, ScrapableDomainView, ResumeDetailView, CoverLetterDetailView
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
    path('resumes/', ResumeView.as_view(), name='resumes'),
    path('resumes/<int:pk>/', ResumeDetailView.as_view(), name='resume_detail'),
    path('cover-letters/', CoverLetterView.as_view(), name='cover_letters'),
    path('cover-letters/<int:pk>/', CoverLetterDetailView.as_view(), name='cover_letter_detail'),
    path('generate-resume/', GenerateResumeView.as_view(), name='generate_resume'),
    path('generate-cover-letter/', GenerateCoverLetterView.as_view(), name='generate_cover_letter'),
    path('scrapable-domains/', ScrapableDomainView.as_view(), name='scrapable_domains'),
]
