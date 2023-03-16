from django.contrib import admin

from users.models import Buyers
from users.services import get_purchase_delivery


# Register your models here.


class BuyersAdmin(admin.ModelAdmin):
    model = Buyers
    fields = ('email', 'get_purchase_delivery', 'get_address')
    readonly_fields = ('email', 'get_purchase_delivery', 'get_address')

    def get_purchase_delivery(self, obj):
        return get_purchase_delivery(obj.purchases)

    def get_address(self, obj):
        # print(obj.delivery_data)
        return obj.delivery_data



admin.site.register(Buyers, BuyersAdmin)
