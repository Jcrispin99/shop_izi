from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopifyConfigViewSet, test_connectivity_page

router = DefaultRouter()
router.register(r'config', ShopifyConfigViewSet, basename='shopify-config')

urlpatterns = [
    path('api/', include(router.urls)),
    path('test/', test_connectivity_page, name='test_connectivity_page'),
]