
from django.conf.urls.static import static
from . import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('users.urls')),
    path('', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('checkout/', include('order.urls')),
    path('', include('mpesa.urls')),
    path('paypal/', include('paypal_payment.urls')),
    path('paypal/', include("paypal.standard.ipn.urls")),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
