from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.contrib import messages

from .models import Category, Item, Comparison, Spec, SpecValue


def home(request):
    categories = Category.objects.all()
    popular_comparisons = Comparison.objects.select_related(
        "item_a", "item_b", "category"
    ).order_by("-views")[:6]
    latest_items = Item.objects.select_related("category").order_by("-created_at")[:8]
    stats = {
        "categories": Category.objects.count(),
        "items": Item.objects.count(),
        "comparisons": Comparison.objects.count(),
    }
    return render(request, "compare/home.html", {
        "categories": categories,
        "popular_comparisons": popular_comparisons,
        "latest_items": latest_items,
        "stats": stats,
    })


def _top_spec_values(item, limit=3):
    """A few headline specs to show on a card, so lists don't feel bare."""
    return list(
        SpecValue.objects.filter(item=item).select_related("spec").order_by("spec__order")[:limit]
    )


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = category.items.all()

    selected_brands = request.GET.getlist("brand")
    if selected_brands:
        items = items.filter(brand__in=selected_brands)

    sort = request.GET.get("sort", "score")
    sort_map = {
        "score": "-score",
        "price_low": "price",
        "price_high": "-price",
        "name": "name",
    }
    items = items.order_by(sort_map.get(sort, "-score"))

    all_brands = category.items.exclude(brand="").values_list("brand", flat=True).distinct().order_by("brand")

    items_with_specs = [{"item": item, "top_specs": _top_spec_values(item)} for item in items]

    return render(request, "compare/category_detail.html", {
        "category": category,
        "items": items,
        "items_with_specs": items_with_specs,
        "all_brands": all_brands,
        "selected_brands": selected_brands,
        "sort": sort,
    })


def item_detail(request, category_slug, item_slug):
    item = get_object_or_404(Item, category__slug=category_slug, slug=item_slug)
    other_items = item.category.items.exclude(pk=item.pk)
    reviews = item.reviews.all()[:20]
    spec_values = SpecValue.objects.filter(item=item).select_related("spec").order_by("spec__order")
    return render(request, "compare/item_detail.html", {
        "item": item,
        "other_items": other_items,
        "reviews": reviews,
        "spec_values": spec_values,
    })


def pick_comparison(request, category_slug):
    """Picks two items (from POST form or GET ?a=&b= quick-link) and redirects to /vs/."""
    category = get_object_or_404(Category, slug=category_slug)
    a = request.POST.get("item_a") or request.GET.get("a")
    b = request.POST.get("item_b") or request.GET.get("b")
    if not a or not b or a == b:
        messages.error(request, "Please choose two different items to compare.")
        return redirect("category_detail", slug=category_slug)
    item_a = get_object_or_404(Item, pk=a, category=category)
    item_b = get_object_or_404(Item, pk=b, category=category)
    slug_a, slug_b = sorted([item_a.slug, item_b.slug])
    return redirect("compare", category_slug=category_slug, slug_a=slug_a, slug_b=slug_b)


def compare_view(request, category_slug, slug_a, slug_b):
    category = get_object_or_404(Category, slug=category_slug)
    item_a = get_object_or_404(Item, category=category, slug=slug_a)
    item_b = get_object_or_404(Item, category=category, slug=slug_b)

    comparison, _ = Comparison.objects.get_or_create(
        category=category,
        item_a=item_a if item_a.id < item_b.id else item_b,
        item_b=item_b if item_a.id < item_b.id else item_a,
    )
    Comparison.objects.filter(pk=comparison.pk).update(views=F("views") + 1)
    comparison.refresh_from_db()

    specs = category.specs.all()
    rows = []
    a_wins, b_wins = 0, 0
    for spec in specs:
        val_a = SpecValue.objects.filter(item=item_a, spec=spec).first()
        val_b = SpecValue.objects.filter(item=item_b, spec=spec).first()
        winner = None
        if val_a and val_b and val_a.value_numeric is not None and val_b.value_numeric is not None:
            if val_a.value_numeric != val_b.value_numeric:
                if spec.higher_is_better:
                    winner = "a" if val_a.value_numeric > val_b.value_numeric else "b"
                else:
                    winner = "a" if val_a.value_numeric < val_b.value_numeric else "b"
                if winner == "a":
                    a_wins += 1
                else:
                    b_wins += 1
        rows.append({"spec": spec, "a": val_a, "b": val_b, "winner": winner})

    if a_wins > b_wins:
        overall_winner, overall_score = item_a, f"{a_wins}-{b_wins}"
    elif b_wins > a_wins:
        overall_winner, overall_score = item_b, f"{b_wins}-{a_wins}"
    else:
        overall_winner, overall_score = None, f"{a_wins}-{b_wins}"

    other_items = category.items.exclude(pk__in=[item_a.pk, item_b.pk])

    # so votes always line up with a/b as shown on THIS page, regardless of
    # which order they're stored in on the Comparison row
    if comparison.item_a_id == item_a.id:
        percent_a, percent_b = comparison.percent_a, comparison.percent_b
    else:
        percent_a, percent_b = comparison.percent_b, comparison.percent_a

    return render(request, "compare/compare.html", {
        "category": category,
        "item_a": item_a,
        "item_b": item_b,
        "rows": rows,
        "other_items": other_items,
        "overall_winner": overall_winner,
        "overall_score": overall_score,
        "comparison": comparison,
        "percent_a": percent_a,
        "percent_b": percent_b,
    })


def vote(request, category_slug, slug_a, slug_b, side):
    """Records a 'which one wins' community vote and redirects back to the duel."""
    category = get_object_or_404(Category, slug=category_slug)
    item_a = get_object_or_404(Item, category=category, slug=slug_a)
    item_b = get_object_or_404(Item, category=category, slug=slug_b)
    comparison, _ = Comparison.objects.get_or_create(
        category=category,
        item_a=item_a if item_a.id < item_b.id else item_b,
        item_b=item_b if item_a.id < item_b.id else item_a,
    )
    is_a_first_in_stored_pair = comparison.item_a_id == item_a.id
    if side == "a":
        field = "votes_a" if is_a_first_in_stored_pair else "votes_b"
    else:
        field = "votes_b" if is_a_first_in_stored_pair else "votes_a"
    Comparison.objects.filter(pk=comparison.pk).update(**{field: F(field) + 1})
    return redirect("compare", category_slug=category_slug, slug_a=slug_a, slug_b=slug_b)


def search(request):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        results = Item.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query)
        ).select_related("category")[:30]
    return render(request, "compare/search.html", {"query": query, "results": results})
