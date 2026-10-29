from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.content.models import Page, UIString, SiteSettings, ThemeToken, FeatureFlag
from apps.api.serializers.content import PageSerializer, SiteSettingsSerializer
from apps.entities.models import Company, Brand, Platform

class PageViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = PageSerializer

    def get_queryset(self):
        from apps.core.utils import can_access_drafts
        if can_access_drafts(self.request):
            return Page.objects.all()
        return Page.objects.public()


class HomePageView(APIView):
    """
    Returns the ordered, enabled sections for the homepage.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Homepage Composition", responses={200: dict})
    def get(self, request):
        home_page = Page.objects.filter(slug="home").first()
        if not home_page:
            # Fallback homepage definition
            return Response({
                "page": "home",
                "title": "SKAD GROUP | Building Businesses. Creating Brands. Shaping the Future.",
                "headline": "BUILDING BUSINESSES. CREATING BRANDS. SHAPING THE FUTURE.",
                "philosophy": "BUILD • CONNECT • SCALE",
                "sections": [],
            })
        serializer = PageSerializer(home_page)
        return Response(serializer.data)

class NavigationView(APIView):
    """
    Dynamic navigation tree for Header, Mega Menus, and Footer.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Navigation Tree", responses={200: dict})
    def get(self, request):
        show_all = bool(request.user and request.user.is_authenticated and request.user.is_staff)
        companies = Company.objects.all() if show_all else Company.objects.public()
        brands = Brand.objects.all() if show_all else Brand.objects.public()
        platforms = Platform.objects.all() if show_all else Platform.objects.public()

        return Response({
            "primary_nav": [
                {"label": "Group", "href": "/about"},
                {
                    "label": "Companies",
                    "href": "/companies",
                    "children": [{"label": c.name, "href": f"/companies/{c.slug}"} for c in companies]
                },
                {
                    "label": "Brands",
                    "href": "/brands",
                    "children": [{"label": b.name, "href": f"/brands/{b.slug}", "category": b.category} for b in brands]
                },
                {
                    "label": "Platforms & Ventures",
                    "href": "/platforms",
                    "children": [{"label": p.name, "href": f"/platforms/{p.slug}"} for p in platforms]
                },
                {"label": "Capabilities", "href": "/capabilities"},
                {"label": "Impact", "href": "/impact"},
                {"label": "Insights", "href": "/insights"},
                {"label": "People", "href": "/people"},
                {"label": "Partners", "href": "/partners"},
                {"label": "Contact", "href": "/contact"},
            ],
            "primary_cta": {
                "label": "PARTNER WITH SKAD",
                "href": "/partner-with-skad",
            },
            "footer": {
                "columns": [
                    {"title": "Ecosystem", "links": [{"label": "Companies", "href": "/companies"}, {"label": "Brands", "href": "/brands"}, {"label": "Platforms", "href": "/platforms"}]},
                    {"title": "Capabilities", "links": [{"label": "Overview", "href": "/capabilities"}, {"label": "Industries", "href": "/industries"}, {"label": "Global Markets", "href": "/markets"}]},
                    {"title": "Corporate", "links": [{"label": "Leadership", "href": "/people"}, {"label": "Impact Foundation", "href": "/impact"}, {"label": "Careers", "href": "/careers"}]},
                    {"title": "Legal", "links": [{"label": "Privacy Policy", "href": "/legal/privacy"}, {"label": "Terms of Use", "href": "/legal/terms"}, {"label": "Cookie Policy", "href": "/legal/cookies"}]},
                ],
                "copyright": "© 2026 SKAD GROUP. All rights reserved.",
            }
        })

