from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id, price, quantity):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity,
                                     'price': str(price)}
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def update_quantity(self, product_id, quantity):
        """Update quantity product in cart."""
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.cart[product_id]['products_price'] = \
                str(Decimal(self.cart[product_id]['price']) * self.cart[product_id]['quantity'])
            self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, pk):
        """
        Удаление товара из корзины.
        """
        product_id = str(pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids).only('name', 'id')
        for product in products:
            self.cart[str(product.id)]['product'] = product.name

        for item in self.cart.values():
            item['products_price'] = str(Decimal(item['price']) * item['quantity'])
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
