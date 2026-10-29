import os
from django.http import FileResponse, Http404
from django.db.models import F
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.documents.models import Document, DocumentVersion
from apps.api.serializers.documents import DocumentSerializer

class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    serializer_class = DocumentSerializer
    filterset_fields = ["doc_type", "visibility"]
    search_fields = ["title"]

    def get_queryset(self):
        return Document.objects.filter(visibility="public")

class DocumentDownloadView(APIView):
    """
    Tracked download endpoint that increments download metrics and serves the document.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Tracked Document Download", responses={200: bytes})
    def get(self, request, pk):
        try:
            # Per Doc 1 Page 8: 'Only approved, current documents are returned.'
            if request.user and request.user.is_authenticated and request.user.is_staff:
                document = Document.objects.get(pk=pk)
            else:
                document = Document.objects.public().filter(visibility="public", pk=pk).first()
                if not document:
                    raise Http404("Document download not available.")

            version = document.current_version
            if not version or not version.file or not version.allow_download:
                raise Http404("Document download not available.")
            
            # Log / increment download metric
            DocumentVersion.objects.filter(pk=version.pk).update(download_count=F("download_count") + 1)
            
            # If S3 / MinIO presigned URL is available on storage, redirect per Page 8 & 10
            if hasattr(version.file.storage, "generate_presigned_url"):
                from django.http import HttpResponseRedirect
                signed_url = version.file.storage.generate_presigned_url(version.file.name, expires_in=300)
                return HttpResponseRedirect(signed_url)

            response = FileResponse(version.file.open("rb"), as_attachment=True)
            response["Content-Disposition"] = f'attachment; filename="{os.path.basename(version.file.name)}"'
            return response
        except Document.DoesNotExist:
            raise Http404("Document does not exist.")


class PrivateFileDownloadView(APIView):
    """
    Serves cryptographically signed private downloads (CVs, private attachments)
    when running on local storage or testing. Validates 300-second signature.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Signed Private File Download", responses={200: bytes})
    def get(self, request):
        from pathlib import Path
        from django.conf import settings
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

        token = request.query_params.get("token")
        if not token:
            raise Http404("Missing signature token.")
        secret = getattr(settings, "SECRET_KEY", "skad-private-storage-key")
        signer = TimestampSigner(key=secret, salt="skad-private-download")
        try:
            rel_path = signer.unsign(token, max_age=300)
        except (BadSignature, SignatureExpired):
            raise Http404("Download link has expired or is invalid.")

        root = Path(getattr(settings, "PRIVATE_MEDIA_ROOT", settings.BASE_DIR / "private_media"))
        file_path = (root / rel_path).resolve()

        # Prevent directory traversal attacks
        try:
            is_safe = file_path.is_relative_to(root.resolve())
        except AttributeError:
            is_safe = str(file_path).startswith(str(root.resolve()))

        if not is_safe or not file_path.exists():
            raise Http404("File not found.")

        response = FileResponse(open(file_path, "rb"), as_attachment=True)
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(rel_path)}"'
        return response