class ThemeTokensView(APIView):
    """
    Approved design system tokens per Page 10 & 16 of the specification.
    Allows administrators to edit tokens via Admin; falls back to canonical defaults.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Brand & Global Design Tokens", responses={200: dict})
    def get(self, request):
        palette = {
            "primary_navy": "#0A1F44",
            "deep_navy": "#07152F",
            "champagne_gold": "#D4AF37",
            "metallic_gold": "#B8862D",
            "white": "#FFFFFF",
            "warm_off_white": "#F8F7F3",
            "light_grey": "#F2F3F5",
        }
        typography = {
            "headline_font": "Cormorant Garamond, serif",
            "body_font": "Plus Jakarta Sans, sans-serif",
        }
        brand_themes = {
            "benavi": {"primary_accent": "#A8A9AD", "style": "Contemporary Fine Silver", "scope": "India only"},
            "detara": {"primary_accent": "#D4AF37", "style": "Luxury Fine Diamond", "scope": "International"},
            "luxora_glow": {"primary_accent": "#E8C5B8", "style": "Personal Beauty Studio", "scope": "Regional"},
            "zemo": {"primary_accent": "#1A1A1A", "style": "Custom Streetwear", "scope": "Regional"},
        }
        # Overlay any custom ThemeTokens configured in the Django Admin
        for token in ThemeToken.objects.all():
            if token.group == "palette":
                palette[token.key.replace("palette.", "")] = token.value
            elif token.group == "typography":
                typography[token.key.replace("typography.", "")] = token.value

        return Response({
            "palette": palette,
            "typography": typography,
            "brand_themes": brand_themes,
        })

class FeatureFlagsView(APIView):
    """
    Feature flag switches per Page 14 of the specification.
    Controls visibility of modular components: markets_map, people, newsroom, careers, etc.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Modular Feature Flags", responses={200: dict})
    def get(self, request):
        flags = FeatureFlag.objects.all()
        data = {f.key: f.enabled for f in flags}
        # Canonical default flags if not yet seeded/customized
        defaults = {
            "markets_map": True,
            "people": True,
            "newsroom": True,
            "careers": True,
            "search": True,
            "newsletter": True,
            "investment_route": False,  # Investment route inactive by default per spec
            "ask_skad": False,          # Future AI feature
        }
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return Response(data)

class UIStringsView(APIView):
    """
    Microcopy key/value pairs for frontend localization and instant CMS editing.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Microcopy UI Strings", responses={200: dict})
    def get(self, request):
        strings = UIString.objects.all()
        data = {s.key: s.value for s in strings}
        # Provide sensible defaults if not yet customized
        if "cta.partner_with_skad" not in data:
            data["cta.partner_with_skad"] = "PARTNER WITH SKAD"
        if "cta.explore_group" not in data:
            data["cta.explore_group"] = "EXPLORE THE GROUP"
        if "form.submit" not in data:
            data["form.submit"] = "Submit Enquiry"
        return Response(data)

class SiteSettingsView(APIView):
    """
    Global site identity and corporate contact details.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Global Site Settings", responses={200: dict})
    def get(self, request):
        settings_obj = SiteSettings.objects.first()
        if not settings_obj:
            settings_obj = SiteSettings.objects.create()
        serializer = SiteSettingsSerializer(settings_obj)
        return Response(serializer.data)

from rest_framework import serializers

class RevalidateRequestSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)

class InternalRevalidateHookView(APIView):
    """
    HMAC-signed internal webhook for triggering cache revalidations.
    Per page 11 & 20 of SKAD Backend Specification.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Internal Revalidation Webhook",
        request=RevalidateRequestSerializer,
        responses={200: dict, 403: dict},
    )
    def post(self, request):
        import time
        import hmac
        import hashlib
        from django.conf import settings
        from apps.core.tasks import trigger_revalidation_sync

        signature = request.headers.get("x-skad-signature", "")
        timestamp = request.headers.get("x-skad-timestamp")
        secret = getattr(settings, "REVALIDATE_SECRET", "")

        if not secret:
            return Response({"error": "Revalidation secret not configured."}, status=500)

        # Anti-replay attack check: ensure timestamp is within 300s window if provided
        if timestamp:
            try:
                if abs(time.time() - float(timestamp)) > 300:
                    return Response({"error": "Request timestamp has expired (replay defense)."}, status=403)
            except (ValueError, TypeError):
                return Response({"error": "Invalid timestamp format."}, status=400)

        body = request.body
        expected_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return Response({"error": "Invalid HMAC signature."}, status=403)

        tags = request.data.get("tags", ["sitemap", "navigation"])
        success = trigger_revalidation_sync(tags)
        return Response({"revalidated": success, "tags": tags})

