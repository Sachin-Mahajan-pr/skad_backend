from rest_framework import serializers
from apps.people.models import Person

class PersonSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)
    group_display = serializers.CharField(source="get_group_display", read_only=True)

    class Meta:
        model = Person
        fields = [
            "slug", "name", "title", "group", "group_display", "bio", "photo",
            "expertise", "linkedin_url", "company_name", "sort_order"
        ]
