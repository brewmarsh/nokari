from django.urls import path
from . import views

urlpatterns = [
    path('scrape/', views.scrape_view, name='scrape'),
    path('match/', views.match_resume_view, name='match_resume'),
]
