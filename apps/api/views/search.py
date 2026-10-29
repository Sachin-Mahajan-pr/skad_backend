from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.entities.models import Company, Brand, Platform
from apps.taxonomy.models import Capability, Industry
from apps.content.models import Article
from apps.careers.models import Career

class CrossEntitySearchView(APIView):
    """
    Unified multi-entity search endpoint across the SKAD corporate ecosystem.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Unified Cross-Entity Search",
        parameters=[
            OpenApiParameter(name="q", description="Search query string", required=True, type=str)
        ],
        responses={200: dict},
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query or len(query) < 2:
            return Response({"query": query, "results": []})

        show_all = bool(request.user and request.user.is_authenticated and request.user.is_staff)
        results = []

        # Search Companies
        c_qs = Company.objects.all() if show_all else Company.objects.public()
        for c in c_qs.filter(Q(name__icontains=query) | Q(legal_name__icontains=query) | Q(summary__icontains=query))[:5]:
            results.append({"type": "company", "title": c.name, "slug": c.slug, "snippet": c.summary[:140], "url": f"/companies/{c.slug}"})

        # Search Brands
        b_qs = Brand.objects.all() if show_all else Brand.objects.public()
        for b in b_qs.filter(Q(name__icontains=query) | Q(tagline__icontains=query) | Q(summary__icontains=query))[:5]:
            results.append({"type": "brand", "title": b.name, "slug": b.slug, "snippet": b.tagline or b.summary[:140], "url": f"/brands/{b.slug}"})

        # Search Platforms
        p_qs = Platform.objects.all() if show_all else Platform.objects.public()
        for p in p_qs.filter(Q(name__icontains=query) | Q(tagline__icontains=query) | Q(summary__icontains=query))[:5]:
            results.append({"type": "platform", "title": p.name, "slug": p.slug, "snippet": p.tagline, "url": f"/platforms/{p.slug}"})

        # Search Capabilities
        cap_qs = Capability.objects.all() if show_all else Capability.objects.public()
        for cap in cap_qs.filter(Q(name__icontains=query) | Q(description__icontains=query))[:5]:
            results.append({"type": "capability", "title": cap.name, "slug": cap.slug, "snippet": cap.description[:140], "url": "/capabilities"})

        # Search Articles
        art_qs = Article.objects.all() if show_all else Article.objects.public()
        for a in art_qs.filter(Q(title__icontains=query) | Q(body__icontains=query))[:5]:
            results.append({"type": "article", "title": a.title, "slug": a.slug, "snippet": a.excerpt[:140] if a.excerpt else a.body[:140], "url": f"/insights/{a.slug}"})

        return Response({
            "query": query,
            "count": len(results),
            "results": results,
        })
