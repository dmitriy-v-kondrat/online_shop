""" app.shop admin. """

from django.contrib import admin
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from shop.models import Category, ImagesProduct, Product
from shop.services import new_price


# Register your models here.


class ImagesProductInline(admin.TabularInline):
    """ Inline model ImagesProduct. """
    model = ImagesProduct
    extra = 0
    fields = ('image', 'get_photo')
    readonly_fields = ('get_photo',)

    def get_photo(self, obj):
        """ For photo preview. """
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100">')
        return 'No photo'

    get_photo.short_description = 'preview'


class ImagesProductAdmin(admin.ModelAdmin):
    """ Images. """
    model = ImagesProduct
    show_full_result_count = False


class CategoryAdmin(DraggableMPTTAdmin):
    """ Category. """
    prepopulated_fields = {'slug': ('name',)}
    show_full_result_count = False


class ProductAdmin(admin.ModelAdmin):
    """ Product. """
    inlines = [ImagesProductInline]
    model = Product
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('views',)

    def save_model(self, request, obj, form, change):
        """ Change 'new_price' field. """
        if obj.discount > 0 and obj.new_price is None:
            obj.new_price = new_price(obj.price, obj.discount)
        obj.save()

    show_full_result_count = False


admin.site.register(ImagesProduct, ImagesProductAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(
        Category,
        CategoryAdmin,
        list_display=(
            'tree_actions',
            'indented_title',

            ),
        list_display_links=(
            'indented_title',
            ),
        )
