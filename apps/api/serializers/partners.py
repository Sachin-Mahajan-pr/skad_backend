from rest_framework import serializers
from apps.partners.models import Partner
from apps.foundation.models import FoundationInitiative

class PartnerSerializer(serializers.ModelSerializer):
    partner_type_display = serializers.CharField(source="get_partner_type_display", read_only=True)

    class Meta:
        model = Partner
        fields = ["name", "partner_type", "partner_type_display", "relationship_description", "logo", "website_url"]

class FoundationInitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundationInitiative
        fields = ["slug", "title", "focus_area", "status_label", "date", "verified_impact_details", "media"]
