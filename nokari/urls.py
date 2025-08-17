from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.core.views import SearchableJobTitleViewSet

router = DefaultRouter()
router.register(r'admin/job-titles', SearchableJobTitleViewSet, basename='job_title')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include('app.core.urls')),
    path("api/", include(router.urls)),
]
