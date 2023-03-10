
from django.urls import path

from shop.views import ProductDetailView, ProductListView

urlpatterns = [
    path('', ProductListView.as_view(), name='shop'),
    path('detail-product/<slug:slug>/', ProductDetailView.as_view(), name='detail_product')
    ]
