import uuid
import secrets

from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_order_number():
    return (
        f"VLD-{timezone.now():%Y%m%d}-"
        f"{secrets.token_hex(3).upper()}"
    )


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        CONFIRMED = "confirmed", "Tasdiqlandi"
        PROCESSING = "processing", "Tayyorlanmoqda"
        DELIVERING = "delivering", "Yetkazilmoqda"
        COMPLETED = "completed", "Yakunlandi"
        CANCELLED = "cancelled", "Bekor qilindi"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Naqd pul"
        CLICK = "click", "Click"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "To'lanmagan"
        PENDING = "pending", "To'lov kutilmoqda"
        PAID = "paid", "To'langan"
        FAILED = "failed", "Muvaffaqiyatsiz"
        REFUNDED = "refunded", "Qaytarilgan"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order_number = models.CharField(max_length=30,unique=True,default=generate_order_number,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="orders")
    address = models.ForeignKey("addresses.Address",on_delete=models.SET_NULL,null=True,blank=True,related_name="orders")
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    payment_method = models.CharField(max_length=20,choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=20,choices=PaymentStatus.choices,default=PaymentStatus.UNPAID)
    total_amount = models.DecimalField(max_digits=14,decimal_places=2,default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    courier = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name="delivery_orders",limit_choices_to={"role": "courier"},)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="assigned_orders",)
    assigned_at = models.DateTimeField(null=True,blank=True,)
    accepted_at = models.DateTimeField(null=True,blank=True,)
    delivered_at = models.DateTimeField(null=True,blank=True,)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey("catalog.Product",on_delete=models.PROTECT,related_name="order_items")
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12,decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=14,decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"



class Payment(models.Model):

    class Provider(models.TextChoices):
        CLICK = "click", "Click"

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        SUCCESS = "success", "Muvaffaqiyatli"
        FAILED = "failed", "Xatolik"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order = models.ForeignKey(Order,on_delete=models.PROTECT,related_name="payments")
    provider = models.CharField(max_length=20,choices=Provider.choices)
    amount = models.DecimalField(max_digits=14,decimal_places=2)
    provider_transaction_id = models.CharField(max_length=255,blank=True,db_index=True)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.provider}"