from django.urls import path
from .views import MeView, RegisterView, JobPostingView, ResumeView, CoverLetterView, GenerateResumeView, GenerateCoverLetterView, ScrapableDomainView, ResumeDetailView, CoverLetterDetailView, test_page, ScrapeView, UserCountView, ScrapeHistoryView
from .admin_views import AdminMenuView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
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
    path('scrape/', ScrapeView.as_view(), name='scrape'),
    path('scrape-history/', ScrapeHistoryView.as_view(), name='scrape_history'),
    path('test/', test_page, name='test_page'),
    path('user-count/', UserCountView.as_view(), name='user_count'),
]
