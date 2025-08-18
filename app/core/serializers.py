from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import JobPosting, Resume, CoverLetter, ScrapableDomain, ScrapeHistory, UserJobInteraction, HiddenCompany, SearchableJobTitle

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'preferred_work_arrangement')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
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
    is_pinned = serializers.BooleanField(read_only=True)

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

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except User.DoesNotExist:
            raise InvalidToken("User not found")

class ScrapeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeHistory
        fields = '__all__'

class UserJobInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserJobInteraction
        fields = '__all__'

class HiddenCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = HiddenCompany
        fields = '__all__'

class SearchableJobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchableJobTitle
        fields = '__all__'
