from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import UserSerializer, JobPostingSerializer, ResumeSerializer, CoverLetterSerializer, ScrapableDomainSerializer
from django.contrib.auth import get_user_model
from .models import JobPosting, Resume, CoverLetter, ScrapableDomain
from rest_framework.views import APIView
from rest_framework.response import Response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class JobPostingView(generics.ListAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = JobPosting.objects.all()
        title = self.request.query_params.get('title')
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        company = self.request.query_params.get('company')
        if company is not None:
            queryset = queryset.filter(company__icontains=company)
        search = self.request.query_params.get('search')
        if search is not None:
            queryset = queryset.filter(description__icontains=search)

        resume = Resume.objects.filter(user=self.request.user).first()
        if resume:
            with open(resume.file.path, 'r') as f:
                resume_text = f.read()
            for job_posting in queryset:
                job_posting.confidence_score = match_resume(resume_text, job_posting.description)['scores'][0]
                job_posting.save()

        return queryset

class ResumeView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

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
        job_posting_id = request.data.get('job_posting_id')
        try:
            job_posting = JobPosting.objects.get(id=job_posting_id)
        except JobPosting.DoesNotExist:
            return Response({'error': 'Job posting not found'}, status=404)

        # This is a placeholder for the actual resume generation logic.
        generated_resume_text = f"This is a generated resume for the position of {job_posting.title} at {job_posting.company}."

        return Response({'resume_text': generated_resume_text})

class GenerateCoverLetterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        job_posting_id = request.data.get('job_posting_id')
        try:
            job_posting = JobPosting.objects.get(id=job_posting_id)
        except JobPosting.DoesNotExist:
            return Response({'error': 'Job posting not found'}, status=404)

        # This is a placeholder for the actual cover letter generation logic.
        generated_cover_letter_text = f"This is a generated cover letter for the position of {job_posting.title} at {job_posting.company}."

        return Response({'cover_letter_text': generated_cover_letter_text})

class ScrapableDomainView(generics.ListCreateAPIView):
    serializer_class = ScrapableDomainSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ScrapableDomain.objects.all()
