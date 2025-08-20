from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .permissions import IsAdmin
from .serializers import UserSerializer, JobPostingSerializer, ResumeSerializer, CoverLetterSerializer, ScrapableDomainSerializer, ScrapeHistorySerializer, UserJobInteractionSerializer, HiddenCompanySerializer, SearchableJobTitleSerializer
from django.contrib.auth import get_user_model
from .models import JobPosting, Resume, CoverLetter, ScrapableDomain, ScrapeHistory, UserJobInteraction, HiddenCompany, SearchableJobTitle
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .scraper import scrape_jobs
import numpy as np
from numpy.linalg import norm
import threading
from django.db.models import OuterRef, Subquery, BooleanField, Value
from django.db.models.functions import Coalesce
from transformers import AutoTokenizer, AutoModel
import torch

User = get_user_model()

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def generate_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    embeddings = outputs.last_hidden_state
    mask = inputs['attention_mask'].unsqueeze(-1).expand(embeddings.size()).float()
    masked_embeddings = embeddings * mask
    summed = torch.sum(masked_embeddings, 1)
    counted = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / counted

    # Normalize
    mean_pooled = torch.nn.functional.normalize(mean_pooled, p=2, dim=1)
    return mean_pooled.tolist()[0]

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
            user=user,
            job_posting=OuterRef('pk')
        ).values('pinned')
        queryset = JobPosting.objects.annotate(
            is_pinned=Coalesce(Subquery(pinned_status, output_field=BooleanField()), Value(False))
        ).order_by('-is_pinned')

        hidden_job_postings = UserJobInteraction.objects.filter(user=user, hidden=True).values_list('job_posting_id', flat=True)
        hidden_companies = HiddenCompany.objects.filter(user=user).values_list('name', flat=True)
        queryset = queryset.exclude(link__in=hidden_job_postings).exclude(company__in=hidden_companies)
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
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = ScrapableDomain.objects.all()


class ScrapeHistoryView(generics.ListAPIView):
    serializer_class = ScrapeHistorySerializer
    permission_classes = [IsAdmin]
    queryset = ScrapeHistory.objects.all().order_by('-timestamp')

class ScrapeView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        days = request.data.get('days')
        scraped_count = 0
        try:
            domains = ScrapableDomain.objects.all()
            job_titles = SearchableJobTitle.objects.all()
            if not job_titles:
                return Response({'detail': 'No job titles to search for.'}, status=status.HTTP_400_BAD_REQUEST)

            query_parts = [f'"{title.title}"' for title in job_titles]
            query = f'({" OR ".join(query_parts)}) AND "remote"'

            for domain in domains:
                jobs = scrape_jobs(query, domain.domain, days=days)
                for job_data in jobs:
                    title = job_data['title']
                    if 'Job Application for' in title:
                        title = title.replace('Job Application for', '').strip()

                    obj, created = JobPosting.objects.get_or_create(
                        link=job_data['link'],
                        defaults={
                            'title': title,
                            'company': job_data['company'],
                            'description': job_data['description'],
                            'posting_date': job_data['posting_date'],
                            'locations': job_data['locations'],
                        }
                    )
                    if created:
                        text = f"{obj.title} {obj.description}"
                        obj.embedding = generate_embedding(text)
                        obj.save()
                        scraped_count += 1
            ScrapeHistory.objects.create(
                user=request.user,
                status='success',
                jobs_found=scraped_count
            )
            return Response({'detail': f'Scraped {scraped_count} new jobs.'})
        except Exception as e:
            ScrapeHistory.objects.create(
                user=request.user,
                status='failure',
                details=str(e)
            )
            return Response({'detail': f'An error occurred: {e}'}, status=500)


def test_page(request):
    User = get_user_model()
    user = User.objects.first()
    return render(request, 'test_page.html', {'user': user})

class UserCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({'user_count': User.objects.count()})

class HideJobPostingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserJobInteractionSerializer

    def post(self, request, *args, **kwargs):
        job_posting_link = request.data.get('job_posting_link')
        if not job_posting_link:
            return Response({'error': 'Job posting link not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_posting = JobPosting.objects.get(link=job_posting_link)
        except JobPosting.DoesNotExist:
            return Response({'error': 'Job posting not found'}, status=status.HTTP_404_NOT_FOUND)

        interaction, created = UserJobInteraction.objects.get_or_create(
            user=request.user,
            job_posting=job_posting
        )

        interaction.hidden = True
        interaction.save()

        return Response(status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        user = self.get_object()
        user.role = 'admin'
        user.save()
        return Response({'status': 'user promoted'})

import numpy as np
from numpy.linalg import norm

def scrape_in_background(query):
    domains = ScrapableDomain.objects.all()
    for domain in domains:
        try:
            jobs = scrape_jobs(query, domain.domain)
            for job_data in jobs:
                obj, created = JobPosting.objects.get_or_create(
                    link=job_data['link'],
                    defaults={
                        'title': job_data['title'],
                        'company': job_data['company'],
                        'description': job_data['description'],
                        'posting_date': job_data['posting_date'],
                        'locations': job_data['locations'],
                    }
                )
                if created:
                    text = f"{obj.title} {obj.description}"
                    obj.embedding = generate_embedding(text)
                    obj.save()
        except Exception as e:
            # In a real app, you'd want to log this properly
            print(f"Error scraping in background {domain.domain}: {e}")

class FindSimilarJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        job_pk = kwargs.get('pk')
        try:
            target_job = JobPosting.objects.get(pk=job_pk)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND)

        # --- Part 1: Find and return similar jobs immediately ---
        if not target_job.embedding:
            return Response({"error": "Target job has no embedding."}, status=status.HTTP_400_BAD_REQUEST)

        all_jobs = JobPosting.objects.exclude(pk=target_job.pk).exclude(embedding__isnull=True)
        target_embedding = np.array(target_job.embedding)
        similar_jobs = []
        for job in all_jobs:
            if job.embedding and isinstance(job.embedding, (list, tuple)):
                job_embedding = np.array(job.embedding)
                target_norm = norm(target_embedding)
                job_norm = norm(job_embedding)

                if target_norm > 0 and job_norm > 0:
                    cosine_similarity = np.dot(target_embedding, job_embedding) / (target_norm * job_norm)
                    similar_jobs.append((job, cosine_similarity))

        similar_jobs.sort(key=lambda x: x[1], reverse=True)
        top_jobs = [job for job, score in similar_jobs[:5]]
        serializer = JobPostingSerializer(top_jobs, many=True)

        # --- Part 2: Kick off background scraping ---
        query = f'"{target_job.title}"'
        thread = threading.Thread(target=scrape_in_background, args=(query,))
        thread.daemon = True
        thread.start()

        return Response(serializer.data)

class SearchableJobTitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = SearchableJobTitleSerializer
    queryset = SearchableJobTitle.objects.all()

class HideCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HiddenCompanySerializer

    def post(self, request, *args, **kwargs):
        company_name = request.data.get('name')
        if not company_name:
            return Response({'error': 'Company name not provided'}, status=status.HTTP_400_BAD_REQUEST)

        hidden_company, created = HiddenCompany.objects.get_or_create(
            user=request.user,
            name=company_name
        )

        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_200_OK)

class PinJobPostingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserJobInteractionSerializer

    def post(self, request, *args, **kwargs):
        job_posting_link = request.data.get('job_posting_link')
        pinned = request.data.get('pinned', False)

        if not job_posting_link:
            return Response({'error': 'Job posting link not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_posting = JobPosting.objects.get(link=job_posting_link)
        except JobPosting.DoesNotExist:
            return Response({'error': 'Job posting not found'}, status=status.HTTP_404_NOT_FOUND)

        interaction, created = UserJobInteraction.objects.get_or_create(
            user=request.user,
            job_posting=job_posting
        )

        interaction.pinned = pinned
        interaction.save()

        return Response(status=status.HTTP_200_OK)
