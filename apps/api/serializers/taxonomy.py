from rest_framework import serializers
from apps.taxonomy.models import Industry, Capability, Market
from apps.entities.models import Company, Brand, Platform

class IndustrySerializer(serializers.ModelSerializer):
    companies = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    brands = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    platforms = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    foundations = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Industry
        fields = [
            "slug", "name", "description",
            "companies", "brands", "platforms", "foundations",
            "seo_title", "seo_description"
        ]

class CapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capability
        fields = ["slug", "group", "name", "description", "sort_order", "seo_title", "seo_description"]

class MarketSerializer(serializers.ModelSerializer):
    companies = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    brands = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    capabilities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Market
        # Notice: evidence_note is deliberately EXCLUDED for data governance / privacy!
        fields = ["region", "country", "status", "description", "show_cta", "companies", "brands", "capabilities"]
