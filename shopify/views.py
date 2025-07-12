from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ShopifyConfig
from .serializers import ShopifyConfigSerializer, ShopifyConfigPublicSerializer, ConnectivityTestSerializer, ConnectivityTestResponseSerializer

@method_decorator(csrf_exempt, name='dispatch')
class ShopifyConfigViewSet(viewsets.ModelViewSet):
    queryset = ShopifyConfig.objects.all()
    serializer_class = ShopifyConfigSerializer

    @action(detail=False, methods=['get'])
    def active_config(self, request):
        config = ShopifyConfig.get_active_config()
        if not config:
            return Response({'error': 'No active Shopify configuration found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShopifyConfigPublicSerializer(config)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def test_connectivity(self, request):
        serializer = ConnectivityTestSerializer(data=request.data)
        if serializer.is_valid():
            config_id = serializer.validated_data.get('config_id')
            if config_id:
                try:
                    config = ShopifyConfig.objects.get(pk=config_id)
                except ShopifyConfig.DoesNotExist:
                    return Response({'error': 'Configuration not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                config = ShopifyConfig.get_active_config()
                if not config:
                    return Response({'error': 'No active Shopify configuration found.'}, status=status.HTTP_404_NOT_FOUND)
            
            success, message = config.test_connection()
            response_serializer = ConnectivityTestResponseSerializer(data={'success': success, 'message': message})
            if response_serializer.is_valid():
                return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def test_specific_config(self, request, pk=None):
        try:
            config = self.get_object()
            success, message = config.test_connection()
            response_serializer = ConnectivityTestResponseSerializer(data={'success': success, 'message': message})
            if response_serializer.is_valid():
                return Response(response_serializer.data)
        except ShopifyConfig.DoesNotExist:
            return Response({'error': 'Configuration not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def test_connectivity_page(request):
    active_config = ShopifyConfig.get_active_config()
    return render(request, 'shopify/test_connectivity.html', {'config': active_config})


