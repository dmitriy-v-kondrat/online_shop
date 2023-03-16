from django.contrib import admin

from users.models import Buyers
from users.services import purchases_and_delivery


# Register your models here.


class BuyersAdmin(admin.ModelAdmin):
    model = Buyers
    fields = ('email', 'get_purchases_and_delivery')
    readonly_fields = ('email', 'get_purchases_and_delivery')

    def get_purchases_and_delivery(self, obj):
        return purchases_and_delivery(obj)


admin.site.register(Buyers, BuyersAdmin)
