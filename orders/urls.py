from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("list/", views.order_list, name="order_list"),
    path("create/", views.create_order, name="create_order"),
    path("<str:order_number>/",views.order_detail,name="order_detail"),
]