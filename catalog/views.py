from django.shortcuts import render, get_object_or_404

from .models import Category, Product


def catalog_list(request):
    categories = Category.objects.filter(is_active=True)

    products = Product.objects.filter(
        is_active=True,
        stock__gt=0
    ).select_related("category")

    category_slug = request.GET.get("category")

    if category_slug:
        products = products.filter(
            category__slug=category_slug
        )

    return render(request, "catalog/catalog.html", {
        "categories": categories,
        "products": products,
        "selected_category": category_slug,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock__gt=0
    ).exclude(id=product.id)[:8]

    return render(request, "catalog/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })