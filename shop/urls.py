""" app.shop urls. """
from django.urls import path

from shop.views import CategoryDetailView, CategoryListView, ProductDetailView, ProductListView

urlpatterns = [
    path('', ProductListView.as_view(), name='shop'),
    path('detail-product/<str:slug>/', ProductDetailView.as_view(), name='detail_product'),
    path('category/', CategoryListView.as_view(), name='category'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='detail_category')
    ]
