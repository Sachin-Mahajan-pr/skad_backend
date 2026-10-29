from .base import *

DEBUG = False

# Host & CSRF configuration per Page 19
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "skadgroup.com,api.skadgroup.com").split(",")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://skadgroup.com")
CSRF_TRUSTED_ORIGINS = [FRONTEND_ORIGIN]

# Security headers from page 19 of SKAD Backend Spec
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN]

# Redis Cache for Production DRF Throttling & Aggregate Endpoints per Pages 3, 10, 13, 19
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "skad_prod",
    }
}

# Transactional Email Provider (SES, Postmark, SendGrid) per page 20 of SKAD Backend Spec
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1")

# Object Storage & CDN in Production per Page 3 & 20
if USE_S3 and AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
elif USE_S3 and AWS_STORAGE_BUCKET_NAME:
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

