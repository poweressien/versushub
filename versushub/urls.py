from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from compare import views
from compare.sitemaps import ItemSitemap, ComparisonSitemap, CategorySitemap

sitemaps = {
    "items": ItemSitemap,
    "comparisons": ComparisonSitemap,
    "categories": CategorySitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("item/<slug:category_slug>/<slug:item_slug>/", views.item_detail, name="item_detail"),
    path("vs/<slug:category_slug>/<slug:slug_a>-vs-<slug:slug_b>/", views.compare_view, name="compare"),
    path("vs/<slug:category_slug>/<slug:slug_a>-vs-<slug:slug_b>/vote/<str:side>/", views.vote, name="vote"),
    path("category/<slug:category_slug>/pick/", views.pick_comparison, name="pick_comparison"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
