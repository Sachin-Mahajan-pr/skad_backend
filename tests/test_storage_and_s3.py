import os
import io
from pathlib import Path
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner
from django.conf import settings
from rest_framework.test import APIClient

from apps.core.storage import PublicMediaStorage, PrivateMediaStorage, get_private_storage
from apps.core.utils import (
    random_resume_upload_path, random_enquiry_upload_path,
    random_document_upload_path, random_opportunity_upload_path
)
from apps.core.validators import validate_secure_file_upload, validate_secure_image
from apps.careers.models import Career, Application
from apps.documents.models import Document, DocumentVersion
from apps.enquiries.models import Enquiry, EnquiryRoute


class StorageAndUploadSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_randomized_upload_paths(self):
        """Verifies uploads receive randomized filenames per Page 13 & 19."""
        path1 = random_resume_upload_path(None, "my_real_cv.pdf")
        self.assertTrue(path1.startswith("private/resumes/"))
        self.assertTrue(path1.endswith(".pdf"))
        self.assertNotIn("my_real_cv", path1)

        path2 = random_enquiry_upload_path(None, "proposal.docx")
        self.assertTrue(path2.startswith("private/enquiries/"))
        self.assertTrue(path2.endswith(".docx"))
        self.assertNotIn("proposal", path2)

        path3 = random_document_upload_path(None, "policy.pdf")
        self.assertTrue(path3.startswith("documents/"))
        self.assertTrue(path3.endswith(".pdf"))
        self.assertNotIn("policy", path3)

    def test_private_storage_presigned_url_generation(self):
        """Verifies PrivateMediaStorage generates presigned / signed download URLs."""
        storage = PrivateMediaStorage()
        url = storage.generate_presigned_url("private/resumes/test_resume.pdf", expires_in=300)
        self.assertTrue(url.startswith("/api/v1/private-download/?token=") or "http" in url)

    def test_private_download_endpoint_with_valid_and_invalid_tokens(self):
        """Verifies /api/v1/private-download/ correctly validates signed tokens."""
        # Create a test file in private media directory
        private_root = Path(getattr(settings, "PRIVATE_MEDIA_ROOT", settings.BASE_DIR / "private_media"))
        test_dir = private_root / "private" / "test_docs"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / "sample.pdf"
        test_file.write_bytes(b"%PDF-1.4 test secure content")

        try:
            rel_path = "private/test_docs/sample.pdf"
            signer = TimestampSigner(key=settings.SECRET_KEY, salt="skad-private-download")
            valid_token = signer.sign(rel_path)

            # Valid token request
            res = self.client.get(f"/api/v1/private-download/?token={valid_token}")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(b"".join(res.streaming_content), b"%PDF-1.4 test secure content")

            # Tampered / Invalid token
            bad_res = self.client.get("/api/v1/private-download/?token=tampered-bad-token")
            self.assertEqual(bad_res.status_code, 404)

            # Missing token
            no_token_res = self.client.get("/api/v1/private-download/")
            self.assertEqual(no_token_res.status_code, 404)
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_file_magic_byte_validation(self):
        """Verifies that spoofed extensions with wrong magic bytes are rejected."""
        from django.core.exceptions import ValidationError
        fake_pdf = SimpleUploadedFile("cv.pdf", b"This is plain text not a pdf", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_secure_file_upload(fake_pdf)

        valid_pdf = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 header bytes and valid stream", content_type="application/pdf")
        # Should not raise
        validate_secure_file_upload(valid_pdf)

    def test_partner_pathways_mapping(self):
        """Verifies settings.PARTNER_PATHWAYS_MAPPING per Page 12."""
        mapping = getattr(settings, "PARTNER_PATHWAYS_MAPPING", {})
        self.assertIn("strategic_partner", mapping)
        self.assertIn("distributor", mapping)
        self.assertIn("technology_partner", mapping)
        self.assertEqual(mapping["distributor"], "international_trade")
        self.assertEqual(mapping["technology_partner"], "technology")

    def test_media_asset_model_and_endpoint(self):
        """Verifies MediaAsset creation and GET /media/{id}/ endpoint per Page 14, 16, 18."""
        from apps.content.models import MediaAsset
        asset = MediaAsset.objects.create(
            title="SKAD Group Header Banner",
            folder="general",
            alt_text="SKAD corporate architectural headquarters",
            focal_point="center",
            credit_licence="Copyright 2026 SKAD GROUP",
            width=1920,
            height=1080,
            derivatives={"webp": "/media/derivatives/banner.webp"},
        )
        res = self.client.get(f"/api/v1/media/{asset.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "SKAD Group Header Banner")
        self.assertEqual(res.data["folder"], "general")
        self.assertEqual(res.data["alt_text"], "SKAD corporate architectural headquarters")
