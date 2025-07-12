from django.contrib import admin

from .models import ShopifyConfig

@admin.register(ShopifyConfig)
class ShopifyConfigAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'api_key', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('shop_name',)
