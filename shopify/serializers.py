from rest_framework import serializers
from .models import ShopifyConfig

class ShopifyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopifyConfig
        fields = '__all__'

class ShopifyConfigPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopifyConfig
        fields = ('id', 'shop_name', 'api_key', 'is_active')

class ConnectivityTestSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(required=False, help_text="ID of the configuration to test. If not provided, the active configuration will be used.")

class ConnectivityTestResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()