from django.conf import settings
from .models import Category


def site_settings(request):
    return {
        "ADSENSE_CLIENT_ID": getattr(settings, "ADSENSE_CLIENT_ID", ""),
        "ADSENSE_ENABLED": getattr(settings, "ADSENSE_ENABLED", False),
        "SITE_NAME": "VersusHub",
        "nav_categories": Category.objects.all(),
    }
