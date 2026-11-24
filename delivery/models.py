from django.db import models
import uuid
from orders.models import Order
from config import settings

class OrderDelivery(models.Model):

    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Biriktirilgan"
        ACCEPTED = "accepted", "Qabul qilingan"
        PICKED_UP = "picked_up", "Olib ketilgan"
        DELIVERING = "delivering", "Yetkazilmoqda"
        DELIVERED = "delivered", "Yetkazilgan"
        FAILED = "failed", "Yetkazilmadi"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    order = models.OneToOneField(Order,on_delete=models.PROTECT,related_name="delivery",)
    courier = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="deliveries",)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.ASSIGNED,)
    delivery_region = models.CharField(max_length=100)
    delivery_district = models.CharField(max_length=100)
    delivery_mahalla = models.CharField(max_length=150, blank=True)
    delivery_street = models.CharField(max_length=255)
    delivery_house = models.CharField(max_length=50)
    delivery_apartment = models.CharField(max_length=50, blank=True)
    delivery_landmark = models.CharField(max_length=255, blank=True)
    delivery_latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True,)
    delivery_longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True,)
    delivered_latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True,)
    delivered_longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True,)
    assigned_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.courier.phone}"



class CourierLocation(models.Model):
    courier = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="location",)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)