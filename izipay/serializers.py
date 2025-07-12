from rest_framework import serializers
from .models import IzipayConfig

class IzipayConfigSerializer(serializers.ModelSerializer):
    """Serializador para el modelo IzipayConfig"""
    
    class Meta:
        model = IzipayConfig
        fields = '__all__'
        extra_kwargs = {
            'api_key': {'write_only': True},
            'hash_key': {'write_only': True},
        }
    
    def validate(self, data):
        """Validación personalizada"""
        if data.get('is_active', False):
            # Verificar que no haya otra configuración activa
            existing_active = IzipayConfig.objects.filter(is_active=True)
            if self.instance:
                existing_active = existing_active.exclude(pk=self.instance.pk)
            
            if existing_active.exists():
                raise serializers.ValidationError(
                    "Solo puede haber una configuración activa a la vez."
                )
        
        return data

class IzipayConfigPublicSerializer(serializers.ModelSerializer):
    """Serializador público sin campos sensibles"""
    environment = serializers.SerializerMethodField()
    
    class Meta:
        model = IzipayConfig
        fields = ['id', 'merchant_code', 'script_url', 'is_sandbox', 'is_active', 'environment', 'created_at', 'updated_at']
    
    def get_environment(self, obj):
        return 'Sandbox' if obj.is_sandbox else 'Producción'

class ConnectivityTestSerializer(serializers.Serializer):
    """Serializador para las pruebas de conectividad"""
    test_type = serializers.ChoiceField(
        choices=[('simple', 'Simple'), ('full', 'Completa')],
        default='simple',
        help_text="Tipo de prueba a realizar"
    )
    config_id = serializers.IntegerField(
        required=False,
        help_text="ID de configuración específica (opcional, usa la activa por defecto)"
    )

class ConnectivityTestResponseSerializer(serializers.Serializer):
    """Serializador para la respuesta de pruebas de conectividad"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    config_info = serializers.DictField(required=False)
    response_status = serializers.IntegerField(required=False)
    response_preview = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    attempted_url = serializers.CharField(required=False)
    test_type = serializers.CharField()
    timestamp = serializers.DateTimeField()

class IzipayScriptSerializer(serializers.Serializer):
    """Serializador para obtener el script de Izipay"""
    script_tag = serializers.CharField(read_only=True)
    script_url = serializers.CharField(read_only=True)
    environment = serializers.CharField(read_only=True)
    merchant_code = serializers.CharField(read_only=True)