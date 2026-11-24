from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from .models import Cart, CartItem
from catalog.models import Product


@login_required
@transaction.atomic
def add_to_cart(request, product_id):

    if request.method != "POST":
        return redirect("catalog")

    product = get_object_or_404(
        Product.objects.select_for_update(),
        id=product_id,
        is_active=True
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1 or quantity > product.stock:
        messages.warning(request, "Tanlangan miqdor mavjud emas.")
        return redirect("product_detail", slug=product.slug)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity}
    )

    if not created:
        new_quantity = item.quantity + quantity

        if new_quantity > product.stock:
            messages.warning(
                request,
                "Omborda tanlangan miqdor yetarli emas."
            )
            return redirect("product_detail", slug=product.slug)

        item.quantity = new_quantity
        item.save(update_fields=["quantity", "updated_at"])

    messages.success(request, "Mahsulot savatchaga qo'shildi.")

    return redirect("cart_detail")


@login_required
def cart_detail(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = cart.items.select_related(
        "product",
        "product__category"
    )

    total = sum(item.total_price for item in items)

    return render(request, "cart/cart.html", {
        "cart": cart,
        "items": items,
        "total": total,
    })


@login_required
@transaction.atomic
def update_cart_item(request, item_id):

    if request.method == "POST":
        item = get_object_or_404(
            CartItem.objects.select_related("product"),
            id=item_id,
            cart__user=request.user
        )

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            item.delete()

        elif quantity <= item.product.stock:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])

        else:
            messages.warning(
                request,
                f"Omborda faqat {item.product.stock} ta mahsulot mavjud."
            )

    return redirect("cart_detail")


@login_required
def remove_from_cart(request, item_id):

    if request.method == "POST":
        CartItem.objects.filter(
            id=item_id,
            cart__user=request.user
        ).delete()

    return redirect("cart_detail")