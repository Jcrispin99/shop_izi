from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para DRF
router = DefaultRouter()
router.register(r'config', views.IzipayConfigViewSet, basename='izipayconfig')

app_name = 'izipay'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Página HTML tradicional (opcional)
    path('test-page/', views.connectivity_test_page, name='test_page'),
]