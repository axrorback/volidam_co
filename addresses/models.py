from django.db import models
import uuid
from accounts.models import CustomUser


class Address(models.Model):

    class AddressType(models.TextChoices):
        HOME = "home", "Uy"
        WORK = "work", "Ishxona"
        OTHER = "other", "Boshqa"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="addresses")
    title = models.CharField(max_length=100,help_text="Masalan: Uyim, Ishxonam")
    address_type = models.CharField(max_length=20,choices=AddressType.choices,default=AddressType.HOME)
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    mahalla = models.CharField(max_length=150, blank=True)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=50)
    apartment = models.CharField(max_length=50, blank=True)
    landmark = models.CharField(max_length=255,blank=True,help_text="Mo'ljal")
    latitude = models.DecimalField(max_digits=30,decimal_places=25,null=True,blank=True)
    longitude = models.DecimalField(max_digits=30,decimal_places=25,null=True,blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.street}, {self.house}"