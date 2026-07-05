from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Avg


class Category(models.Model):
    """e.g. Cars, Smartphones, Foods, Companies"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Bootstrap icon class, e.g. 'bi-car-front'"
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})


class Spec(models.Model):
    """A comparable attribute within a category, e.g. 'Horsepower' for Cars."""
    category = models.ForeignKey(Category, related_name="specs", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=30, blank=True, help_text="e.g. 'hp', 'GB', 'kcal'")
    higher_is_better = models.BooleanField(
        default=True,
        help_text="Untick for specs where lower is better, e.g. price, weight"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Item(models.Model):
    """A single thing that can be compared, e.g. 'Toyota Camry 2025'."""
    category = models.ForeignKey(Category, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, blank=True)
    brand = models.CharField(max_length=80, blank=True, help_text="Maker/origin tag, used as a sidebar filter, e.g. 'Toyota' or 'Yoruba cuisine'")
    image_url = models.URLField(blank=True, help_text="Link to a product image")
    photo_credit = models.CharField(
        max_length=200, blank=True,
        help_text="Required for most Wikimedia Commons photos, e.g. 'Photo: Jane Doe / CC BY-SA 4.0'"
    )
    logo_url = models.URLField(blank=True, help_text="Link to the real brand/company logo, shown as a small badge")
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    score = models.PositiveSmallIntegerField(
        default=0,
        help_text="0-100 overall rating shown as a badge on the card, like a 'Versus score'"
    )
    pros = models.TextField(blank=True, help_text="One point per line")
    cons = models.TextField(blank=True, help_text="One point per line")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("category", "slug")
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("item_detail", kwargs={"category_slug": self.category.slug, "item_slug": self.slug})

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def pros_list(self):
        return [p.strip() for p in self.pros.splitlines() if p.strip()]

    @property
    def cons_list(self):
        return [c.strip() for c in self.cons.splitlines() if c.strip()]

    @property
    def initials(self):
        """Fallback avatar text when there's no photo — e.g. real people, where
        we deliberately don't show a photo (see seed_demo.py for why)."""
        words = self.name.split()
        letters = "".join(w[0] for w in words[:2] if w)
        return letters.upper() or "?"


class SpecValue(models.Model):
    """The value of one Spec for one Item."""
    item = models.ForeignKey(Item, related_name="spec_values", on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, related_name="values", on_delete=models.CASCADE)
    value_text = models.CharField(max_length=200, help_text="Display value, e.g. '200 hp' or 'Yes'")
    value_numeric = models.FloatField(
        null=True, blank=True,
        help_text="Optional numeric value used to auto-highlight the winner"
    )

    class Meta:
        unique_together = ("item", "spec")

    def __str__(self):
        return f"{self.item.name} / {self.spec.name}: {self.value_text}"


class Review(models.Model):
    """Simple user review/rating on an item — also great for repeat engagement + AdSense pageviews."""
    item = models.ForeignKey(Item, related_name="reviews", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    rating = models.PositiveSmallIntegerField(help_text="1 to 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.name} - {self.rating}/5 by {self.name}"


class Comparison(models.Model):
    """
    Records a specific head-to-head (A vs B) so it gets its own permanent,
    shareable, SEO-friendly URL and we can track which comparisons are popular.
    """
    category = models.ForeignKey(Category, related_name="comparisons", on_delete=models.CASCADE)
    item_a = models.ForeignKey(Item, related_name="comparisons_as_a", on_delete=models.CASCADE)
    item_b = models.ForeignKey(Item, related_name="comparisons_as_b", on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    votes_a = models.PositiveIntegerField(default=0)
    votes_b = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("item_a", "item_b")
        ordering = ["-views"]

    def __str__(self):
        return f"{self.item_a.name} vs {self.item_b.name}"

    def get_absolute_url(self):
        return reverse("compare", kwargs={
            "category_slug": self.category.slug,
            "slug_a": self.item_a.slug,
            "slug_b": self.item_b.slug,
        })

    @property
    def total_votes(self):
        return self.votes_a + self.votes_b

    @property
    def percent_a(self):
        return round((self.votes_a / self.total_votes) * 100) if self.total_votes else 50

    @property
    def percent_b(self):
        return 100 - self.percent_a if self.total_votes else 50
