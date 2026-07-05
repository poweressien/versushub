"""
Django settings for VersusHub project.
A comparison website (cars, phones, foods, companies, anything vs anything)
built to be AdSense-friendly: fast, SEO-structured, content-rich.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: change this before going to production!
SECRET_KEY = "django-insecure-CHANGE-THIS-BEFORE-DEPLOYING-xk29fj2938fj"

# Set DEBUG = False in production
DEBUG = True

ALLOWED_HOSTS = ["*"]  # tighten this to your real domain(s) before deploying

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

# Default: SQLite for easy local setup. Swap for Postgres in production.
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
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Note: no STATICFILES_DIRS needed — app-level static files in compare/static/
# are found automatically by Django's AppDirectoriesFinder.

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- AdSense config (set these once Google approves your site) ---
ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX"  # replace with your real publisher ID
ADSENSE_ENABLED = False  # flip to True once you've been approved and have real slot IDs
