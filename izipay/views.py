from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render
import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime
from .models import IzipayConfig
from .serializers import (
    IzipayConfigSerializer,
    IzipayConfigPublicSerializer,
    ConnectivityTestSerializer,
    ConnectivityTestResponseSerializer,
    IzipayScriptSerializer
)

class IzipayConfigViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar configuraciones de Izipay"""
    queryset = IzipayConfig.objects.all()
    serializer_class = IzipayConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar serializador público para acciones de solo lectura"""
        if self.action in ['list', 'retrieve']:
            return IzipayConfigPublicSerializer
        return IzipayConfigSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active_config(self, request):
        """Obtener la configuración activa"""
        try:
            config = IzipayConfig.get_active_config()
            if not config:
                return Response(
                    {'error': 'No hay configuración activa'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = IzipayConfigPublicSerializer(config)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def script_info(self, request):
        """Obtener información del script de Izipay"""
        try:
            config = IzipayConfig.get_active_config()
            if not config:
                return Response(
                    {'error': 'No hay configuración activa'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            script_data = {
                'script_tag': config.get_script_tag(),
                'script_url': config.script_url,
                'environment': 'Sandbox' if config.is_sandbox else 'Producción',
                'merchant_code': config.merchant_code
            }
            
            serializer = IzipayScriptSerializer(script_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def test_connectivity(self, request):
        """Probar conectividad con Izipay"""
        serializer = ConnectivityTestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        test_type = serializer.validated_data.get('test_type', 'simple')
        config_id = serializer.validated_data.get('config_id')
        
        try:
            # Obtener configuración
            if config_id:
                try:
                    config = IzipayConfig.objects.get(id=config_id)
                except IzipayConfig.DoesNotExist:
                    return Response(
                        {'error': f'Configuración con ID {config_id} no encontrada'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                config = IzipayConfig.get_active_config()
                if not config:
                    return Response(
                        {'error': 'No hay configuración activa de Izipay'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            if test_type == 'simple':
                result = self._simple_connectivity_test(config)
            else:
                result = self._full_connectivity_test(config)
            
            result['test_type'] = test_type
            result['timestamp'] = datetime.now()
            
            response_serializer = ConnectivityTestResponseSerializer(result)
            return Response(response_serializer.data)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f'Error inesperado: {str(e)}',
                'test_type': test_type,
                'timestamp': datetime.now()
            }
            response_serializer = ConnectivityTestResponseSerializer(error_result)
            return Response(response_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _simple_connectivity_test(self, config):
        """Prueba simple de conectividad"""
        try:
            test_url = config.script_url
            response = requests.get(test_url, timeout=10)
            
            return {
                'success': True,
                'message': 'Conectividad básica exitosa con Izipay',
                'config_info': {
                    'merchant_code': config.merchant_code,
                    'environment': 'Sandbox' if config.is_sandbox else 'Producción',
                    'script_url': config.script_url,
                    'tested_url': test_url
                },
                'response_status': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}',
                'attempted_url': test_url if 'test_url' in locals() else 'URL no definida'
            }
    
    def _full_connectivity_test(self, config):
        """Prueba completa de conectividad con API"""
        try:
            # URLs corregidas para Izipay
            if config.is_sandbox:
                api_url = 'https://sandbox-checkout.izipay.pe/api-payment/V4/Charge/CreatePayment'
            else:
                api_url = 'https://checkout.izipay.pe/api-payment/V4/Charge/CreatePayment'
            
            # Datos de prueba
            test_data = {
                'amount': 100,
                'currency': 'PEN',
                'orderId': f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}'
            }
            
            # Crear firma HMAC
            payload = json.dumps(test_data, separators=(',', ':'))
            signature = hmac.new(
                config.hash_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {base64.b64encode(f"{config.merchant_code}:{config.api_key}".encode()).decode()}',
                'X-Hmac-Sha256': signature
            }
            
            # Realizar petición
            response = requests.post(api_url, json=test_data, headers=headers, timeout=30)
            
            return {
                'success': True,
                'message': f'Respuesta recibida de Izipay (Status: {response.status_code})',
                'config_info': {
                    'merchant_code': config.merchant_code,
                    'environment': 'Sandbox' if config.is_sandbox else 'Producción',
                    'script_url': config.script_url,
                    'api_url': api_url
                },
                'response_status': response.status_code,
                'response_preview': response.text[:200] + '...' if len(response.text) > 200 else response.text
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}',
                'attempted_url': api_url if 'api_url' in locals() else 'URL no definida'
            }

# Vista tradicional para la página HTML (opcional)
def connectivity_test_page(request):
    """Página HTML para probar la conectividad"""
    config = IzipayConfig.get_active_config()
    return render(request, 'izipay/test_connectivity.html', {
        'config': config
    })
