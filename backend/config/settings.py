"""
Django settings for Developer DNA.

Reads all secrets from environment variables — never hardcoded.
Uses dj-database-url for DATABASE_URL parsing.
"""

import os
import logging
from pathlib import Path

import dj_database_url

logger = logging.getLogger(__name__)

# ─── Paths ───
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ───
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY environment variable is required")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS: list[str] = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
]

# ─── Application Definition ───
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local apps
    "telemetry",
    "events",
    "agents",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# ─── Database (PostgreSQL via DATABASE_URL) ───
DATABASES = {
    "default": dj_database_url.config(
        default="postgres://devdna:devdna_local_pass@localhost:5432/developerdna",
        conn_max_age=600,
    )
}

# ─── Auth ───
AUTH_USER_MODEL = "telemetry.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internationalization ───
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── Static Files ───
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─── Primary Key ───
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Django REST Framework ───
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
}

# ─── CORS ───
# Only allow the frontend origin — no wildcards in production
_frontend_url = os.environ.get("NEXT_PUBLIC_API_URL", "http://localhost:3000")
CORS_ALLOWED_ORIGINS = [_frontend_url]
CORS_ALLOW_CREDENTIALS = True

# ─── Kafka ───
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

KAFKA_PRODUCER_CONFIG: dict[str, object] = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "client.id": "devdna-backend",
    "enable.idempotence": True,
    "acks": "all",
}

KAFKA_CONSUMER_CONFIG: dict[str, object] = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "devdna-worker",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}

# All Kafka topics used by the platform
KAFKA_TOPICS: list[str] = [
    "code-events",
    "git-events",
    "terminal-events",
    "error-events",
    "session-events",
    "analysis-requests",
    "skill-insights",
    "weekly-reports",
    "anomaly-events",
]

# ─── AI / LLM ───
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Log which model backend is active at startup
if GEMINI_API_KEY:
    logger.info("🧠 AI backend: Gemini 2.5 Flash (API)")
else:
    logger.warning(
        "⚠️  GEMINI_API_KEY not set — will attempt Qwen3 1.7B offline fallback. "
        "Get a free key at https://aistudio.google.com/apikey"
    )

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.3

# Qwen3 fallback path — only used when GEMINI_API_KEY is absent
QWEN3_MODEL_PATH = os.environ.get(
    "QWEN3_MODEL_PATH",
    str(BASE_DIR / "models" / "qwen3-1.7b-q4_k_m.gguf"),
)

# ─── FAISS ───
FAISS_INDEX_DIR = str(BASE_DIR / "faiss_index")

# ─── Logging ───
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "events": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "agents": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
