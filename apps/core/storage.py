import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.signing import TimestampSigner

# Try importing S3Boto3Storage if django-storages is installed
try:
    from storages.backends.s3boto3 import S3Boto3Storage
    HAS_STORAGES = True
except ImportError:
    S3Boto3Storage = object
    HAS_STORAGES = False


class PublicMediaStorage(S3Boto3Storage if HAS_STORAGES and getattr(settings, "USE_S3", False) else FileSystemStorage):
    """
    Public storage for media assets (company heroes, brand logos, articles).
    In S3: Uses AWS_STORAGE_BUCKET_NAME with public-read and optional CDN domain.
    In Local: Falls back to FileSystemStorage at settings.MEDIA_ROOT.
    """
    def __init__(self, *args, **kwargs):
        if HAS_STORAGES and getattr(settings, "USE_S3", False):
            kwargs.setdefault("bucket_name", getattr(settings, "AWS_STORAGE_BUCKET_NAME", "skad-public-media"))
            kwargs.setdefault("default_acl", "public-read")
            kwargs.setdefault("file_overwrite", False)
            kwargs.setdefault("querystring_auth", False)
            if getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None):
                kwargs.setdefault("custom_domain", settings.AWS_S3_CUSTOM_DOMAIN)
            super().__init__(*args, **kwargs)
        else:
            kwargs.setdefault("location", getattr(settings, "MEDIA_ROOT", None))
            kwargs.setdefault("base_url", getattr(settings, "MEDIA_URL", "/media/"))
            super().__init__(*args, **kwargs)   


class PrivateMediaStorage(S3Boto3Storage if HAS_STORAGES and getattr(settings, "USE_S3", False) else FileSystemStorage):
    """
    Private storage for sensitive uploads (CV resumes, enquiry attachments, confidential documents).
    Per pages 3, 8, 13, 19, 20 of SKAD Specification:
    - Dedicated private bucket: AWS_PRIVATE_STORAGE_BUCKET_NAME
    - Private ACL: No direct public access
    - Presigned URLs with 300-second (5 min) expiry
    In Local: Falls back to settings.PRIVATE_MEDIA_ROOT with cryptographically signed tokens.
    """
    def __init__(self, *args, **kwargs):
        if HAS_STORAGES and getattr(settings, "USE_S3", False):
            kwargs.setdefault(
                "bucket_name",
                getattr(settings, "AWS_PRIVATE_STORAGE_BUCKET_NAME", getattr(settings, "AWS_STORAGE_BUCKET_NAME", "skad-private-uploads"))
            )
            kwargs.setdefault("default_acl", "private")
            kwargs.setdefault("file_overwrite", False)
            kwargs.setdefault("custom_domain", None)
            kwargs.setdefault("querystring_auth", True)
            kwargs.setdefault("querystring_expire", 300)
            super().__init__(*args, **kwargs)
        else:
            kwargs.setdefault("location", getattr(settings, "PRIVATE_MEDIA_ROOT", settings.BASE_DIR / "private_media"))
            kwargs.setdefault("base_url", None)
            super().__init__(*args, **kwargs)

    def generate_presigned_url(self, name: str, expires_in: int = 300) -> str:
        """
        Generates a secure, time-limited presigned URL for private file download.
        """
        if HAS_STORAGES and getattr(settings, "USE_S3", False):
            # S3 presigned URL via boto3 client
            return self.connection.meta.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": self._normalize_name(self._clean_name(name))},
                ExpiresIn=expires_in,
            )
        else:
            # Local fallback: Generate cryptographic signed URL token
            secret = getattr(settings, "SECRET_KEY", "skad-private-storage-key")
            signer = TimestampSigner(key=secret, salt="skad-private-download")
            token = signer.sign(name)
            return f"/api/v1/private-download/?token={token}"


def get_public_storage():
    return PublicMediaStorage()


def get_private_storage():
    return PrivateMediaStorage()
