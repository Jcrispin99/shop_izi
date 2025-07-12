from django.db import models

class ShopifyConfig(models.Model):
    shop_name = models.CharField(max_length=255, unique=True, help_text="The name of the Shopify store (e.g., 'your-store.myshopify.com').")
    api_key = models.CharField(max_length=255, help_text="The API key for your Shopify custom app.")
    api_secret = models.CharField(max_length=255, help_text="The API secret key for your Shopify custom app.")
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
        return f"https://{self.api_key}:{self.api_secret}@{self.shop_name}/admin/api/2023-01/{endpoint}"

    def test_connection(self):
        import requests
        try:
            url = self.get_api_url('shop.json')
            response = requests.get(url)
            if response.status_code == 200:
                return True, "Connection successful!"
            else:
                return False, f"Connection failed. Status code: {response.status_code}, Response: {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"An error occurred: {e}"
