from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import JobPosting, Resume, CoverLetter, ScrapableDomain, ScrapeHistory, UserJobInteraction, HiddenCompany, SearchableJobTitle, ScrapeSchedule

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
        user = User.objects.create_user(**validated_data)
        return user

class JobPostingSerializer(serializers.ModelSerializer):
    is_pinned = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'link',
            'company',
            'title',
            'description',
            'confidence_score',
            'posting_date',
            'locations',
            'days_in_office',
            'embedding',
            'details_updated_at',
            'is_pinned'
        ]

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

class AdminJobPostingSerializer(serializers.ModelSerializer):
    remote = serializers.BooleanField(read_only=True)
    hybrid = serializers.BooleanField(read_only=True)
    onsite = serializers.BooleanField(read_only=True)
    location_string = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            'link',
            'title',
            'company',
            'location_string',
            'remote',
            'hybrid',
            'onsite',
            'details_updated_at',
        ]

    def get_location_string(self, obj):
        # Find the first location with a non-empty location_string
        for loc in obj.locations:
            if loc.get('location_string'):
                return loc['location_string']
        return None

class ScrapeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeSchedule
        fields = ['time']
