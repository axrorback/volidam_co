from django.urls import path
from .views import *

urlpatterns = [
    path("list/", address_list, name="address_list"),
    path("create/", address_create, name="address_create"),
    path("delete/<uuid:uuid>/", address_delete, name="address_delete"),
]