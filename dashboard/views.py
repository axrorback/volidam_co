from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.models import CustomUser
from orders.models import Order
from delivery.models import OrderDelivery
from accounts.decorators import role_required

@role_required(CustomUser.Role.ADMIN)
def admin_dashboard(request):
    orders = (
        Order.objects.select_related("user", "address", "courier").order_by("-created_at")[:20])

    context = {
        "orders": orders,
        "total_orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
        "delivering_orders": Order.objects.filter(status=Order.Status.DELIVERING).count(),
        "completed_orders": Order.objects.filter(status=Order.Status.COMPLETED).count(),
        "total_couriers": CustomUser.objects.filter(role=CustomUser.Role.COURIER,is_active=True,).count(),
    }

    return render(request, "dashboard/home.html", context)


@role_required(CustomUser.Role.ADMIN)
def order_list(request):
    orders = (
        Order.objects
        .select_related("user", "address", "courier")
        .order_by("-created_at")
    )

    status = request.GET.get("status")

    if status:
        orders = orders.filter(status=status)

    return render(request, "dashboard/orders.html", {
        "orders": orders,
        "statuses": Order.Status.choices,
        "selected_status": status,
    })


@role_required(CustomUser.Role.ADMIN)
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "address",
            "courier",
        ).prefetch_related("items", "payments"),
        order_number=order_number,
    )

    couriers = CustomUser.objects.filter(
        role=CustomUser.Role.COURIER,
        is_active=True,
    ).order_by("full_name")

    delivery = (
        OrderDelivery.objects
        .filter(order=order)
        .select_related("courier")
        .order_by("-created_at")
        .first()
    )

    return render(request, "dashboard/order_detail.html", {
        "order": order,
        "courier": couriers,
        "delivery": delivery,
    })


@role_required(CustomUser.Role.ADMIN)
@require_POST
def assign_courier(request, order_number):

    courier_id = request.POST.get("courier")

    with transaction.atomic():

        order = get_object_or_404(
            Order.objects.select_for_update(),
            order_number=order_number,
        )

        courier = get_object_or_404(
            CustomUser,
            id=courier_id,
            role=CustomUser.Role.COURIER,
            is_active=True,
        )

        if order.status != Order.Status.PENDING:
            return redirect(
                "dashboard:order_detail",
                order_number=order.order_number,
            )

        if not order.address:
            return redirect(
                "dashboard:order_detail",
                order_number=order.order_number,
            )

        address = order.address

        delivery = OrderDelivery.objects.create(
            order=order,
            courier=courier,
            status=OrderDelivery.Status.ASSIGNED,

            delivery_region=address.region,
            delivery_district=address.district,
            delivery_mahalla=address.mahalla,
            delivery_street=address.street,
            delivery_house=address.house,
            delivery_apartment=address.apartment,
            delivery_landmark=address.landmark,

            delivery_latitude=address.latitude,
            delivery_longitude=address.longitude,

            assigned_at=timezone.now(),
        )

        order.courier = courier
        order.assigned_by = request.user
        order.assigned_at = timezone.now()
        order.status = Order.Status.CONFIRMED
        order.save()


    return redirect(
        "dashboard:order_detail",
        order_number=order.order_number,
    )


@role_required(CustomUser.Role.ADMIN)
def courier_list(request):
    couriers = CustomUser.objects.filter(
        role=CustomUser.Role.COURIER,
        is_active=True,
    ).order_by("full_name")

    return render(request, "dashboard/couriers.html", {
        "courier": couriers,
        "courier_count": couriers.count(),
    })