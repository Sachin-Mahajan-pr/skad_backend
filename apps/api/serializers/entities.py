from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.entities.models import Group, Company, Brand, Platform, Venture, Foundation, Relationship

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "slug", "name", "primary_line", "operating_philosophy",
            "at_a_glance_facts", "summary", "body", "seo_title", "seo_description"
        ]

class CompanyRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["slug", "name", "legal_name", "company_type", "sector", "city", "country"]

class BrandRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["slug", "name", "tagline", "category", "market_scope", "cta_label", "website_url"]

class CompanySerializer(serializers.ModelSerializer):
    brands = serializers.SerializerMethodField()
    capabilities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    industries = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Company
        fields = [
            "slug", "name", "legal_name", "company_type", "sector", "city", "country",
            "summary", "body", "external_url", "hero_image", "capabilities", "industries",
            "brands", "seo_title", "seo_description", "canonical_url"
        ]

    @extend_schema_field(BrandRefSerializer(many=True))
    def get_brands(self, obj):
        brands = obj.verified_brands
        return BrandRefSerializer(brands, many=True).data

class BrandSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    capabilities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    industries = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Brand
        fields = [
            "slug", "name", "tagline", "category", "market_scope", "positioning",
            "target_market", "summary", "body", "theme", "website_url", "cta_label",
            "logo", "company", "capabilities", "industries", "seo_title", "seo_description",
            "canonical_url"
        ]

    @extend_schema_field(CompanyRefSerializer)
    def get_company(self, obj):
        rel = obj.verified_company_relationship()
        if rel and rel.from_object:
            return CompanyRefSerializer(rel.from_object).data
        return None

class PlatformSerializer(serializers.ModelSerializer):
    capabilities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    sits_within = serializers.SerializerMethodField()

    class Meta:
        model = Platform
        fields = [
            "slug", "name", "tagline", "status", "purpose", "summary", "body",
            "logo", "cta_label", "capabilities", "sits_within", "seo_title", "seo_description"
        ]

    @extend_schema_field(CompanyRefSerializer)
    def get_sits_within(self, obj):
        from apps.entities.models import RelationshipType
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        rel = Relationship.objects.filter(
            from_type=ct,
            from_id=obj.id,
            relationship=RelationshipType.SITS_WITHIN,
            verified=True,
        ).first()
        if rel and rel.to_object:
            return CompanyRefSerializer(rel.to_object).data
        return None

class VentureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venture
        fields = ["slug", "name", "venture_type", "stage_label", "summary", "body", "seo_title", "seo_description"]

class FoundationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foundation
        fields = ["slug", "name", "mission", "summary", "body", "seo_title", "seo_description"]
