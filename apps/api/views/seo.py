from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, serializers
from drf_spectacular.utils import extend_schema

from apps.seo.models import Redirect, SeoGlobalSettings
from apps.entities.models import Company, Brand, Platform
from apps.content.models import Page, Article
from apps.careers.models import Career

class SitemapItemSerializer(serializers.Serializer):
    url = serializers.CharField()
    lastmod = serializers.CharField(required=False)
    changefreq = serializers.CharField(required=False)
    priority = serializers.FloatField(required=False)

class RedirectItemSerializer(serializers.Serializer):
    old_path = serializers.CharField()
    new_path = serializers.CharField()
    permanent = serializers.BooleanField()

class SitemapView(APIView):
    """
    Returns all indexable canonical URLs with last modified timestamps.
    Consumed by frontend sitemap.ts generator and search crawlers.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Dynamic XML/JSON Sitemap URLs", responses={200: SitemapItemSerializer(many=True)})
    def get(self, request):
        urls = [
            {"url": "/", "changefreq": "daily", "priority": 1.0},
            {"url": "/about", "changefreq": "weekly", "priority": 0.8},
            {"url": "/companies", "changefreq": "weekly", "priority": 0.9},
            {"url": "/brands", "changefreq": "weekly", "priority": 0.9},
            {"url": "/platforms", "changefreq": "weekly", "priority": 0.8},
            {"url": "/capabilities", "changefreq": "monthly", "priority": 0.7},
            {"url": "/industries", "changefreq": "monthly", "priority": 0.7},
            {"url": "/markets", "changefreq": "monthly", "priority": 0.7},
            {"url": "/people", "changefreq": "monthly", "priority": 0.6},
            {"url": "/impact", "changefreq": "monthly", "priority": 0.7},
            {"url": "/insights", "changefreq": "weekly", "priority": 0.8},
            {"url": "/careers", "changefreq": "daily", "priority": 0.7},
            {"url": "/partners", "changefreq": "monthly", "priority": 0.6},
            {"url": "/contact", "changefreq": "monthly", "priority": 0.7},
        ]

        # Add Pages (excluding home which is root '/')
        for page in Page.objects.public().filter(noindex=False):
            if page.slug != "home":
                urls.append({"url": f"/{page.slug}", "lastmod": page.updated_at.isoformat(), "priority": 0.7})

        # Add Companies (excluding noindex)
        for c in Company.objects.public().filter(noindex=False):
            urls.append({"url": f"/companies/{c.slug}", "lastmod": c.updated_at.isoformat(), "priority": 0.8})

        # Add Brands (excluding noindex)
        for b in Brand.objects.public().filter(noindex=False):
            urls.append({"url": f"/brands/{b.slug}", "lastmod": b.updated_at.isoformat(), "priority": 0.8})

        # Add Platforms (excluding noindex)
        for p in Platform.objects.public().filter(noindex=False):
            urls.append({"url": f"/platforms/{p.slug}", "lastmod": p.updated_at.isoformat(), "priority": 0.8})

        # Add Articles (excluding noindex)
        for a in Article.objects.public().filter(noindex=False):
            urls.append({"url": f"/insights/{a.slug}", "lastmod": a.updated_at.isoformat(), "priority": 0.7})

        # Add Careers
        for cr in Career.objects.public():
            urls.append({"url": f"/careers/{cr.slug}", "lastmod": cr.updated_at.isoformat(), "priority": 0.6})

        return Response(urls)


class RedirectsView(APIView):
    """
    Returns active redirect map for frontend reverse proxy or middleware.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Active SEO 301/302 Redirects", responses={200: RedirectItemSerializer(many=True)})
    def get(self, request):
        redirects = Redirect.objects.all().values("old_path", "new_path", "permanent")
        return Response(list(redirects))

class StructuredDataView(APIView):
    """
    Generates canonical JSON-LD Schema.org structured data for the SKAD Group Corporation.
    Per page 11 & 20 of SKAD Specification.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="JSON-LD Structured Data Schema", responses={200: dict})
    def get(self, request):
        seo_settings = SeoGlobalSettings.objects.first()
        org_name = seo_settings.schema_organization_name if seo_settings else "SKAD GROUP"
        same_as = seo_settings.schema_same_as if seo_settings else []

        companies = Company.objects.public()

        schema = {
            "@context": "https://schema.org",
            "@type": "Corporation",
            "name": org_name,
            "url": "https://skadgroup.com",
            "slogan": "BUILDING BUSINESSES. CREATING BRANDS. SHAPING THE FUTURE.",
            "description": "Diversified corporate ecosystem operating across jewellery, diamonds, manufacturing, beauty, fashion, international trade, and commerce platforms.",
            "sameAs": same_as,
            "subOrganization": [
                {
                    "@type": "Organization",
                    "name": c.legal_name,
                    "url": f"https://skadgroup.com/companies/{c.slug}",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": c.city or "Surat",
                        "addressCountry": c.country or "IN"
                    }
                }
                for c in companies
            ]
        }
        return Response(schema)
