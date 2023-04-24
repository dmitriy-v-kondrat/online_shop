""" add.users admin. """

from django.contrib import admin

from users.models import Buyer, BuyerPaymentPending
from users.services import product_naming, purchases_and_delivery


# Register your models here.


class BuyersAdmin(admin.ModelAdmin):
    """ Buyer. """
    model = Buyer
    fields = ('email', 'purchases_and_delivery')
    readonly_fields = ('email', 'purchases_and_delivery')

    def purchases_and_delivery(self, obj):
        """ For processing JSON fields. """
        return purchases_and_delivery(obj)

    show_full_result_count = False


class BuyerPaymentPendingAdmin(admin.ModelAdmin):
    model = BuyerPaymentPending
    list_display = ('created_at', 'payment_status')
    fields = ('payment_id', 'created_at',
              'payment_status',
              'first_name', 'last_name', 'email',
              'phone', 'postal_code',
              'country', 'state', 'locality', 'receive_newsletter',
              'detail_products'
              )
    readonly_fields = ('payment_id', 'created_at',
                       'payment_status',
                       'first_name', 'last_name', 'email',
                       'phone', 'postal_code',
                       'country', 'state', 'locality', 'receive_newsletter',
                       'detail_products'
                       )

    def detail_products(self, obj):
        return product_naming(obj.orders_pending)

    show_full_result_count = False


admin.site.register(Buyer, BuyersAdmin)
admin.site.register(BuyerPaymentPending, BuyerPaymentPendingAdmin)
