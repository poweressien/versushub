from django.contrib import admin
from .models import Category, Spec, Item, SpecValue, Review, Comparison


class SpecValueInline(admin.TabularInline):
    model = SpecValue
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Spec)
class SpecAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "unit", "higher_is_better", "order")
    list_filter = ("category",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "score", "average_rating", "has_logo", "has_credit")
    list_filter = ("category", "brand")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SpecValueInline]

    @admin.display(boolean=True, description="Logo")
    def has_logo(self, obj):
        return bool(obj.logo_url)

    @admin.display(boolean=True, description="Credited")
    def has_credit(self, obj):
        return bool(obj.photo_credit) if obj.image_url else True


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("item", "name", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ("item_a", "item_b", "category", "views", "votes_a", "votes_b")
    ordering = ("-views",)
