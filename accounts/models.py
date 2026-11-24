from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
import uuid
from django.utils import timezone


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        CUSTOMER = "customer", _("Customer")
        COURIER = "courier", _("Courier")
        ADMIN = "admin", _("Admin")
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    phone = models.CharField(max_length=20,unique=True,)
    full_name = models.CharField(max_length=255,blank=True,)
    role = models.CharField(max_length=20,choices=Role.choices,default=Role.CUSTOMER,)
    is_phone_verified = models.BooleanField(default=False,)
    is_active = models.BooleanField(default=True,)
    is_staff = models.BooleanField(default=False,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,)
    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone}-{self.full_name}"

class SMSLog(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        REJECTED = "rejected", "Rejected"
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    phone = models.CharField(max_length=20)
    request_id = models.CharField(max_length=100,unique=True,null=True,blank=True)
    message_id = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    provider_status = models.CharField(max_length=50,null=True,blank=True)
    sms_count = models.PositiveIntegerField(default=0)
    callback_data = models.JSONField(null=True,blank=True)
    verification = models.ForeignKey("accounts.OTPVerification",on_delete=models.SET_NULL,null=True,blank=True,related_name="sms_logs")
    error_message = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["phone", "created_at"]),models.Index(fields=["status"]),]

    def __str__(self):
        return f"{self.phone} - {self.status}"


class OTPVerification(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        EXPIRED = "expired", "Expired"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    phone = models.CharField(max_length=20)
    otp_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.phone} - {self.status}"