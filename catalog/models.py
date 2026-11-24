import uuid
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/",blank=True,null=True)
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()

    class Meta:
        ordering = ["ordering", "name"]
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/",blank=True,null=True)
    price = models.DecimalField(max_digits=12,decimal_places=2)
    old_price = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    unit = models.CharField(max_length=30,default="dona",help_text="Masalan: dona, litr, quti")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.is_active and self.stock > 0