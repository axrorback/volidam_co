from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from cart.models import Cart, CartItem
from catalog.models import Product
from addresses.models import Address
from dashboard.events import notify_admin_new_order

from .models import Order, OrderItem, Payment

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    cart_items = (
        cart.items
        .select_related("product")
        .all()
    )

    if not cart_items.exists():
        messages.warning(request, "Savatchangiz bo'sh.")
        return redirect("cart_detail")

    total_amount = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal("0.00")
    )

    addresses = Address.objects.filter(user=request.user)

    if not addresses.exists():
        messages.warning(
            request,
            "Buyurtma berish uchun avval manzil qo'shing."
        )
        return redirect("address_create")

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "cart_items": cart_items,
        "total_amount": total_amount,
        "addresses": addresses,
    })


@login_required
@require_POST
@transaction.atomic
def create_order(request):

    cart = get_object_or_404(
        Cart.objects.select_for_update(),
        user=request.user
    )

    cart_items = list(
        cart.items.select_related("product").all()
    )

    if not cart_items:
        messages.warning(request, "Savatchangiz bo'sh.")
        return redirect("cart_detail")

    address_id = request.POST.get("address")
    payment_method = request.POST.get("payment_method")
    note = request.POST.get("note", "").strip()

    # Foydalanuvchining o'z manzilini tekshiramiz
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    # To'lov usulini tekshiramiz
    allowed_methods = [
        Order.PaymentMethod.CASH,
        Order.PaymentMethod.CLICK,
    ]

    if payment_method not in allowed_methods:
        messages.error(request, "To'lov usuli noto'g'ri.")
        return redirect("checkout")

    product_ids = [item.product_id for item in cart_items]

    products = Product.objects.select_for_update().filter(
        id__in=product_ids
    )

    products_map = {
        product.id: product
        for product in products
    }

    total_amount = Decimal("0.00")
    order_items = []

    for cart_item in cart_items:

        product = products_map.get(cart_item.product_id)

        if (
            product is None
            or not product.is_active
            or cart_item.quantity > product.stock
        ):
            messages.error(
                request,
                f"{cart_item.product.name} mahsuloti "
                "omborda yetarli emas."
            )
            return redirect("cart_detail")

        unit_price = product.price
        item_total = unit_price * cart_item.quantity

        total_amount += item_total

        order_items.append({
            "product": product,
            "product_name": product.name,
            "unit_price": unit_price,
            "quantity": cart_item.quantity,
            "total_price": item_total,
        })

    order = Order.objects.create(
        user=request.user,
        address=address,
        payment_method=payment_method,
        payment_status=(
            Order.PaymentStatus.PENDING
            if payment_method == Order.PaymentMethod.CLICK
            else Order.PaymentStatus.UNPAID
        ),
        total_amount=total_amount,
        note=note,
    )

    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            product=item["product"],
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            total_price=item["total_price"],
        )
        for item in order_items
    ])

    for item in order_items:
        product = item["product"]
        product.stock -= item["quantity"]
        product.save()

    if payment_method == Order.PaymentMethod.CLICK:
        Payment.objects.create(
            order=order,
            provider=Payment.Provider.CLICK,
            amount=total_amount,
            status=Payment.Status.PENDING,
        )

    cart.items.all().delete()
    transaction.on_commit(lambda: notify_admin_new_order(order))
    messages.success(
        request,
        f"Buyurtmangiz yaratildi: {order.order_number}"
    )

    return redirect("order_detail", order_number=order.order_number)



@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "orders": orders,
    }
    return render(request, "orders/order_list.html", context)





@login_required
def order_detail(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "payments"
        ),
        order_number=order_number,
        user=request.user
    )

    return render(request, "orders/order_detail.html", {
        "order": order,
    })