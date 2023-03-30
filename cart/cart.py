""" Cart. """
from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):
    """ Cart on the sessions."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id, price, quantity):
        """ Add product in to cart or update quantity. """
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity,
                                     'price': str(price)}
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def update_quantity(self, product_id, quantity):
        """ Replace product quantity and price in a cart. """
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.cart[product_id]['products_price'] = \
                str(Decimal(self.cart[product_id]['price']) * self.cart[product_id]['quantity'])
            self.save()

    def save(self):
        """ Update session. """
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, pk):
        """ Remove product from a cart. """
        product_id = str(pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """ Iterating through the items in the cart and getting the products from the db. """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).only('name', 'id')
        for product in products:
            self.cart[str(product.id)]['product'] = product.name

        for item in self.cart.values():
            item['products_price'] = str(Decimal(item['price']) * item['quantity'])
            yield item

    def __len__(self):
        """ All product in a cart. """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """ Total cost all products in a cart. """
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        """ Remove cart from a session. """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
