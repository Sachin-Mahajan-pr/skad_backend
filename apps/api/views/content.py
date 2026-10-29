from rest_framework import viewsets, permissions
from apps.content.models import Article, NewsItem, PressRelease, CaseStudy, Report, Event
from apps.api.serializers.content import (
    ArticleSerializer, NewsItemSerializer, PressReleaseSerializer,
    CaseStudySerializer, ReportSerializer, EventSerializer
)
from apps.core.utils import can_access_drafts

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = ArticleSerializer
    filterset_fields = ["category__slug"]
    search_fields = ["title", "excerpt", "body"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return Article.objects.all()
        return Article.objects.public()

class NewsItemViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = NewsItemSerializer
    filterset_fields = ["kind"]
    search_fields = ["title", "body"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return NewsItem.objects.all()
        return NewsItem.objects.public()

class PressReleaseViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = PressReleaseSerializer
    search_fields = ["title", "body", "location"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return PressRelease.objects.all()
        return PressRelease.objects.public()

class CaseStudyViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = CaseStudySerializer
    filterset_fields = ["company__slug", "brand__slug"]
    search_fields = ["title", "summary", "solution"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return CaseStudy.objects.all()
        return CaseStudy.objects.public()

class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = ReportSerializer
    filterset_fields = ["year", "is_public"]
    search_fields = ["title", "summary"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return Report.objects.all()
        return Report.objects.public().filter(is_public=True)

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer
    search_fields = ["title", "location", "description"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return Event.objects.all()
        return Event.objects.public()


from rest_framework import generics
from apps.content.models import MediaAsset
from apps.api.serializers.content import MediaAssetSerializer

class MediaAssetDetailView(generics.RetrieveAPIView):
    """
    Asset metadata and derivatives per Page 18:
    GET /media/{id}/
    """
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.AllowAny]
