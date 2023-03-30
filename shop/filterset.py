""" app.shop filter set. """

from django_filters.widgets import LinkWidget
from django import forms
from django.db.models import Q
from django_filters import rest_framework as filters
from mptt.forms import TreeNodeChoiceField
from shop.models import Category, Product


class ProductFilter(filters.FilterSet):
    """ Filter set for product. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['category'].field_class = TreeNodeChoiceField

    category = filters.ModelChoiceFilter(field_name='category',
                                         queryset=Category.objects.all(),
                                         widget=LinkWidget
                                         )
    brand = filters.AllValuesMultipleFilter(field_name='brand', widget=forms.CheckboxSelectMultiple())
    min_price = filters.NumberFilter(label='min price', method='get_min_price')
    max_price = filters.NumberFilter(label='max price', method='get_max_price')
    discount = filters.BooleanFilter(widget=forms.widgets.CheckboxInput(),
                                     field_name='discount',
                                     lookup_expr='gte',
                                     label='discount',
                                     )
    in_stock = filters.BooleanFilter(widget=forms.widgets.CheckboxInput(),
                                     field_name='in_stock',
                                     lookup_expr='gte',
                                     label='in stock',
                                     )

    def get_min_price(self, value):
        return self.queryset.filter(price__gte=value).exclude(new_price__lt=value)

    def get_max_price(self, value):
        return self.queryset.filter(Q(price__lte=value) | Q(new_price__lte=value))

    class Meta:
        model = Product
        fields = ('category', 'brand', 'min_price', 'max_price', 'discount', 'in_stock')
