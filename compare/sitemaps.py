from django.contrib.sitemaps import Sitemap
from .models import Item, Comparison, Category


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()


class ItemSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Item.objects.all()


class ComparisonSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9  # comparison pages are your main SEO/AdSense moneymakers

    def items(self):
        return Comparison.objects.all()
