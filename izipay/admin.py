from django.contrib import admin
from .models import IzipayConfig

@admin.register(IzipayConfig)
class IzipayConfigAdmin(admin.ModelAdmin):
    list_display = ['merchant_code', 'is_sandbox', 'is_active', 'created_at']
    list_filter = ['is_sandbox', 'is_active']
    fields = ['merchant_code', 'api_key', 'hash_key', 'public_key', 'is_sandbox', 'is_active']