""" add.users admin. """

from django.contrib import admin

from users.models import Buyers
from users.services import purchases_and_delivery


# Register your models here.


class BuyersAdmin(admin.ModelAdmin):
    """ Buyer. """
    model = Buyers
    fields = ('email', 'purchases_and_delivery')
    readonly_fields = ('email', 'purchases_and_delivery')

    def purchases_and_delivery(self, obj):
        """ For processing JSON fields. """
        return purchases_and_delivery(self)

    show_full_result_count = False


admin.site.register(Buyers, BuyersAdmin)
