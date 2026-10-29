from rest_framework import viewsets, generics, permissions, parsers
from apps.careers.models import Career, Application
from apps.api.serializers.careers import CareerSerializer, ApplicationCreateSerializer
from apps.core.utils import can_access_drafts

class CareerViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = CareerSerializer
    filterset_fields = ["department", "employment_type"]
    search_fields = ["title", "description", "location"]

    def get_queryset(self):
        if can_access_drafts(self.request):
            return Career.objects.all()
        return Career.objects.public()

class ApplicationCreateView(generics.CreateAPIView):
    """
    Submits a candidate job application with resume upload.
    CV files are safely stored in private storage.
    """
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = ApplicationCreateSerializer
