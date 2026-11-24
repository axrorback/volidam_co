from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from accounts.models import CustomUser
from orders.models import Order


@role_required(CustomUser.Role.COURIER)
def dashboard(request):
    courier = request.user

    active_orders = Order.objects.filter(
        courier=courier,
        status__in=[
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
            Order.Status.DELIVERING,
        ],
    )

    today = timezone.localdate()

    context = {
        "active_orders": active_orders.select_related(
            "user", "address"
        ).order_by("-created_at")[:5],

        "active_count": active_orders.count(),

        "today_count": Order.objects.filter(
            courier=courier,
            assigned_at__date=today,
        ).count(),

        "completed_count": Order.objects.filter(
            courier=courier,
            status=Order.Status.COMPLETED,
            delivered_at__date=today,
        ).count(),
    }

    return render(request, "courier/dashboard.html", context)


@role_required(CustomUser.Role.COURIER)
def order_list(request):
    orders = Order.objects.filter(
        courier=request.user,
        status__in=[
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
            Order.Status.DELIVERING,
        ],
    ).select_related(
        "user", "address"
    ).order_by("-created_at")

    return render(request, "courier/orders.html", {
        "orders": orders,
    })


@role_required(CustomUser.Role.COURIER)
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related(
            "user", "address", "courier"
        ).prefetch_related("items"),
        order_number=order_number,
        courier=request.user,
    )

    return render(request, "courier/order_detail.html", {
        "order": order,
    })


@role_required(CustomUser.Role.COURIER)
@require_POST
def accept_order(request, order_number):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            order_number=order_number,
            courier=request.user,
            status=Order.Status.CONFIRMED,
        )

        order.status = Order.Status.PROCESSING
        order.accepted_at = timezone.now()
        order.save(update_fields=["status", "accepted_at", "updated_at"])

    return redirect(
        "courier:order_detail",
        order_number=order.order_number,
    )


@role_required(CustomUser.Role.COURIER)
@require_POST
def start_delivery(request, order_number):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            order_number=order_number,
            courier=request.user,
            status=Order.Status.PROCESSING,
        )

        order.status = Order.Status.DELIVERING
        order.save(update_fields=["status", "updated_at"])

    return redirect(
        "courier:order_detail",
        order_number=order.order_number,
    )


@role_required(CustomUser.Role.COURIER)
@require_POST
def complete_order(request, order_number):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            order_number=order_number,
            courier=request.user,
            status=Order.Status.DELIVERING,
        )

        order.status = Order.Status.COMPLETED
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])

    return redirect("courier:dashboard")


@role_required(CustomUser.Role.COURIER)
def order_history(request):
    orders = Order.objects.filter(
        courier=request.user,
        status=Order.Status.COMPLETED,
    ).select_related(
        "user", "address"
    ).order_by("-delivered_at")

    return render(request, "courier/history.html", {
        "orders": orders,
    })
