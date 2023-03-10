from decimal import Decimal


def new_price(price: int, discount: int) -> Decimal:
    """

    :param price:
    :param discount:
    :return:
    """
    return price * (1 - Decimal(discount) / 100)


def _quantity_product(product_quantity: int, quantity: int) -> bool:
    if 0 < product_quantity >= quantity:
        return True


def add_cart(cart, product, quantity):
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


def update_quantity_cart(cart, product_id, quantity):
    if quantity > 0:
        cart.update_quantity(product_id=product_id,
                             quantity=quantity
                             )

