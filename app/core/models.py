import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        if "username" not in extra_fields or not extra_fields["username"]:
            extra_fields["username"] = email
        if "role" not in extra_fields:
            extra_fields["role"] = "user"
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10, choices=[("admin", "Admin"), ("user", "User")]
    )
    preferred_work_arrangement = models.JSONField(default=list)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class JobPosting(models.Model):
    link = models.URLField(primary_key=True)
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(default="")
    confidence_score = models.FloatField(default=0)
    posting_date = models.DateField(null=True, blank=True)
    locations = models.JSONField(default=list)
    days_in_office = models.IntegerField(blank=True, null=True)
    embedding = models.JSONField(null=True, blank=True)
    details_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="default_resume_name")
    file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CoverLetter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="default_cover_letter_name")
    file = models.FileField(upload_to="cover_letters/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ScrapableDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.domain


class ScrapeHistory(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failure", "Failure"),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    jobs_found = models.IntegerField(default=0)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Scrape by {self.user} at {self.timestamp} - {self.status}"


class UserJobInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    hidden = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "job_posting")


class HiddenCompany(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("user", "name")


class SearchableJobTitle(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class ScrapeSchedule(models.Model):
    """
    Singleton model to store the schedule for daily scraping.
    """

    time = models.TimeField(default=datetime.time(3, 0))  # Default to 3:00 AM

    def __str__(self):
        return f"Daily scrape scheduled at {self.time.strftime('%H:%M')}"

    def save(self, *args, **kwargs):
        """
        Ensure that there is only ever one instance of this model.
        """
        self.pk = 1
        super(ScrapeSchedule, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load the singleton instance.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
