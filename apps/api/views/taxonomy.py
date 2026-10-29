from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.taxonomy.models import Industry, Capability, Market, MarketStatus
from apps.api.serializers.taxonomy import IndustrySerializer, CapabilitySerializer, MarketSerializer
from apps.core.utils import can_access_drafts

class IndustryViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = IndustrySerializer

    def get_queryset(self):
        return Industry.objects.all() if can_access_drafts(self.request) else Industry.objects.public()

class CapabilityViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = CapabilitySerializer
    filterset_fields = ["group"]

    def get_queryset(self):
        return Capability.objects.all() if can_access_drafts(self.request) else Capability.objects.public()

class MarketsGroupedView(APIView):
    """
    Returns global markets grouped strictly by verification status:
    active, served, target, future.
    Evidence note is never leaked.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Grouped Global Markets", responses={200: dict})
    def get(self, request):
        markets = Market.objects.all()
        return Response({
            "active_markets": MarketSerializer(markets.filter(status=MarketStatus.ACTIVE), many=True).data,
            "served_markets": MarketSerializer(markets.filter(status=MarketStatus.SERVED), many=True).data,
            "target_markets": MarketSerializer(markets.filter(status=MarketStatus.TARGET), many=True).data,
            "future_markets": MarketSerializer(markets.filter(status=MarketStatus.FUTURE), many=True).data,
        })
