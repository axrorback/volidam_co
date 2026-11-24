from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notify_admin_new_order(order):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "admin_orders",
        {
            "type": "order.created",
            "order": {
                "id": str(order.id),
                "order_number": order.order_number,
                "customer": order.user.full_name or order.user.phone,
                "total_amount": str(order.total_amount),
                "created_at": order.created_at.isoformat(),
            },
        },
    )