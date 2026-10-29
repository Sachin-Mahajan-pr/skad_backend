from .base import *

# Staging Environment Configuration
# Per page 4 & 22 of Backend Specification:
# "Staging mirrors production, is password-protected, noindex and uses test credentials;
# never copy production personal data to staging without anonymisation."

DEBUG = False

# Staging Allowed Hosts
ALLOWED_HOSTS = os.getenv("STAGING_ALLOWED_HOSTS", "staging.skadgroup.com,localhost,127.0.0.1").split(",")

# Staging Security Headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# Prevent search engine indexing on staging
ROBOTS_NOINDEX = True

# CORS & CSRF
CORS_ALLOW_ALL_ORIGINS = False
STAGING_ORIGIN = os.getenv("STAGING_FRONTEND_ORIGIN", "https://staging.skadgroup.com")
CORS_ALLOWED_ORIGINS = [STAGING_ORIGIN]
CSRF_TRUSTED_ORIGINS = [STAGING_ORIGIN]

# Email Configuration for Staging
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1")

# Object Storage & CDN in Staging per Page 3 & 20
if USE_S3 and AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
elif USE_S3 and AWS_STORAGE_BUCKET_NAME:
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

