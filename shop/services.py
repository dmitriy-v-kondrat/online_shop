""" app.shop services. """

from decimal import Decimal

from cart.cart import Cart


def new_price(price: int, discount: int) -> Decimal:
    """ Calculates the value for 'new_price' field. """
    return price * (1 - Decimal(discount) / 100)


def add_cart(request, product, quantity):
    """ Add to cart. """
    cart = Cart(request)
    if 0 < product.quantity >= quantity:
        product_id = str(product.id)
        if product.new_price is None:
            price = product.price
        else:
            price = product.new_price
        cart.add(product_id=product_id,
                 quantity=quantity,
                 price=price
                 )
    else:
        if product.quantity == 0:
            return 'not found'
        elif product.quantity < quantity:
            return 'many quantity'
