import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-skad-group-platform-secret-2026")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
ALLOWED_HOSTS = [h.strip() for h in hosts.split(",") if h.strip()]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "simple_history",
    "storages",
]

LOCAL_APPS = [
    "apps.core",
    "apps.entities",
    "apps.taxonomy",
    "apps.people",
    "apps.content",
    "apps.careers",
    "apps.partners",
    "apps.documents",
    "apps.enquiries",
    "apps.foundation",
    "apps.seo",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "apps.core.middleware.AdminContentSecurityPolicyMiddleware",
]

# Staff Multi-Factor Authentication & Admin Rate Limiting / Lockout per Doc 1 Pages 3, 9, 19
try:
    import axes
    THIRD_PARTY_APPS.append("axes")
    MIDDLEWARE.append("axes.middleware.AxesMiddleware")
    AUTHENTICATION_BACKENDS = [
        "axes.backends.AxesStandaloneBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
    AXES_FAILURE_LIMIT = 5
    AXES_COOLOFF_TIME = 1  # 1 hour lockout after repeated failures
    AXES_RESET_ON_SUCCESS = True
except ImportError:
    pass

try:
    import django_otp
    THIRD_PARTY_APPS.extend([
        "django_otp",
        "django_otp.plugins.otp_totp",
    ])
    MIDDLEWARE.append("django_otp.middleware.OTPMiddleware")
except ImportError:
    pass

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database Configuration: PostgreSQL per specification with SQLite dev fallback
import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
elif DB_NAME and DB_USER:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD or "",
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "CONN_MAX_AGE": 600,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static & Media Files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
PRIVATE_MEDIA_ROOT = BASE_DIR / "private_media"

# Object Storage (S3-compatible & CDN) per Pages 3, 8, 13, 19, 20
USE_S3 = os.getenv("USE_S3", "False").lower() in ("true", "1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "skad-public-media")
AWS_PRIVATE_STORAGE_BUCKET_NAME = os.getenv("AWS_PRIVATE_STORAGE_BUCKET_NAME", "skad-private-uploads")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", None)  # e.g. http://minio:9000 for local MinIO
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", None)  # CDN domain (e.g. cdn.skadgroup.com)
AWS_DEFAULT_ACL = None  # Bucket owner enforced
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 300  # 5 minutes for signed private URLs

STORAGES = {
    "default": {
        "BACKEND": "apps.core.storage.PublicMediaStorage" if USE_S3 else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "private": {
        "BACKEND": "apps.core.storage.PrivateMediaStorage",
    },
}

# Partner pathways mapped to enquiry route codes per Page 12
PARTNER_PATHWAYS_MAPPING = {
    "strategic_partner": "business_partnership",
    "distributor": "international_trade",
    "technology_partner": "technology",
    "international_partner": "international_trade",
    "founder": "business_partnership",
    "business_opportunity": "business_partnership",
    "supplier": "supplier",
    "manufacturer": "manufacturing",
    "diamond_trading": "diamond_trading",
    "media": "media",
    "careers": "careers",
    "foundation": "foundation",
    "other": "general",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "apps.api.schema.SkadAutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "600/hour",
        "user": "2000/hour",
        "enquiry_ip": "5/hour",
        "enquiry_email": "3/day",
    },
}

# Redis Cache configuration per Doc 1 Pages 3, 10, 13, 19 (DRF throttling backed by Redis)
REDIS_URL = os.getenv("REDIS_URL", os.getenv("CELERY_BROKER_URL", None))
if REDIS_URL and "redis" in REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "KEY_PREFIX": "skad",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "skad-local-cache",
        }
    }

# drf-spectacular for OpenAPI & Swagger UI
SPECTACULAR_SETTINGS = {
    "TITLE": "SKAD GROUP Corporate REST API",
    "DESCRIPTION": (
        "Complete REST API for the SKAD GROUP corporate website ecosystem. "
        "Provides content delivery for Next.js, interactive ecosystem graph, "
        "enquiry routing, careers pipeline, governance documents, and SEO sitemaps."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True").lower() in ("true", "1")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN]

# Content & Business Rules
PRIVACY_POLICY_VERSION = os.getenv("PRIVACY_POLICY_VERSION", "2026.1")
REVALIDATE_SECRET = os.getenv("REVALIDATE_SECRET", "skad-revalidation-shared-secret-key-2026")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
TURNSTILE_ENABLED = os.getenv("TURNSTILE_ENABLED", "False").lower() in ("true", "1")

# Celery Beat Schedule for Data Retention per Doc 1 Page 13 & 19
CELERY_BEAT_SCHEDULE = {
    "prune-expired-candidate-applications-daily": {
        "task": "apps.careers.tasks.prune_expired_applications",
        "schedule": 86400.0,  # Run daily
    },
}

# Email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "SKAD GROUP <no-reply@skadgroup.com>")
