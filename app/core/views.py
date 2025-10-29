from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .permissions import IsAdmin
from .serializers import (
    UserSerializer,
    JobPostingSerializer,
    ResumeSerializer,
    CoverLetterSerializer,
    ScrapableDomainSerializer,
    ScrapeHistorySerializer,
    UserJobInteractionSerializer,
    HiddenCompanySerializer,
    SearchableJobTitleSerializer,
    AdminJobPostingSerializer,
    ScrapeScheduleSerializer,
)
from django.contrib.auth import get_user_model
from .models import (
    JobPosting,
    Resume,
    CoverLetter,
    ScrapableDomain,
    ScrapeHistory,
    UserJobInteraction,
    HiddenCompany,
    SearchableJobTitle,
    ScrapeSchedule,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .tasks import (
    scrape_and_save_jobs_task,
    rescrape_job_details_task,
    analyze_resume_against_jobs,
)
from celery.result import AsyncResult
import numpy as np
from numpy.linalg import norm
import threading
from django.db.models import OuterRef, Subquery, BooleanField, Value, Q, Case, When
from django.db.models.functions import Coalesce
from urllib.parse import unquote
from .ml_utils import generate_embedding

User = get_user_model()


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class JobPostingView(generics.ListAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Annotate with pinned status
        pinned_status = UserJobInteraction.objects.filter(
            user=user, job_posting=OuterRef("pk")
        ).values("pinned")
        queryset = JobPosting.objects.annotate(
            is_pinned=Coalesce(
                Subquery(pinned_status, output_field=BooleanField()), Value(False)
            )
        ).order_by("-is_pinned")

        hidden_job_postings = UserJobInteraction.objects.filter(
            user=user, hidden=True
        ).values_list("job_posting_id", flat=True)
        hidden_companies = HiddenCompany.objects.filter(user=user).values_list(
            "name", flat=True
        )
        queryset = queryset.exclude(link__in=hidden_job_postings).exclude(
            company__in=hidden_companies
        )
        title = self.request.query_params.get("title")
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        company = self.request.query_params.get("company")
        if company is not None:
            queryset = queryset.filter(company__icontains=company)
        search = self.request.query_params.get("search")
        if search is not None:
            queryset = queryset.filter(description__icontains=search)

        preferences = user.preferred_work_arrangement
        if preferences:
            q_objects = Q()
            # Handle specific preferences
            if "remote" in preferences:
                q_objects |= Q(locations__contains=[{"type": "remote"}])
            if "hybrid" in preferences:
                q_objects |= Q(locations__contains=[{"type": "hybrid"}])
            if "onsite" in preferences:
                q_objects |= Q(locations__contains=[{"type": "onsite"}])

            # Handle 'unspecified'
            if "unspecified" in preferences:
                # This logic finds jobs that are not explicitly remote, hybrid, or onsite
                q_objects |= (
                    ~Q(locations__contains=[{"type": "remote"}])
                    & ~Q(locations__contains=[{"type": "hybrid"}])
                    & ~Q(locations__contains=[{"type": "onsite"}])
                )

            if q_objects:
                queryset = queryset.filter(q_objects)

        # The confidence score is now calculated asynchronously by a Celery task
        # triggered on resume upload. This view no longer needs to perform
        # this calculation.

        return queryset


class ResumeView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        analyze_resume_against_jobs.delay(self.request.user.id)


class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        analyze_resume_against_jobs.delay(self.request.user.id)


class CoverLetterView(generics.ListCreateAPIView):
    serializer_class = CoverLetterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoverLetter.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoverLetterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CoverLetterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoverLetter.objects.filter(user=self.request.user)


class GenerateResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        job_posting_id = request.data.get("job_posting_id")
        try:
            job_posting = JobPosting.objects.get(id=job_posting_id)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found"}, status=404)

        # This is a placeholder for the actual resume generation logic.
        generated_resume_text = f"This is a generated resume for the position of {job_posting.title} at {job_posting.company}."

        return Response({"resume_text": generated_resume_text})


class GenerateCoverLetterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        job_posting_id = request.data.get("job_posting_id")
        try:
            job_posting = JobPosting.objects.get(id=job_posting_id)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found"}, status=404)

        # This is a placeholder for the actual cover letter generation logic.
        generated_cover_letter_text = f"This is a generated cover letter for the position of {job_posting.title} at {job_posting.company}."

        return Response({"cover_letter_text": generated_cover_letter_text})


class ScrapableDomainView(generics.ListCreateAPIView):
    serializer_class = ScrapableDomainSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = ScrapableDomain.objects.all()


class ScrapeHistoryView(generics.ListAPIView):
    serializer_class = ScrapeHistorySerializer
    permission_classes = [IsAdmin]
    queryset = ScrapeHistory.objects.all().order_by("-timestamp")


class ScrapeView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        domains = ScrapableDomain.objects.all()
        if not domains.exists():
            return Response(
                {"detail": "No scrapable domains configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task_ids = []
        for domain in domains:
            task = scrape_and_save_jobs_task.delay(domain.id)
            task_ids.append(task.id)

        return Response(
            {"detail": "Scraping tasks initiated.", "task_ids": task_ids},
            status=status.HTTP_202_ACCEPTED,
        )


class TaskStatusView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get("task_id")
        if not task_id:
            return Response(
                {"error": "Task ID not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        task_result = AsyncResult(task_id)

        result = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result,
        }
        return Response(result, status=status.HTTP_200_OK)


class UserCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"user_count": User.objects.count()})


class HideJobPostingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserJobInteractionSerializer

    def post(self, request, *args, **kwargs):
        job_posting_link = request.data.get("job_posting_link")
        if not job_posting_link:
            return Response(
                {"error": "Job posting link not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            job_posting = JobPosting.objects.get(link=job_posting_link)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND
            )

        interaction, created = UserJobInteraction.objects.get_or_create(
            user=request.user, job_posting=job_posting
        )

        interaction.hidden = True
        interaction.save()

        return Response(status=status.HTTP_200_OK)


class ScrapeScheduleView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for managing the daily scrape schedule.
    """

    permission_classes = [IsAdmin]
    serializer_class = ScrapeScheduleSerializer

    def get_object(self):
        return ScrapeSchedule.load()


class AdminJobPostingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for admins to view and manage job postings.
    """

    queryset = JobPosting.objects.all().order_by("-details_updated_at", "-posting_date")
    serializer_class = AdminJobPostingSerializer
    permission_classes = [IsAdmin]
    lookup_field = "link"
    lookup_value_regex = ".+"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    @action(detail=True, methods=["put"])
    def rescrape(self, request, pk=None):
        """
        Triggers a Celery task to rescrape the details of a single job posting.
        """
        job = self.get_object()
        task = rescrape_job_details_task.delay(job.pk)
        return Response({"status": "rescrape_task_started", "task_id": task.id})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=["post"])
    def promote(self, request, pk=None):
        user = self.get_object()
        user.role = "admin"
        user.save()
        return Response({"status": "user promoted"})


class FindSimilarJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        job_pk = request.data.get("link")
        if not job_pk:
            return Response(
                {"error": "Link not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_job = JobPosting.objects.get(pk=job_pk)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # --- Part 1: Find and return similar jobs immediately ---
        if not target_job.embedding:
            return Response(
                {"error": "Target job has no embedding."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_jobs = JobPosting.objects.exclude(pk=target_job.pk).exclude(
            embedding__isnull=True
        )
        target_embedding = np.array(target_job.embedding)
        similar_jobs = []
        for job in all_jobs:
            if job.embedding and isinstance(job.embedding, (list, tuple)):
                job_embedding = np.array(job.embedding)
                target_norm = norm(target_embedding)
                job_norm = norm(job_embedding)

                if target_norm > 0 and job_norm > 0:
                    cosine_similarity = np.dot(target_embedding, job_embedding) / (
                        target_norm * job_norm
                    )
                    similar_jobs.append((job, cosine_similarity))

        similar_jobs.sort(key=lambda x: x[1], reverse=True)
        top_jobs = [job for job, score in similar_jobs if score > 0.7][:5]
        serializer = JobPostingSerializer(top_jobs, many=True)

        # --- Part 2: Kick off background scraping ---
        query = f'"{target_job.title}"'
        scrape_and_save_jobs_task.delay(query)

        return Response(serializer.data)


class SearchableJobTitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = SearchableJobTitleSerializer
    queryset = SearchableJobTitle.objects.all()


class HideCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HiddenCompanySerializer

    def post(self, request, *args, **kwargs):
        company_name = request.data.get("name")
        if not company_name:
            return Response(
                {"error": "Company name not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hidden_company, created = HiddenCompany.objects.get_or_create(
            user=request.user, name=company_name
        )

        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_200_OK)


class PinJobPostingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserJobInteractionSerializer

    def post(self, request, *args, **kwargs):
        job_posting_link = request.data.get("job_posting_link")
        pinned = request.data.get("pinned", False)

        if not job_posting_link:
            return Response(
                {"error": "Job posting link not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            job_posting = JobPosting.objects.get(link=job_posting_link)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND
            )

        interaction, created = UserJobInteraction.objects.get_or_create(
            user=request.user, job_posting=job_posting
        )

        interaction.pinned = pinned
        interaction.save()

        return Response(status=status.HTTP_200_OK)
