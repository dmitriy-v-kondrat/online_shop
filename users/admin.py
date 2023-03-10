from django.contrib import admin

from users.models import Buyers
from users.services import purchases_product


# Register your models here.


class BuyersAdmin(admin.ModelAdmin):
    model = Buyers
    fields = ('first_name', 'last_name', 'email', 'phone', 'country', 'get_purchase', 'get_address')
    readonly_fields = ('first_name', 'last_name', 'email', 'phone', 'country', 'get_purchase', 'get_address')

    def get_purchase(self, obj):
        return purchases_product(obj.purchases)

    def get_address(self, obj):
        get_address = f"Postal code: {obj.address['postal_code']}\n" \
                     f"Country: {obj.address['country']}\n" \
                     f"State: {obj.address['state']}\n" \
                     f"Locality: {obj.address['locality']}"
        return get_address



admin.site.register(Buyers, BuyersAdmin)
