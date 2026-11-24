from django.urls import path
from . import views

app_name = "courier"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("orders/", views.order_list, name="orders"),
    path("orders/<str:order_number>/", views.order_detail, name="order_detail"),

    path(
        "orders/<str:order_number>/accept/",
        views.accept_order,
        name="accept_order",
    ),
    path(
        "orders/<str:order_number>/start/",
        views.start_delivery,
        name="start_delivery",
    ),
    path(
        "orders/<str:order_number>/complete/",
        views.complete_order,
        name="complete_order",
    ),
    path("history/", views.order_history, name="history"),
]
