from django.contrib import admin
from django.urls import path , include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('panel/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('addresses/', include('addresses.urls')),
    path('cart/', include('cart.urls')),
    path('', include('catalog.urls')),
    path('orders/', include('orders.urls')),
    path('admin/', include('dashboard.urls')),
    path('courier/', include('couriers.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)