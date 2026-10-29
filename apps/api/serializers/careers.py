from rest_framework import serializers
from apps.careers.models import Career, Application
from apps.core.validators import validate_secure_file_upload

class CareerSerializer(serializers.ModelSerializer):
    department_display = serializers.CharField(source="get_department_display", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)

    class Meta:
        model = Career
        fields = [
            "slug", "title", "department", "department_display", "location",
            "employment_type", "description", "requirements", "company_name",
            "application_route", "external_apply_url", "closes_on", "publish_at"
        ]

class ApplicationCreateSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)  # Honeypot bot protection

    class Meta:
        model = Application
        fields = ["career", "candidate_name", "email", "phone", "linkedin_profile", "cv_file", "cover_letter", "consent_recorded", "website"]
        extra_kwargs = {
            "consent_recorded": {"required": True},
        }

    def validate_cv_file(self, value):
        if value:
            validate_secure_file_upload(value, max_mb=10, allowed_extensions={".pdf", ".docx", ".doc"})
        return value

    def validate_consent_recorded(self, value):
        if not value:
            raise serializers.ValidationError("Consent must be accepted to submit job application.")
        return value

    def validate(self, attrs):
        if attrs.get("website"):
            raise serializers.ValidationError("Submission flagged by security filters.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)
