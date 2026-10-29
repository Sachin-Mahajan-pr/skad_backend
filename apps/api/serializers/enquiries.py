import uuid
import requests
from django.conf import settings
from rest_framework import serializers

from apps.enquiries.models import EnquiryRoute, Enquiry, Opportunity, Subscription

def verify_turnstile_token(token: str, ip: str = "") -> bool:
    """Verifies Cloudflare Turnstile captcha token."""
    secret = getattr(settings, "TURNSTILE_SECRET_KEY", "")
    if not secret or not getattr(settings, "TURNSTILE_ENABLED", False):
        return True
    if not token:
        return False
    try:
        resp = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": secret, "response": token, "remoteip": ip},
            timeout=5,
        )
        return resp.json().get("success", False)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Captcha verification exception: %s", exc)
        return False

class EnquiryRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryRoute
        fields = ["code", "label", "active"]

class EnquiryCreateSerializer(serializers.ModelSerializer):
    route_code = serializers.CharField(write_only=True)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True) # Honeypot field
    turnstile_token = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Enquiry
        fields = [
            "reference", "route_code", "name", "company", "role", "email",
            "phone", "country", "company_website", "message", "attachment",
            "website", "turnstile_token", "created_at"
        ]
        read_only_fields = ["reference", "created_at"]

    def validate_route_code(self, value):
        try:
            route = EnquiryRoute.objects.get(code=value, active=True)
            return route
        except EnquiryRoute.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive enquiry routing destination.")

    def validate(self, attrs):
        # 1. Honeypot defense (page 12 & 13)
        if attrs.get("website"):
            raise serializers.ValidationError("Submission flagged by security filters.")

        # 2. Captcha token verification (if enabled)
        token = attrs.get("turnstile_token", "")
        if getattr(settings, "TURNSTILE_ENABLED", False) and not verify_turnstile_token(token):
            raise serializers.ValidationError({"turnstile_token": "Captcha validation failed."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("website", None)
        validated_data.pop("turnstile_token", None)
        route = validated_data.pop("route_code")
        return Enquiry.objects.create(route=route, **validated_data)

class OpportunityCreateSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)  # Honeypot

    class Meta:
        model = Opportunity
        fields = [
            "id", "opportunity_type", "name", "email", "company",
            "company_website", "summary", "attachment", "website", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        if attrs.get("website"):
            raise serializers.ValidationError("Submission flagged by security filters.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["email", "confirmed"]
        read_only_fields = ["confirmed"]

    def create(self, validated_data):
        validated_data["opt_in_token"] = uuid.uuid4().hex
        return super().create(validated_data)
