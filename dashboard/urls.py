from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.admin_dashboard, name="home"),
    path("orders/", views.order_list, name="orders"),
    path("orders-detail/<str:order_number>/", views.order_detail, name="order_detail"),
    path("orders/<str:order_number>/assign/",views.assign_courier,name="assign_courier",),
    path("courier/", views.courier_list, name="courier"),
]