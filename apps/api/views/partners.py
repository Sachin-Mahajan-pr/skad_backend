from rest_framework import viewsets, permissions
from apps.partners.models import Partner
from apps.foundation.models import FoundationInitiative
from apps.api.serializers.partners import PartnerSerializer, FoundationInitiativeSerializer
from apps.core.utils import can_access_drafts

class PartnerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = PartnerSerializer
    filterset_fields = ["partner_type"]
    search_fields = ["name", "relationship_description"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return Partner.objects.all()
        return Partner.objects.public()

class FoundationInitiativeViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = FoundationInitiativeSerializer
    filterset_fields = ["focus_area"]
    search_fields = ["title", "verified_impact_details"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return FoundationInitiative.objects.all()
        return FoundationInitiative.objects.public()
