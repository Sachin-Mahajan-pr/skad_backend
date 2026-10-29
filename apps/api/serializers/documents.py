from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.documents.models import Document, DocumentVersion

class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ["id", "version_label", "issued_on", "sha256", "allow_download"]

class DocumentSerializer(serializers.ModelSerializer):
    current_version = DocumentVersionSerializer(read_only=True)
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["id", "slug", "title", "doc_type", "doc_type_display", "visibility", "current_version", "download_url"]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_download_url(self, obj):
        if obj.current_version and obj.current_version.allow_download:
            return f"/api/v1/documents/{obj.id}/download/"
        return None
