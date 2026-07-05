"""
Django settings for VersusHub project.
A comparison website (cars, phones, foods, companies, anything vs anything)
built to be AdSense-friendly: fast, SEO-structured, content-rich.

Works unchanged for local development (SQLite, DEBUG on) and switches to
production mode automatically when deployed to a real host that sets
DATABASE_URL (Render, Railway, Heroku-likes all do this) -- see README's
"Deploying" section.
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't leave the fallback value below in place once this
# is public. Set a real SECRET_KEY as an environment variable on your host.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-CHANGE-THIS-BEFORE-DEPLOYING-xk29fj2938fj"
)

# Locally this defaults to True (unchanged behavior). On your host, set the
# environment variable DEBUG=False -- never run a public site with this on.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Priority: explicit ALLOWED_HOSTS env var, then Render's auto-injected
# hostname (secure zero-config default when deployed there), then a wide-open
# wildcard as a local-dev-only fallback.
_hosts_env = os.environ.get("ALLOWED_HOSTS", "")
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in _hosts_env.split(",") if h.strip()]
elif _render_host:
    ALLOWED_HOSTS = [_render_host]
else:
    ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "compare",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "versushub.urls"

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
                "compare.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "versushub.wsgi.application"

# Locally: SQLite, zero setup needed. On a real host: set DATABASE_URL and
# this switches to that automatically (Render/Railway set this for you the
# moment you attach a Postgres database -- you don't type it in yourself).
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
# Note: no STATICFILES_DIRS needed — app-level static files in compare/static/
# are found automatically by Django's AppDirectoriesFinder.

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Only matters once DEBUG=False (i.e. once you're actually deployed)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- AdSense config (set these once Google approves your site) ---
ADSENSE_CLIENT_ID = os.environ.get("ADSENSE_CLIENT_ID", "ca-pub-XXXXXXXXXXXXXXXX")
ADSENSE_ENABLED = os.environ.get("ADSENSE_ENABLED", "False") == "True"
