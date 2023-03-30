""" Services for app.cart.views. """
from typing import Dict

from cart.cart import Cart
from users.buyers_data import AddToBuyerPaymentPending, AddToBuyers, DataForPayment


def data_for_buyers(request, buyer: Dict) -> Dict:
    """ Takes data for create list a pay. """
    checkout_data = DataForPayment(request, buyer).pay_product()
    return checkout_data


def data_payment_pending(request) -> None:
    """ For writing data in a db. """
    AddToBuyerPaymentPending(request).data_for_buyer_payment_pending()


def payment_detail(request) -> str:
    """ For check payment. """
    str_response = AddToBuyers(request).check_payment()
    return str_response


def update_quantity_cart(request, product_id: str, quantity: int) -> None:
    """ Update product quantity in a cart. """
    cart = Cart(request)
    if quantity > 0:
        cart.update_quantity(product_id=product_id,
                             quantity=quantity
                             )
