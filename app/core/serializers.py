from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobPosting, Resume, CoverLetter, ScrapableDomain, ScrapeHistory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True},
        }

    def create(self, validated_data):
        is_superuser = self.initial_data.get('is_superuser', False)
        if is_superuser:
            user = User.objects.create_superuser(**validated_data)
        else:
            user = User.objects.create_user(**validated_data)
        return user

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'

class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = '__all__'

class ScrapableDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapableDomain
        fields = '__all__'

class ScrapeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeHistory
        fields = '__all__'
