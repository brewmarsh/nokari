import json
from django.core.management.base import BaseCommand
from app.core.models import ScrapableDomain, JobPosting

class Command(BaseCommand):
    help = 'Loads initial data from initial_data.json'

    def handle(self, *args, **options):
        with open('app/initial_data.json') as f:
            data = json.load(f)

        for domain_name in data['domains']:
            ScrapableDomain.objects.get_or_create(domain=domain_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully added domain "{domain_name}"'))

        for job_title in data['job_titles']:
            # Note: JobPosting requires a company, so we'll create dummy entries
            # This can be adjusted based on more specific requirements
            JobPosting.objects.get_or_create(
                link=f"http://default.com/{job_title.replace(' ', '-').lower()}",
                defaults={
                    'title': job_title,
                    'company': 'Default Company',
                    'description': 'Default description',
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added job title "{job_title}"'))
