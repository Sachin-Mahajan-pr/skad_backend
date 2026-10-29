from rest_framework import viewsets, permissions
from apps.people.models import Person
from apps.api.serializers.people import PersonSerializer
from apps.core.utils import can_access_drafts

class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonSerializer
    filterset_fields = ["group"]
    search_fields = ["name", "title", "bio"]

    def get_queryset(self):
        # Only people with explicit recorded consent and approved verification can be returned
        if can_access_drafts(self.request):
            return Person.objects.filter(consent_recorded=True)
        return Person.objects.public().filter(consent_recorded=True)
