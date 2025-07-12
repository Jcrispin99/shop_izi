from django.db import models
from django.core.validators import URLValidator

class IzipayConfig(models.Model):
    """
    Configuración básica para conectividad con Izipay
    Intermediario entre Izipay y Shopify
    """
    
    # Campos esenciales para la conectividad
    merchant_code = models.CharField(
        max_length=50, 
        verbose_name="Código de comercio",
        help_text="Código de comercio proporcionado por Izipay"
    )
    
    api_key = models.CharField(
        max_length=255, 
        verbose_name="Clave API",
        help_text="Clave API para autenticación con Izipay"
    )
    
    hash_key = models.CharField(
        max_length=255, 
        verbose_name="Clave Hash",
        help_text="Clave Hash para validación de integridad"
    )
    
    public_key = models.TextField(
        verbose_name="Clave Pública RSA",
        help_text="Clave pública RSA para encriptación"
    )
    
    # URL del script de Izipay - CAMPO CLAVE PARA SANDBOX/PRODUCCIÓN
    script_url = models.URLField(
        default="https://sandbox-checkout.izipay.pe/payments/v1/js/index.js",
        verbose_name="URL del Script Izipay",
        help_text="URL del script JavaScript de Izipay",
        validators=[URLValidator()]
    )
    
    # Control de entorno
    is_sandbox = models.BooleanField(
        default=True,
        verbose_name="Modo Sandbox",
        help_text="Activar para usar el entorno de pruebas"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Configuración Activa",
        help_text="Marcar como configuración activa para usar"
    )
    
    # Metadatos básicos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    class Meta:
        verbose_name = "Configuración Izipay"
        verbose_name_plural = "Configuraciones Izipay"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Izipay - {self.merchant_code} ({'Sandbox' if self.is_sandbox else 'Producción'})"
    
    @classmethod
    def get_active_config(cls):
        """
        Obtiene la configuración activa
        """
        return cls.objects.filter(is_active=True).first()
    
    def get_script_tag(self):
        """
        Retorna el tag script para incluir en templates
        """
        return f'<script src="{self.script_url}" defer></script>'
    
    def get_basic_config(self):
        """
        Retorna configuración básica para conectividad
        """
        return {
            'merchantCode': self.merchant_code,
            'isSandbox': self.is_sandbox,
            'scriptUrl': self.script_url,
            'keyRSA': self.public_key
        }
    
    def save(self, *args, **kwargs):
        """
        Auto-actualiza la URL del script según el entorno
        """
        if self.is_sandbox:
            self.script_url = "https://sandbox-checkout.izipay.pe/payments/v1/js/index.js"
        else:
            # URL de producción
            self.script_url = "https://checkout.izipay.pe/payments/v1/js/index.js"
        
        # Solo una configuración activa a la vez
        if self.is_active:
            IzipayConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    def test_connectivity(self):
        """
        Método para probar la conectividad básica con Izipay
        """
        return {
            'merchant_code': self.merchant_code,
            'script_url': self.script_url,
            'environment': 'sandbox' if self.is_sandbox else 'production',
            'status': 'ready_for_testing'
        }
