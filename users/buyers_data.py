""" Service for operations with payments, rewriting products and buyers. """

import uuid
from typing import Dict, Tuple, TypeVar

from celery import chain, group
from django.conf import settings
from django.db.models import F
from rest_framework.exceptions import ValidationError
from yookassa import Configuration, Payment

from cart.cart import Cart
from cart.tasks import add_csv, add_mail, create_pdf
from shop.models import Product
from users.models import BuyerPaymentPending
from users.tasks import add_buyer_payment_pending, create_buyer, remove_buyer_payment_pending

Configuration.account_id = settings.CONFIGURATION_PAY['payment_account']
Configuration.secret_key = settings.CONFIGURATION_PAY['payment_key']


class ForBuyersBase(object):
    """ Base class. """

    def __init__(self, request):
        self.session = request.session
        self.cart = Cart(request)

    def data_payment(self):
        """ Data payment from model Payment. """
        return Payment.find_one(self.session.get('payment_id'))

    def cart_detail(self):
        """ Products detail from cart. """
        return [item for item in self.cart]


class DataForPayment(ForBuyersBase):
    """ Class for payment creation. """

    def __init__(self, request, buyer):
        super().__init__(request)
        self.buyer = buyer

    def pay_product(self) -> Dict:
        """ Create data for payment. """
        payments = self._create_payment()
        checkout_data = {"buyer": self.buyer,
                         "cart": self.cart_detail(),
                         "payment_value": payments.amount.value,
                         }
        return checkout_data

    def _create_payment(self) -> TypeVar:
        purchase_detail = self._check_product()
        to_payment = Payment.create({
            "amount": {
                "value": self.cart.get_total_price(),
                "currency": "RUB"
                },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/api/v1/cart/payment-detail/"
                },
            "metadata": purchase_detail,
            "capture": True,
            "description": f"{self.buyer['email']}, {self.buyer['first_name']}, {self.buyer['last_name']}",

            }, uuid.uuid4())
        self._update_session(to_payment)
        return to_payment

    def _check_product(self) -> Dict:
        purchase_detail = {}
        for product in self._get_products(keys=self.cart.cart.keys()):
            if product.quantity >= self.cart.cart[str(product.id)]['quantity']:
                purchase_detail[str(product.id)] = f"{product.name}, {self.cart.cart[str(product.id)]['quantity']}"
            else:
                raise ValidationError(detail=f"{product.name} left {product.quantity} pieces.")
        return purchase_detail

    def _get_products(self, keys):
        return Product.objects.filter(id__in=keys).only('id', 'name', 'quantity')

    def _update_session(self, payments: TypeVar) -> None:
        self.session.update({'payment_id': payments.id,
                             'buyer': self.buyer,
                             'to_pay': payments.confirmation.confirmation_url
                             })


class AddToBuyerPaymentPending(ForBuyersBase):
    """ Formation data payment and buyer for after write db. """

    def data_for_buyer_payment_pending(self) -> None:
        """ Data to create an instance of the BuyerPaymentPending model. """
        data_for_payment = self.data_payment()
        data_payment = {'payment_id': data_for_payment.id,
                        'orders_pending': data_for_payment.metadata,
                        'created_at': data_for_payment.created_at,
                        'payment_status': data_for_payment.status,
                        **self.session.get('buyer')
                        }
        add_buyer_payment_pending.s(data_payment=data_payment).apply_async()


class AddToBuyers(ForBuyersBase):
    """ For create model after succeeded pay. """

    def __init__(self, request):

        super().__init__(request)
        self.payment = self.data_payment()

    def check_payment(self):
        """ Check payment status. """
        if self.session.get('payment_id'):
            if self.payment.status == 'succeeded':
                if self.add_buyer_data() is True:
                    self.session.flush()
                    return 'succeeded'
            else:
                return 'not succeeded'
        else:
            return 'fail'

    def add_buyer_data(self) -> bool:
        """ We form data for sending for write and mailing."""
        dict_data_payment = self._read_data_payment_pending()
        total_price = self.payment.amount.value
        payment_id = dict_data_payment['payment_id']
        write_product = self._write_product_for(orders_products=dict_data_payment['orders_pending'])

        newsletter_status = dict_data_payment.pop('receive_newsletter')
        dict_data_payment['captured_at'] = self.payment.captured_at
        dict_data_payment['payment_status'] = self.payment.status

        if newsletter_status is True:
            data_payment_for_model = dict_data_payment.copy()
            create_buyer.s(data_payment_for_model=data_payment_for_model,
                           total_price=total_price
                           ).apply_async()

        dict_data_payment.pop('orders_pending')
        data_for_csv = {**write_product[0], **dict_data_payment}

        group(
                chain(add_csv.s(data_for_csv=data_for_csv),
                      remove_buyer_payment_pending.s(payment_id=payment_id)),
                chain(create_pdf.s(sales=write_product[1], payment=total_price, payment_id=payment_id),
                      add_mail.s(dict_data_payment=dict_data_payment))
                ).apply_async()

        return True

    def _write_product_for(self, orders_products: Dict) -> Tuple:
        """ Writing data for sending to CSV and PDF. """
        product_name = ''
        product_id = ''
        product_pieces = ''
        sales = []

        for pk in orders_products.keys():
            product_name += orders_products[pk].split(', ')[0] + '\n\n'
            product_pieces += orders_products[pk].split(', ')[1] + '\n\n'
            product_id += str(pk) + '\n\n'
            sales.append({"Product": orders_products[pk].split(', ')[0],
                          "pieces": orders_products[pk].split(', ')[1]
                          }
                         )
        self._update_product_quantity(orders_products=orders_products)
        dict_data_for_csv = {'product_name': product_name, 'product_id': product_id, 'product_pieces': product_pieces}
        return dict_data_for_csv, sales

    def _update_product_quantity(self, orders_products: Dict) -> None:
        """ Update product quantity in db after successful payment. """
        Product.objects.bulk_update(  # move in the Celery?
                [Product(id=int(pk),
                         quantity=F('quantity') - int(orders_products[pk].split(', ')[1]))
                 for pk in orders_products.keys()
                 ],
                ['quantity']
                )

    def _read_data_payment_pending(self) -> Dict:
        buyer = BuyerPaymentPending.objects \
            .filter(payment_id=self.payment.id) \
            .values('payment_id', 'created_at',
                    'payment_status', 'first_name',
                    'last_name', 'email',
                    'phone', 'orders_pending',
                    'postal_code', 'country',
                    'state', 'locality',
                    'receive_newsletter'
                    )
        return buyer[0]
