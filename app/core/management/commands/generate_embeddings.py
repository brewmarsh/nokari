from django.core.management.base import BaseCommand
from app.core.models import JobPosting
from transformers import AutoTokenizer, AutoModel
import torch


class Command(BaseCommand):
    help = "Generates embeddings for all job postings"

    def handle(self, *args, **options):
        self.stdout.write("Loading model...")
        tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.stdout.write("Model loaded.")

        job_postings = JobPosting.objects.all()
        for job_posting in job_postings:
            if job_posting.embedding is not None:
                self.stdout.write(
                    f"Embedding already exists for job: {job_posting.title}, skipping."
                )
                continue

            self.stdout.write(f"Generating embedding for job: {job_posting.title}")
            text = f"{job_posting.title} {job_posting.description}"
            inputs = tokenizer(
                text, return_tensors="pt", truncation=True, max_length=512
            )
            with torch.no_grad():
                outputs = model(**inputs)

            # Mean pooling
            embeddings = outputs.last_hidden_state
            mask = (
                inputs["attention_mask"].unsqueeze(-1).expand(embeddings.size()).float()
            )
            masked_embeddings = embeddings * mask
            summed = torch.sum(masked_embeddings, 1)
            counted = torch.clamp(mask.sum(1), min=1e-9)
            mean_pooled = summed / counted

            # Normalize
            mean_pooled = torch.nn.functional.normalize(mean_pooled, p=2, dim=1)

            job_posting.embedding = mean_pooled.tolist()[0]
            job_posting.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully generated embeddings for all job postings."
            )
        )
