from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('izipay/', include('izipay.urls')),
    path('shopify/', include('shopify.urls')),
    # Documentación de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Interfaces de la documentación
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
