from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobPosting, Resume, CoverLetter, ScrapableDomain

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
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
