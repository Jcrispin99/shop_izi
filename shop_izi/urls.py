from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('izipay/', include('izipay.urls')),
    path('shopify/', include('shopify.urls')),
]
