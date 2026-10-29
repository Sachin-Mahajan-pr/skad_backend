from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.entities.models import (
    Group, Company, Brand, Platform, Venture, Foundation, Relationship
)
from apps.api.serializers.entities import (
    GroupSerializer, CompanySerializer, BrandSerializer, PlatformSerializer,
    VentureSerializer, FoundationSerializer
)

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("sort_order", "name")
    serializer_class = GroupSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

class BaseEntityViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from apps.core.utils import can_access_drafts
        if can_access_drafts(self.request):
            return self.queryset.all()
        return self.queryset.public()


class CompanyViewSet(BaseEntityViewSet):
    queryset = Company.objects.prefetch_related("capabilities", "industries")
    serializer_class = CompanySerializer
    filterset_fields = ["country", "sector", "industries__slug", "capabilities__slug"]
    search_fields = ["name", "legal_name", "company_type", "summary"]

class BrandViewSet(BaseEntityViewSet):
    queryset = Brand.objects.prefetch_related("capabilities", "industries")
    serializer_class = BrandSerializer
    filterset_fields = ["market_scope", "category", "industries__slug", "capabilities__slug"]
    search_fields = ["name", "tagline", "category", "summary"]

class PlatformViewSet(BaseEntityViewSet):
    queryset = Platform.objects.prefetch_related("capabilities", "industries")
    serializer_class = PlatformSerializer
    filterset_fields = ["industries__slug", "capabilities__slug"]
    search_fields = ["name", "tagline", "summary"]

class VentureViewSet(BaseEntityViewSet):
    queryset = Venture.objects.all()
    serializer_class = VentureSerializer

class FoundationViewSet(BaseEntityViewSet):
    queryset = Foundation.objects.all()
    serializer_class = FoundationSerializer

class EcosystemGraphView(APIView):
    """
    Returns the visual interactive ecosystem node & edge graph,
    plus an accessible flat-list alternative (per specification section 14).
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="SKAD Ecosystem Graph & Fallback",
        description="Returns nodes, edges, and accessible list structure for the interactive SKAD ecosystem.",
        responses={200: dict},
    )
    def get(self, request):
        show_all = bool(request.user and request.user.is_authenticated and request.user.is_staff)
        companies = Company.objects.all() if show_all else Company.objects.public()
        brands = Brand.objects.all() if show_all else Brand.objects.public()
        platforms = Platform.objects.all() if show_all else Platform.objects.public()
        ventures = Venture.objects.all() if show_all else Venture.objects.public()
        foundation = Foundation.objects.all() if show_all else Foundation.objects.public()

        nodes = [
            {"id": "skad-group", "name": "SKAD GROUP", "type": "group", "tagline": "BUILD • CONNECT • SCALE"}
        ]
        for c in companies:
            nodes.append({"id": f"comp-{c.slug}", "name": c.name, "type": "company", "slug": c.slug, "meta": c.company_type})
        for b in brands:
            nodes.append({"id": f"brand-{b.slug}", "name": b.name, "type": "brand", "slug": b.slug, "meta": b.category, "scope": b.market_scope})
        for p in platforms:
            nodes.append({"id": f"plat-{p.slug}", "name": p.name, "type": "platform", "slug": p.slug, "meta": p.tagline})
        for v in ventures:
            nodes.append({"id": f"vent-{v.slug}", "name": v.name, "type": "venture", "slug": v.slug, "meta": v.venture_type})
        for f in foundation:
            nodes.append({"id": f"found-{f.slug}", "name": f.name, "type": "foundation", "slug": f.slug, "meta": "Impact Initiative"})

        def get_node_id(obj):
            if hasattr(obj, "primary_line"):
                return "skad-group"
            prefix_map = {
                "company": "comp",
                "brand": "brand",
                "platform": "plat",
                "venture": "vent",
                "foundation": "found",
            }
            model_name = getattr(obj._meta, "model_name", "")
            prefix = prefix_map.get(model_name, "plat")
            return f"{prefix}-{obj.slug}"

        # Relationships
        rels = Relationship.objects.all() if show_all else Relationship.objects.filter(verified=True)
        edges = []
        for r in rels:
            if r.from_object and r.to_object:
                edges.append({
                    "from": get_node_id(r.from_object),
                    "to": get_node_id(r.to_object),
                    "relationship": r.relationship,
                    "label": r.get_relationship_display(),
                    "verified": r.verified,
                })

        return Response({
            "group": "SKAD GROUP",
            "nodes": nodes,
            "edges": edges,
            "accessible_list": {
                "companies": [c.name for c in companies],
                "brands": [b.name for b in brands],
                "platforms": [p.name for p in platforms],
                "ventures": [v.name for v in ventures],
                "impact": [f.name for f in foundation],
            }
        })
