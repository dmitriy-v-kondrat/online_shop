from django.urls import path

from cart.views import (CartDestroyProductView,
                        CartDetailAPI,
                        CartUpdateQuantityView,
                        ClearCartView,
                        PaymentDetailAPI,
                        PaymentView, RedirectToPayView,
                        )

urlpatterns = [
    path('detail/', CartDetailAPI.as_view(), name='cart'),
    path('update-cart/<int:pk>/', CartUpdateQuantityView.as_view(), name='update_cart'),
    path('destroy-cart/<int:pk>/', CartDestroyProductView.as_view(), name='destroy_cart'),
    path('clear-cart/', ClearCartView.as_view(), name='clear_cart'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment-detail/', PaymentDetailAPI.as_view()),
    path('redirect-to-pay/', RedirectToPayView.as_view(), name='redirect_to_pay'),
    ]