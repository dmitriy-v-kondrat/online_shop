from rest_framework import serializers

from cart.cart import Cart
from users.models import BuyerPaymentPending


class AddToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(initial=1, min_value=1)

    class Meta:
        model = Cart
        fields = ('quantity',)


class CartUpdateQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(initial=1, min_value=1)

    class Meta:
        model = Cart
        fields = ('quantity',)


class PaymentSerializer(serializers.ModelSerializer):
    receive_newsletter = serializers.BooleanField(initial=True, help_text='receive newsletter new product and discount')

    class Meta:
        model = BuyerPaymentPending
        fields = ('first_name', 'last_name', 'email',
                  'phone', 'postal_code', 'country',
                  'state', 'locality', 'receive_newsletter'
                  )
