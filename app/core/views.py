"""Core views for the Nokari application."""

from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CoverLetter,
    JobPosting,
    Resume,
    ScrapableDomain,
    ScrapeHistory,
)
from .permissions import IsAdmin
from .scraper import scrape_jobs
from .serializers import (
    CoverLetterSerializer,
    JobPostingSerializer,
    ResumeSerializer,
    ScrapableDomainSerializer,
    ScrapeHistorySerializer,
    UserSerializer,
)

User = get_user_model()


class MeView(generics.RetrieveAPIView):
    """A view to retrieve the authenticated user's information."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user


class RegisterView(generics.CreateAPIView):
    """A view to register a new user."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class JobPostingView(generics.ListAPIView):
    """A view to list and filter job postings."""

    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get the queryset for job postings, filtering by title, company, and description.
        """
        queryset = JobPosting.objects.all()
        title = self.request.query_params.get("title")
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        company = self.request.query_params.get("company")
        if company is not None:
            queryset = queryset.filter(company__icontains=company)
        search = self.request.query_params.get("search")
        if search is not None:
            queryset = queryset.filter(description__icontains=search)

        # TODO: The match_resume function is not defined. This feature seems
        # to be incomplete.
        # resume = Resume.objects.filter(user=self.request.user).first()
        # if resume:
        #     with open(resume.file.path, "r") as f:
        #         resume_text = f.read()
        #     for job_posting in queryset:
        #         job_posting.confidence_score = match_resume(
        #             resume_text, job_posting.description
        #         )["scores"][0]
        #         job_posting.save()

        return queryset


class ResumeView(generics.ListCreateAPIView):
    """A view to list and create resumes for the authenticated user."""

    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the resumes for the authenticated user."""
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate the resume with the authenticated user."""
        serializer.save(user=self.request.user)


class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """A view to retrieve, update, or delete a resume."""

    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the resumes for the authenticated user."""
        return Resume.objects.filter(user=self.request.user)


class CoverLetterView(generics.ListCreateAPIView):
    """A view to list and create cover letters for the authenticated user."""

    serializer_class = CoverLetterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the cover letters for the authenticated user."""
        return CoverLetter.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate the cover letter with the authenticated user."""
        serializer.save(user=self.request.user)


class CoverLetterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """A view to retrieve, update, or delete a cover letter."""

    serializer_class = CoverLetterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the cover letters for the authenticated user."""
        return CoverLetter.objects.filter(user=self.request.user)


class GenerateResumeView(APIView):
    """A view to generate a resume for a job posting."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Generate a resume based on a job posting.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the generated resume text.
        """
        job_posting_id = request.data.get("job_posting_id")
        try:
            job_posting = JobPosting.objects.get(id=job_posting_id)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found"}, status=404)

        # This is a placeholder for the actual resume generation logic.
        generated_resume_text = (
            f"This is a generated resume for the position of "
            f"{job_posting.title} at {job_posting.company}."
        )

        return Response({"resume_text": generated_resume_text})


class GenerateCoverLetterView(APIView):
    """A view to generate a cover letter for a job posting."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Generate a cover letter based on a job posting.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the generated cover letter text.
        """
        job_posting_id = request.data.get("job_posting_id")
        try:
            job_posting = JobPosting.objects.get(id=job_posting_id)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found"}, status=404)

        # This is a placeholder for the actual cover letter generation logic.
        generated_cover_letter_text = (
            f"This is a generated cover letter for the position of "
            f"{job_posting.title} at {job_posting.company}."
        )

        return Response({"cover_letter_text": generated_cover_letter_text})


class ScrapableDomainView(generics.ListCreateAPIView):
    """A view to list and create scrapable domains."""

    serializer_class = ScrapableDomainSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = ScrapableDomain.objects.all()


class ScrapeHistoryView(generics.ListAPIView):
    """A view to list the scrape history."""

    serializer_class = ScrapeHistorySerializer
    permission_classes = [IsAdmin]
    queryset = ScrapeHistory.objects.all().order_by("-timestamp")


class ScrapeView(APIView):
    """A view to trigger a scrape of all scrapable domains."""

    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        """
        Trigger a scrape of all scrapable domains.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating the result of the scrape.
        """
        scraped_count = 0
        try:
            domains = ScrapableDomain.objects.all()
            query = '"director of product" AND "remote"'
            for domain in domains:
                jobs = scrape_jobs(query, domain.domain)
                for job_data in jobs:
                    obj, created = JobPosting.objects.get_or_create(
                        link=job_data["link"],
                        defaults={
                            "title": job_data["title"],
                            "company": job_data["company"],
                            "description": job_data["description"],
                        },
                    )
                    if created:
                        scraped_count += 1
            ScrapeHistory.objects.create(
                user=request.user, status="success", jobs_found=scraped_count
            )
            return Response({"detail": f"Scraped {scraped_count} new jobs."})
        except Exception as e:
            ScrapeHistory.objects.create(
                user=request.user, status="failure", details=str(e)
            )
            return Response({"detail": f"An error occurred: {e}"}, status=500)


def test_page(request):
    """A view to render a test page."""
    User = get_user_model()
    user = User.objects.first()
    return render(request, "test_page.html", {"user": user})


class UserCountView(APIView):
    """A view to get the total number of users."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Return the total number of users.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the user count.
        """
        return Response({"user_count": User.objects.count()})


class HealthCheckView(APIView):
    """A view to check the health of the application."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Return a health check response.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating the application is healthy.
        """
        return Response({"status": "ok"})
