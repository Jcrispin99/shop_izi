from django.contrib import admin

from .models import ShopifyConfig

@admin.register(ShopifyConfig)
class ShopifyConfigAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'api_key', 'access_token', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('shop_name', 'api_key')
    fieldsets = (
        ('Store Information', {
            'fields': ('shop_name', 'is_active')
        }),
        ('Authentication (Choose one method)', {
            'fields': ('access_token', ('api_key', 'api_secret')),
            'description': 'Use either Access Token (recommended) OR API Key + Secret (legacy)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')
