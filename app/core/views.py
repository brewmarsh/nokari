from django.shortcuts import render
from .scraper import scrape_jobs
from .matcher import match_resume
from django.http import JsonResponse
import json

def scrape_view(request):
    # This is a placeholder for the actual view logic.
    # You will need to create a form for administrators to enter a URL to scrape.
    if request.method == 'POST':
        url = request.POST.get('url')
        jobs = scrape_jobs(url)
        return render(request, 'scraper_results.html', {'jobs': jobs})
    return render(request, 'scrape_form.html')

def match_resume_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        resume_text = data.get('resume_text')
        job_description_text = data.get('job_description_text')

        if resume_text and job_description_text:
            result = match_resume(resume_text, job_description_text)
            return JsonResponse(result)
        else:
            return JsonResponse({'error': 'Missing resume_text or job_description_text'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
