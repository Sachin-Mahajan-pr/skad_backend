from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.api.views.entities import (
    GroupViewSet, CompanyViewSet, BrandViewSet, PlatformViewSet,
    VentureViewSet, FoundationViewSet, EcosystemGraphView
)
from apps.api.views.pages import (
    PageViewSet, HomePageView, NavigationView,
    ThemeTokensView, FeatureFlagsView, UIStringsView, SiteSettingsView, InternalRevalidateHookView
)
from apps.api.views.content import (
    ArticleViewSet, NewsItemViewSet, PressReleaseViewSet,
    CaseStudyViewSet, ReportViewSet, EventViewSet, MediaAssetDetailView
)
from apps.api.views.taxonomy import IndustryViewSet, CapabilityViewSet, MarketsGroupedView
from apps.api.views.people import PersonViewSet
from apps.api.views.careers import CareerViewSet, ApplicationCreateView
from apps.api.views.documents import DocumentViewSet, DocumentDownloadView, PrivateFileDownloadView
from apps.api.views.partners import PartnerViewSet, FoundationInitiativeViewSet
from apps.api.views.enquiries import (
    EnquiryCreateView, EnquiryRoutesListView,
    OpportunityCreateView, SubscriptionCreateView, SubscriptionConfirmView
)
from apps.api.views.seo import SitemapView, RedirectsView, StructuredDataView
from apps.api.views.search import CrossEntitySearchView
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

class HealthCheckView(APIView):
    @extend_schema(summary="Service Health Status", responses={200: dict})
    def get(self, request):
        return Response({
            "status": "online",
            "platform": "SKAD GROUP Corporate API",
            "version": "1.0.0",
            "philosophy": "BUILD • CONNECT • SCALE",
        })

router = DefaultRouter()
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"platforms", PlatformViewSet, basename="platform")
router.register(r"ventures", VentureViewSet, basename="venture")
router.register(r"foundation/initiatives", FoundationInitiativeViewSet, basename="foundation-initiative")
router.register(r"foundation", FoundationViewSet, basename="foundation")

router.register(r"pages", PageViewSet, basename="page")
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"news", NewsItemViewSet, basename="news")
router.register(r"press-releases", PressReleaseViewSet, basename="press-release")
router.register(r"case-studies", CaseStudyViewSet, basename="case-study")
router.register(r"reports", ReportViewSet, basename="report")
router.register(r"events", EventViewSet, basename="event")

router.register(r"industries", IndustryViewSet, basename="industry")
router.register(r"capabilities", CapabilityViewSet, basename="capability")
router.register(r"people", PersonViewSet, basename="person")
router.register(r"careers", CareerViewSet, basename="career")
router.register(r"partners", PartnerViewSet, basename="partner")
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = [
    # Core health & status
    path("health/", HealthCheckView.as_view(), name="health-check"),

    # Dynamic Pages & Composition
    path("pages/home/", HomePageView.as_view(), name="page-home"),
    path("navigation/", NavigationView.as_view(), name="navigation"),
    path("site-settings/", SiteSettingsView.as_view(), name="site-settings"),
    path("theme/", ThemeTokensView.as_view(), name="theme-tokens"),
    path("feature-flags/", FeatureFlagsView.as_view(), name="feature-flags"),
    path("ui-strings/", UIStringsView.as_view(), name="ui-strings"),
    path("media/<int:pk>/", MediaAssetDetailView.as_view(), name="media-detail"),

    # Visual Ecosystem
    path("ecosystem/", EcosystemGraphView.as_view(), name="ecosystem-graph"),

    # Grouped Markets
    path("markets/", MarketsGroupedView.as_view(), name="markets-grouped"),

    # Inquiries & Routing
    path("enquiries/routes/", EnquiryRoutesListView.as_view(), name="enquiry-routes"),
    path("enquiries/", EnquiryCreateView.as_view(), name="enquiry-create"),
    path("opportunities/", OpportunityCreateView.as_view(), name="opportunity-create"),
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
    path("subscriptions/", SubscriptionCreateView.as_view(), name="subscription-create"),
    path("subscriptions/confirm/", SubscriptionConfirmView.as_view(), name="subscription-confirm"),

    # Tracked Document Download & Private File Downloads
    path("documents/<int:pk>/download/", DocumentDownloadView.as_view(), name="document-download"),
    path("private-download/", PrivateFileDownloadView.as_view(), name="private-download"),

    # Unified Search & SEO
    path("search/", CrossEntitySearchView.as_view(), name="cross-search"),
    path("seo/sitemap/", SitemapView.as_view(), name="seo-sitemap"),
    path("seo/redirects/", RedirectsView.as_view(), name="seo-redirects"),
    path("seo/structured-data/", StructuredDataView.as_view(), name="seo-structured-data"),

    # Cache Revalidation Webhook
    path("internal/revalidate-hook/", InternalRevalidateHookView.as_view(), name="internal-revalidate"),

    # Router endpoints
    path("", include(router.urls)),
]
