from django.db import models

class ShopifyConfig(models.Model):
    shop_name = models.CharField(max_length=255, unique=True, help_text="The name of the Shopify store (e.g., 'your-store.myshopify.com').")
    api_key = models.CharField(max_length=255, blank=True, help_text="The API key for your Shopify custom app (legacy).")
    api_secret = models.CharField(max_length=255, blank=True, help_text="The API secret key for your Shopify custom app (legacy).")
    access_token = models.CharField(max_length=255, blank=True, help_text="The Admin API access token for your Shopify app.")
    is_active = models.BooleanField(default=False, help_text="Is this the currently active configuration?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name

    class Meta:
        verbose_name = "Shopify Configuration"
        verbose_name_plural = "Shopify Configurations"

    @classmethod
    def get_active_config(cls):
        return cls.objects.filter(is_active=True).first()

    def get_api_url(self, endpoint):
        return f"https://{self.shop_name}/admin/api/2024-04/{endpoint}"

    def get_headers(self):
        if self.access_token:
            return {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
        else:
            # Fallback to basic auth for legacy configurations
            import base64
            credentials = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()
            return {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }

    def test_connection(self):
        import requests
        try:
            url = self.get_api_url('shop.json')
            headers = self.get_headers()
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
                return True, f"Connection successful! Connected to: {shop_name}"
            else:
                return False, f"Connection failed. Status code: {response.status_code}, Response: {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"An error occurred: {e}"
