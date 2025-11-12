from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .admin_views import AdminMenuView
from .views import (
    AdminJobPostingViewSet,
    CoverLetterDetailView,
    CoverLetterView,
    FindSimilarJobsView,
    GenerateCoverLetterView,
    GenerateResumeView,
    HideCompanyView,
    HideJobPostingView,
    JobPostingView,
    MeView,
    PinJobPostingView,
    RegisterView,
    ResumeDetailView,
    ResumeView,
    ScrapableDomainView,
    ScrapeHistoryView,
    ScrapeScheduleView,
    ScrapeView,
    SearchableJobTitleViewSet,
    TaskStatusView,
    UserCountView,
    UserViewSet,
    health_check,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"job-titles", SearchableJobTitleViewSet, basename="job-title")
router.register(r"admin/jobs", AdminJobPostingViewSet, basename="admin-job")

urlpatterns = [
    path("api/health/", health_check, name="health_check"),
    path("api/", include(router.urls)),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/admin/menu/", AdminMenuView.as_view(), name="admin_menu"),
    path("api/jobs/", JobPostingView.as_view(), name="job_postings"),
    path("api/jobs/hide/", HideJobPostingView.as_view(), name="hide_job_posting"),
    path("api/jobs/pin/", PinJobPostingView.as_view(), name="pin_job_posting"),
    path(
        "api/jobs/find-similar/",
        FindSimilarJobsView.as_view(),
        name="find_similar_jobs",
    ),
    path("api/companies/hide/", HideCompanyView.as_view(), name="hide_company"),
    path("api/resumes/", ResumeView.as_view(), name="resumes"),
    path("api/resumes/<int:pk>/", ResumeDetailView.as_view(), name="resume_detail"),
    path("api/cover-letters/", CoverLetterView.as_view(), name="cover_letters"),
    path(
        "api/cover-letters/<int:pk>/",
        CoverLetterDetailView.as_view(),
        name="cover_letter_detail",
    ),
    path("api/generate-resume/", GenerateResumeView.as_view(), name="generate_resume"),
    path(
        "api/generate-cover-letter/",
        GenerateCoverLetterView.as_view(),
        name="generate_cover_letter",
    ),
    path(
        "api/scrapable-domains/",
        ScrapableDomainView.as_view(),
        name="scrapable_domains",
    ),
    path("api/scrape/", ScrapeView.as_view(), name="scrape"),
    path(
        "api/task-status/<str:task_id>/", TaskStatusView.as_view(), name="task_status"
    ),
    path("api/scrape-history/", ScrapeHistoryView.as_view(), name="scrape_history"),
    path("api/scrape-schedule/", ScrapeScheduleView.as_view(), name="scrape-schedule"),
    path("api/user-count/", UserCountView.as_view(), name="user_count"),
]
